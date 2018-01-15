#!/usr/bin/env python

"""Automatic Steve Reich phasing music

Usage:
    ./phase.py test_input_files/ravi1.wav --n-tracks=24 --gap=.02 --fade=in-out --repeat-count=20 --end-align

"""

import os
import datetime
import argparse
import json

import sox


def fade_in_gains(n_tracks, quietest=-60.0):
    result = []
    chunk_size = -quietest / (n_tracks - 1)
    for i in range(n_tracks):
        this_chunk_size = chunk_size * i
        dB = quietest + this_chunk_size
        result.append(dB)
    return result


def fade_out_gains(n_tracks, quietest=-60.0):
    result = []
    chunk_size = -quietest / (n_tracks - 1)
    for i in reversed(range(n_tracks)):
        this_chunk_size = chunk_size * i
        dB = quietest + this_chunk_size
        result.append(dB)
    return result


def fade_in_out_gains(n_tracks, quietest=-60.0):
    half = n_tracks / 2
    ins = fade_in_gains(half, quietest=quietest)
    outs = fade_out_gains(half, quietest=quietest)
    if n_tracks % 2:
        ins.append(0.0)
    return ins + outs


def get_gain_dbs(fade_type, n_tracks, quietest=-60.0):
    if fade_type is None:
        return [0.0 for _ in range(n_tracks)]
    if fade_type == 'in':
        fade_function = fade_in_gains
    elif fade_type == 'out':
        fade_function = fade_out_gains
    elif fade_type == 'in-out':
        fade_function = fade_in_out_gains
    else:
        raise Exception('Allowed values for fade are None, "in", "out", and "in-out"')
    return fade_function(n_tracks, quietest=quietest)


class Sample(object):
    def __init__(self, file_name, start_pad_duration=0, end_pad_duration=0):
        self.file_name = file_name
        self.full_duration = sox.file_info.duration(file_name)
        self.start_pad_duration = start_pad_duration
        self.end_pad_duration = end_pad_duration


class Phase(object):
    def __init__(self,
            input_file,
            n_tracks=10,
            gap=0.02,
            initial_gap=0,
            repeat_count=10,
            end_align=False,
            start_pad_duration=0.0,
            end_pad_duration=0.0,
            temp_folder='tmp/',
            output_folder='output/',
            fade=None,
            quietest=-60.0,
            gain=0.0,
            trim_start=False,
            trim_end=False,
            solo_repetition_number=0,
            solo_track_number=0,
        ):

        self.args = {
            'input_file': input_file,
            'n_tracks': n_tracks,
            'gap': gap,
            'initial_gap': initial_gap,
            'repeat_count': repeat_count,
            'end_align': end_align,
            'start_pad_duration': start_pad_duration,
            'end_pad_duration': end_pad_duration,
            'temp_folder': temp_folder,
            'output_folder': output_folder,
            'fade': fade,
            'quietest': quietest,
            'gain': gain,
            'trim_start': trim_start,
            'trim_end': trim_end,
            'solo_repetition_number': solo_repetition_number,
            'solo_track_number': solo_track_number,
        }

        self.input_file = input_file
        self.n_tracks = n_tracks
        self.gap = gap
        self.initial_gap = initial_gap
        self.repeat_count = repeat_count
        self.end_align = end_align
        self.start_pad_duration = start_pad_duration
        self.end_pad_duration = end_pad_duration
        self.temp_folder = temp_folder
        self.output_folder = output_folder
        self.fade = fade
        self.quietest = quietest
        self.gain = gain
        self.trim_start = trim_start
        self.trim_end = trim_end
        self.solo_repetition_number = solo_repetition_number
        self.solo_track_number = solo_track_number

        self.gain_dbs = get_gain_dbs(fade, n_tracks, quietest=quietest)

        self.sample = Sample(
                input_file,
                start_pad_duration=start_pad_duration,
                end_pad_duration=end_pad_duration)

        if not os.path.exists(self.temp_folder):
            os.mkdir(self.temp_folder)

        self.output_file_name = self.build_output_file_name()
        self.output_wav_file_name = self.output_file_name + '.wav'

        self.write_args_json()

        print
        print self.output_file_name
        print

        self.phase()

    def write_args_json(self):
        self.output_json_file_name = self.output_file_name + '.json'

        args_json = json.dumps(
                self.args,
                sort_keys=True,
                indent=4,
                separators=(',', ': '))

        with open(self.output_json_file_name, 'w') as f:
            f.write(args_json)

    def make_track(self,
            temp_output_file,
            local_gap,
            local_repeat_count,
            has_initial_rest=False,
            mute_first=False,
            mute_last=False,
            gain_db=0.0):

        rest_duration = self.sample.full_duration + local_gap - self.sample.start_pad_duration - self.sample.end_pad_duration

        if mute_first or mute_last:
            local_repeat_count -= 1

        tfm = sox.Transformer()
        tfm.pad(end_duration=rest_duration)
        if local_repeat_count > 0:
            tfm.repeat(count=local_repeat_count)
        if has_initial_rest:
            tfm.pad(start_duration=rest_duration + ((self.sample.full_duration - rest_duration) / 2.0))

        # Soloing
        if mute_first:
            tfm.pad(start_duration=self.sample.full_duration + rest_duration)
        if mute_last:
            tfm.pad(end_duration=self.sample.full_duration + rest_duration)

        tfm.gain(gain_db=gain_db + self.gain)

        tfm.build(self.sample.file_name, temp_output_file)

    def checker_track(self,
            temp_output_file,
            local_gap,
            mute_first=False,
            mute_last=False,
            gain_db=0.0):
        """Repeat the sample on alternating tracks so the fade in and out can overlap"""

        track_a_file = self.temp_folder + 'track-a.wav'
        track_b_file = self.temp_folder + 'track-b.wav'

        half, remainder = divmod(self.repeat_count, 2)
        track_a_repeat_count = half + remainder - 1
        track_b_repeat_count = half - 1

        # Soloing
        mute_last_a = False
        mute_last_b = False
        if mute_last:
            if remainder:
                # There are an odd number of repeats, so the muted last repetition is in track A
                mute_last_a = True
            else:
                # There are an even number of repeats, so the muted last repetition is in track B
                mute_last_b = True

        self.make_track(
                track_a_file,
                local_gap,
                track_a_repeat_count,
                gain_db=gain_db,
                mute_first=mute_first,
                mute_last=mute_last_a)
        self.make_track(
                track_b_file,
                local_gap,
                track_b_repeat_count,
                gain_db=gain_db,
                mute_last=mute_last_b,
                has_initial_rest=True)

        cbn = sox.Combiner()
        cbn.build([track_a_file, track_b_file], temp_output_file, 'mix-power')

    def phase(self):
        track_file_names = []
        for i in range(self.n_tracks):
            track_file_name = self.temp_folder + 'track-{}.wav'.format(i)
            track_file_names.append(track_file_name)

            mute_first = False
            mute_last = False
            if i != self.solo_track_number:
                # Mute one of the repetitions in this track
                if self.solo_repetition_number == 0:
                    mute_first = True
                elif self.solo_repetition_number == self.repeat_count - 1:
                    mute_last = True
                # TODO: Support repetition numbers other than first and last

            gain_db = self.gain_dbs[i]

            self.checker_track(
                    track_file_name,
                    local_gap=self.gap * (i + 1),
                    mute_first=mute_first,
                    mute_last=mute_last,
                    gain_db=gain_db)

        if self.end_align:
            track_durations = [sox.file_info.duration(f) for f in track_file_names]
            longest_track_duration = max(track_durations)
            track_duration_diffs = [longest_track_duration - d for d in track_durations]
            new_track_file_names = []
            for i, diff, track_file_name in zip(range(1, self.n_tracks + 1), track_duration_diffs, track_file_names):
                new_track_file_name = track_file_name[:-4] + '-start-offset.wav'
                new_track_file_names.append(new_track_file_name)
                tfm = sox.Transformer()
                tfm.pad(start_duration=diff + (self.gap * i))
                tfm.build(track_file_name, new_track_file_name)
            track_file_names = new_track_file_names

        cbn = sox.Combiner()
        if self.trim_start:
            cbn.silence(location=1)  # Remove silence from the beginning
        if self.trim_end:
            cbn.silence(location=-1)  # Remove silence from the end
        cbn.build(track_file_names, self.output_wav_file_name, 'mix-power')

    def build_output_file_name(self):
        # clean input file name
        input_file_name = self.input_file.split('/')[-1]
        input_no_extension = ''.join(input_file_name.split('.')[:-1])

        # Make output folder for this input file
        output_folder = os.path.join(self.output_folder, input_no_extension)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Make file name for this run of phase.py
        timestamp = datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')

        output_file_name = '{}_{}'.format(input_no_extension, timestamp)

        output_file_name = os.path.join(output_folder, output_file_name)
        return output_file_name


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('input_file')

    parser.add_argument(
            '-n',
            '--n-tracks',
            help='how many tracks to generate',
            type=int,
            default=10)
    parser.add_argument(
            '-g',
            '--gap',
            help='the smallest gap between phrases',
            type=float,
            default=0.02)
    parser.add_argument(
            '-i',
            '--initial-gap',
            help='TODO: describe this better. Start (or end, if --end-align=True) this many repetitions off from alignment. A multiple of `gap`',
            type=int,
            default=0)
    parser.add_argument(
            '-r',
            '--repeat-count',
            help='the number of times the phrase should repeat',
            type=int,
            default=10)
    parser.add_argument(
            '-e',
            '--end-align',
            help='come together in the end, rather than starting out together',
            action='store_true',
            default=False)
    parser.add_argument(
            '-S',
            '--start-pad-duration',
            help='duration of silence at the beginning of the sample',
            type=float,
            default=0.0)
    parser.add_argument(
            '-E',
            '--end-pad-duration',
            help='duration of silence at the end of the sample',
            type=float,
            default=0.0)
    parser.add_argument(
            '-t',
            '--temp-folder',
            help='path of directory to put temporary files in',
            default='tmp/')
    parser.add_argument(
            '-o',
            '--output-folder',
            help='path of directory to put output',
            default='output/')
    parser.add_argument(
            '-f',
            '--fade',
            help='relative volumes of tracks: flat, fade in, fade out, or fade in then out',
            default=None,
            choices=[None, 'in', 'out', 'in-out'])
    parser.add_argument(
            '-q',
            '--quietest',
            help='The volume in dB of the quietest track(s) when fading',
            type=float,
            default=-60.0)
    parser.add_argument(
            '-G',
            '--gain',
            help='Raise or lower the over all volume in dB (or negative dB to lower)',
            type=float,
            default=0.0)
    parser.add_argument(
            '--trim-start',
            help='Remove silence from the beginning of the track',
            action='store_true',
            default=False)
    parser.add_argument(
            '--trim-end',
            help='Remove silence from the end of the track',
            action='store_true',
            default=False)
    parser.add_argument(
            '--solo-track-number',
            help='',
            type=int,
            default=0)
    parser.add_argument(
            '--solo-repetition-number',
            help='',
            type=int,
            default=0)

    args = parser.parse_args()

    return args


if __name__ == '__main__':
    args = get_args()

    phaser = Phase(
            args.input_file,
            n_tracks=args.n_tracks,
            gap=args.gap,
            initial_gap=args.initial_gap,
            repeat_count=args.repeat_count,
            end_align=args.end_align,
            start_pad_duration=args.start_pad_duration,
            end_pad_duration=args.end_pad_duration,
            temp_folder=args.temp_folder,
            output_folder=args.output_folder,
            fade=args.fade,
            quietest=args.quietest,
            gain=args.gain,
            trim_start=args.trim_start,
            trim_end=args.trim_end,
            solo_track_number=args.solo_track_number,
            solo_repetition_number=args.solo_repetition_number)

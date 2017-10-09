#!/usr/bin/env python

"""Automatic Steve Reich phasing music

Usage:
    ./phase.py test_input_file.wav test_output_file.wav --n-tracks=10 --gap=.02 --repeat-count=20 --end-align

"""

import os
import argparse

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
            output_file,
            n_tracks=10,
            gap=0.0,
            repeat_count=10,
            end_align=False,
            start_pad_duration=0.0,
            end_pad_duration=0.0,
            temp_folder='tmp/',
            fade=None):

        self.input_file = input_file
        self.output_file = output_file
        self.n_tracks = n_tracks
        self.gap = gap
        self.repeat_count = repeat_count
        self.end_align = end_align
        self.start_pad_duration = start_pad_duration
        self.end_pad_duration = end_pad_duration
        self.temp_folder = temp_folder
        self.fade = fade

        self.gain_dbs = get_gain_dbs(fade, n_tracks)

        self.sample = Sample(
                input_file,
                start_pad_duration=start_pad_duration,
                end_pad_duration=end_pad_duration)

        if not os.path.exists(self.temp_folder):
            os.mkdir(self.temp_folder)

        self.phase()

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
        if mute_first:
            tfm.pad(start_duration=self.sample.full_duration + rest_duration)
        if mute_last:
            tfm.pad(end_duration=self.sample.full_duration + rest_duration)
        tfm.gain(gain_db=gain_db)

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

        if mute_last:
            if remainder:
                # there are an odd number of repeats, so the muted last repetition is in track A
                self.make_track(track_a_file, local_gap, track_a_repeat_count, gain_db=gain_db, mute_last=mute_last)
                self.make_track(track_b_file, local_gap, track_b_repeat_count, gain_db=gain_db, has_initial_rest=True)
            else:
                # there are an even number of repeats, so the muted last repetition is in track B
                self.make_track(track_a_file, local_gap, track_a_repeat_count, gain_db=gain_db)
                self.make_track(track_b_file, local_gap, track_b_repeat_count, gain_db=gain_db, has_initial_rest=True, mute_last=mute_last)

        else:
            self.make_track(track_a_file, local_gap, track_a_repeat_count, gain_db=gain_db, mute_first=mute_first)
            self.make_track(track_b_file, local_gap, track_b_repeat_count, gain_db=gain_db, has_initial_rest=True)

        cbn = sox.Combiner()
        cbn.build([track_a_file, track_b_file], temp_output_file, 'mix-power')

    def phase(self):
        track_file_names = []
        for i in range(1, self.n_tracks + 1):
            track_file_name = self.temp_folder + 'track-{}.wav'.format(i)
            track_file_names.append(track_file_name)

            mute_first = False
            if not self.end_align and i is not 1:
                mute_first = True

            mute_last = False
            if self.end_align and i is not self.n_tracks:
                mute_last = True

            gain_db = self.gain_dbs[i - 1]

            self.checker_track(
                    track_file_name,
                    local_gap=self.gap * i,
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
        cbn.silence(location=1)  # Remove silence from the beginning
        cbn.silence(location=-1)  # Remove silence from the end
        cbn.build(track_file_names, self.output_file, 'mix-power')


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('input_file')
    parser.add_argument('output_file')

    parser.add_argument(
            '-n',
            '--n-tracks',
            help='how many tracks to generate',
            type=int,
            default=9)
    parser.add_argument(
            '-g',
            '--gap',
            help='the smallest gap between phrases',
            type=float,
            default=.03)
    parser.add_argument(
            '-r',
            '--repeat-count',
            help='the number of times the phrase should repeat',
            type=int,
            default=20)
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
            '-f',
            '--fade',
            help='relative volumes of tracks: flat, fade in, fade out, or fade in then out',
            default=None,
            choices=[None, 'in', 'out', 'in-out'])


    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()

    phaser = Phase(
            args.input_file,
            args.output_file,
            n_tracks=args.n_tracks,
            gap=args.gap,
            repeat_count=args.repeat_count,
            end_align=args.end_align,
            start_pad_duration=args.start_pad_duration,
            end_pad_duration=args.end_pad_duration,
            temp_folder=args.temp_folder,
            fade=args.fade)

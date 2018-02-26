#!/usr/bin/env python

"""Automatic Steve Reich phasing music

Usage:
    ./phase.py test_input_files/ravi1.wav --n-tracks=24 --gap=.02 --fade=in-out --repeat-count=20 --end-align

"""

import os
import datetime
import json

import sox

from track import Track


def fade_gains(direction, n_tracks, quietest=-60.0):
    if direction == 'flat':
        return [0.0 for _ in range(n_tracks)]

    elif direction == 'in-out':
        half = n_tracks / 2
        ins = fade_gains('in', half, quietest=quietest)
        outs = fade_gains('out', half, quietest=quietest)
        if n_tracks % 2:
            ins.append(0.0)
        return ins + outs

    elif direction == 'in' or direction == 'out':
        result = []
        chunk_size = -quietest / (n_tracks - 1)

        for i in range(n_tracks):
            this_chunk_size = chunk_size * i
            dB = quietest + this_chunk_size
            result.append(dB)

        if direction == 'out':
            result.reverse()

        return result

    else:
        raise Exception("Allowed values for fades are 'flat', 'in', 'out', and 'in-out'")


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
            fade='flat',
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

        self.gain_dbs = fade_gains(fade, n_tracks, quietest=quietest)

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

    def phase(self):
        track_file_names = []
        for track_number in range(self.n_tracks):
            track = Track(self, track_number)

            track_file_names.append(track.file_name)

        # TODO: Do the end-align adjustments in the Track class, preferably without having to re-render
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

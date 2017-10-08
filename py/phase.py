#!/usr/bin/env python

"""

phase.py sample.wav output.wav --n-tracks=10 --gap=.02 --repeat-count=20 --end-align



"""

import os
import argparse

import sox


class Sample(object):
    def __init__(self,
            file_name='master_sample.wav',
            start_pad_duration=0,
            end_pad_duration=0):
        self.file_name = file_name
        self.full_duration = sox.file_info.duration(file_name)
        self.start_pad_duration = start_pad_duration
        self.end_pad_duration = end_pad_duration


class Phase(object):
    def __init__(self,
            sample_file_name='master_sample.wav',
            output_file_name='output.wav',
            start_pad_duration=0,
            end_pad_duration=0):

        self.sox = sox
        self.sample = Sample(
            sample_file_name,
            start_pad_duration=start_pad_duration,
            end_pad_duration=end_pad_duration)
        self.output_file_name = output_file_name
        self.temp_folder = 'tmp/'
        if not os.path.exists(self.temp_folder):
            os.mkdir(self.temp_folder)

    def make_track(self,
            output_file_name,
            gap,
            repeat_count,
            has_initial_rest=False,
            mute_first=False,
            mute_last=False):

        rest_duration = self.sample.full_duration + gap - self.sample.start_pad_duration - self.sample.end_pad_duration

        if mute_first or mute_last:
            repeat_count -= 1

        tfm = sox.Transformer()
        tfm.pad(end_duration=rest_duration)
        if repeat_count > 0:
            tfm.repeat(count=repeat_count)
        if has_initial_rest:
            tfm.pad(start_duration=rest_duration + ((self.sample.full_duration - rest_duration) / 2.0))
        if mute_first:
            tfm.pad(start_duration=self.sample.full_duration + rest_duration)
        if mute_last:
            tfm.pad(end_duration=self.sample.full_duration + rest_duration)

        tfm.build(self.sample.file_name, output_file_name)

    def checker_track(self,
            output_file_name,
            gap=1.0,
            repeat_count=5,
            mute_first=False,
            mute_last=False):

        """Repeat the sample on alternating tracks so the fade in and out can overlap"""

        track_a_file = self.temp_folder + 'track-a.wav'
        track_b_file = self.temp_folder + 'track-b.wav'

        half, remainder = divmod(repeat_count, 2)
        track_a_repeat_count = half + remainder - 1
        track_b_repeat_count = half - 1

        if mute_last:
            if remainder:
                # there are an odd number of repeats, so the muted last repetition is in track A
                self.make_track(track_a_file, gap, track_a_repeat_count, mute_last=mute_last)
                self.make_track(track_b_file, gap, track_b_repeat_count, has_initial_rest=True)
            else:
                # there are an even number of repeats, so the muted last repetition is in track B
                self.make_track(track_a_file, gap, track_a_repeat_count)
                self.make_track(track_b_file, gap, track_b_repeat_count, has_initial_rest=True, mute_last=mute_last)

        else:
            self.make_track(track_a_file, gap, track_a_repeat_count, mute_first=mute_first)
            self.make_track(track_b_file, gap, track_b_repeat_count, has_initial_rest=True)

        cbn = sox.Combiner()
        cbn.build([track_a_file, track_b_file], output_file_name, 'mix-power')

    def phase(self,
            output_file_name=None,
            n_tracks=9,
            gap=.03,
            repeat_count=20,
            end_align=False):

        if output_file_name == None:
            output_file_name = self.output_file_name
        track_file_names = []
        for i in range(1, n_tracks + 1):
            track_file_name = self.temp_folder + 'track-{}.wav'.format(i)
            track_file_names.append(track_file_name)

            mute_first = False
            if not end_align and i is not 1:
                mute_first = True

            mute_last = False
            if end_align and i is not n_tracks:
                mute_last = True

            self.checker_track(
                track_file_name,
                gap=gap * i,
                repeat_count=repeat_count,
                mute_first=mute_first,
                mute_last=mute_last)

        if end_align:
            track_durations = [sox.file_info.duration(f) for f in track_file_names]
            longest_track_duration = max(track_durations)
            track_duration_diffs = [longest_track_duration - d for d in track_durations]
            new_track_file_names = []
            for i, diff, track_file_name in zip(range(1, n_tracks + 1), track_duration_diffs, track_file_names):
                new_track_file_name = track_file_name[:-4] + '-start-offset.wav'
                new_track_file_names.append(new_track_file_name)
                tfm = sox.Transformer()
                tfm.pad(start_duration=diff + (gap * i))
                tfm.build(track_file_name, new_track_file_name)
            track_file_names = new_track_file_names

        cbn = sox.Combiner()
        cbn.silence(location=1)  # Remove silence from the beginning
        cbn.silence(location=-1)  # Remove silence from the end
        cbn.build(track_file_names, output_file_name, 'mix-power')


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

    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()

    phaser = Phase(
            args.input_file,
            args.output_file,
            n_tracks=args.n_tracks,
            gap=args.gap,
            repeat_count=args.repeat_count,
            end_align=args.end_align
        )



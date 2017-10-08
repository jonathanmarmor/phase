#!/usr/bin/env python

"""

phase.py sample.wav output.wav --n-tracks=10 --gap=.02 --repeat-count=20 --end-align



"""

import os
import argparse

import sox


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
            temp_folder='tmp/'):

        self.input_file = input_file
        self.output_file = output_file
        self.n_tracks = n_tracks
        self.gap = gap
        self.repeat_count = repeat_count
        self.end_align = end_align
        self.start_pad_duration = start_pad_duration
        self.end_pad_duration = end_pad_duration
        self.temp_folder = temp_folder

        self.sox = sox

        self.sample = Sample(
                input_file,
                start_pad_duration=start_pad_duration,
                end_pad_duration=end_pad_duration)

        if not os.path.exists(self.temp_folder):
            os.mkdir(self.temp_folder)

        self.phase()

    def make_track(self, temp_output_file, local_gap, local_repeat_count,
            has_initial_rest=False, mute_first=False, mute_last=False):

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

        tfm.build(self.sample.file_name, temp_output_file)

    def checker_track(self, temp_output_file, local_gap, mute_first=False, mute_last=False):
        """Repeat the sample on alternating tracks so the fade in and out can overlap"""

        track_a_file = self.temp_folder + 'track-a.wav'
        track_b_file = self.temp_folder + 'track-b.wav'

        half, remainder = divmod(self.repeat_count, 2)
        track_a_repeat_count = half + remainder - 1
        track_b_repeat_count = half - 1

        if mute_last:
            if remainder:
                # there are an odd number of repeats, so the muted last repetition is in track A
                self.make_track(track_a_file, local_gap, track_a_repeat_count, mute_last=mute_last)
                self.make_track(track_b_file, local_gap, track_b_repeat_count, has_initial_rest=True)
            else:
                # there are an even number of repeats, so the muted last repetition is in track B
                self.make_track(track_a_file, local_gap, track_a_repeat_count)
                self.make_track(track_b_file, local_gap, track_b_repeat_count, has_initial_rest=True, mute_last=mute_last)

        else:
            self.make_track(track_a_file, local_gap, track_a_repeat_count, mute_first=mute_first)
            self.make_track(track_b_file, local_gap, track_b_repeat_count, has_initial_rest=True)

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

            self.checker_track(track_file_name, local_gap=self.gap * i,
                    mute_first=mute_first, mute_last=mute_last)

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

    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()

    print args

    phaser = Phase(
            args.input_file,
            args.output_file,
            n_tracks=args.n_tracks,
            gap=args.gap,
            repeat_count=args.repeat_count,
            end_align=args.end_align,
            start_pad_duration=args.start_pad_duration,
            end_pad_duration=args.end_pad_duration,
            temp_folder=args.temp_folder
        )

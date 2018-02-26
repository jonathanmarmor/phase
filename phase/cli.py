#!/usr/bin/env python

import argparse

from phase import Phase


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
            default='flat',
            choices=['flat', 'in', 'out', 'in-out'])
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


def main():
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


if __name__ == '__main__':
    main()

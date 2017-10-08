# phase.py

## Install

(on OS X)

1. Install [Homebrew](https://brew.sh/)
1. Install `sox`: `brew install sox --with-lame --with-flac --with-libvorbis`
1. Clone this repo
1. `cd phase/py`
1. `pip install -r requirements.txt`

## Run the example

1. `./phase.py test_input_file.wav test_output_file.wav --n-tracks=10 --gap=.02 --repeat-count=20 --end-align`
1. Open `test_output_file.wav` with an audio player and listen to it

## Run with your own sample

`./phase.py your_own_sample.wav your_own_output_file.wav --n-tracks=10 --gap=.02 --repeat-count=20 --end-align`

### Arguments

```
usage: phase.py [-h] [-n N_TRACKS] [-g GAP] [-r REPEAT_COUNT] [-e]
                [-S START_PAD_DURATION] [-E END_PAD_DURATION] [-t TEMP_FOLDER]
                input_file output_file

positional arguments:
  input_file
  output_file

optional arguments:
  -h, --help            show this help message and exit
  -n N_TRACKS, --n-tracks N_TRACKS
                        how many tracks to generate
  -g GAP, --gap GAP     the smallest gap between phrases
  -r REPEAT_COUNT, --repeat-count REPEAT_COUNT
                        the number of times the phrase should repeat
  -e, --end-align       come together in the end, rather than starting out
                        together
  -S START_PAD_DURATION, --start-pad-duration START_PAD_DURATION
                        duration of silence at the beginning of the sample
  -E END_PAD_DURATION, --end-pad-duration END_PAD_DURATION
                        duration of silence at the end of the sample
  -t TEMP_FOLDER, --temp-folder TEMP_FOLDER
                        path of directory to put temporary files in

```

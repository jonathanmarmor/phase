# phase.py

## Install

(on OS X)

1. Install [Homebrew](https://brew.sh/)
1. Install `sox`: `brew install sox --with-lame --with-flac --with-libvorbis`
1. Clone this repo
1. `cd phase/py`
1. `pip install -r requirements.txt`

## Run the example

1. `./phase.py test_input_files/ravi1.wav --n-tracks=24 --gap=.02 --fade=in-out --repeat-count=20 --end-align`
1. Open `output/ravi1/ravi1_<timestamp>.wav` with an audio player and listen to it

## Run with your own sample

1. `./phase.py your_own_sample.wav --n-tracks=8 --gap=.3 --repeat-count=10`
1. Look in `output/your_own_sample` for the resulting wav files

### Arguments

Do `./phase.py -h` to see all the arguments and options and how to use them.

### TODO

- Finish adding initial gap
- Make more and better options for fade curves

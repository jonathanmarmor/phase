# Phase

Website to automatically loop multiple copies of uploaded audio and make the copies go out of phase with each other.

## Usage

1. Go to http://phase.jonathanmarmor.com
2. Upload a short wav or mp3 file of your choosing (3 to 20 second clips are probably best)
3. Choose the number of copies of the file that will be played simultaneously
4. Choose the amount of time in milliseconds each copy will drift from other copies each time it loops
5. Choose the total amount of time the phasing will go on for
6. Click start
7. Listen

## Credit

Uses [howler.js](http://goldfirestudios.com/blog/104/howler.js-Modern-Web-Audio-Javascript-Library) to make it easier to do really simple stuff with the Web Audio API.

Oh, and [Steve Reich](http://youtu.be/g0WVh1D0N50).

## Run your own on Ubuntu

Locally:

    git clone https://github.com/jonathanmarmor/ops.git
    pip install fabric
    cd ops
    fab -H <hostname> phase.install

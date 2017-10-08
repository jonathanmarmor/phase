'use strict';

function play(sound, start){
    setTimeout(function(){
        sound.play();
    }, start);
}

function playPiece(sound, gap, numTracks, totalDuration){
    var track,
        start,
        origGap = gap,
        soundDuration = sound._duration * 1000;

    for(track = 0; track < numTracks; track++){
        play(sound, 0);
    }

    for(start = soundDuration; start < totalDuration; start += soundDuration){
        for(track = 0; track < numTracks; track++){
            play(sound, start + (gap * track));
        }
        gap += origGap;
    }

}

function run(filename){
    var gap = Number(document.getElementById('gap').value),
        numTracks = Number(document.getElementById('numTracks').value),
        totalDuration = Number(document.getElementById('totalDuration').value) * 60 * 1000,
        sound = new Howl({
            'urls': ['/static/audio/' + filename],
            'onload': function(){
                playPiece(sound, gap, numTracks, totalDuration);
            }
        });
}

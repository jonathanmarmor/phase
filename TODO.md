## Phase v1 To Do

- Client app needs to be able to deal with the audio directly rather than needing it to be served by a webserver.  This requires tearing howler.js apart a bit, but that was bound to be necessary.

- Background task to store clip on archive.org (use S3 if this violates their terms of service).

- Background task to render a wav of the entire phase and upload it to archive.org.

- Way to get back to previously uploaded clips and previously rendered phases.

- Best of, voting system?  No, that's dumb.  Makes it a clinical demonstration rather than art.

- Some kind of visualization of what's happening.  Both diagramatic and spectragram.

- Drag and drop to ingest audio.

- Adjust loop window within uploaded clip.

- Test how it works in other browsers.

- Make frontend app a Backbone app.  I think this is appropriate.

- Display gap as milliseconds with a decimal.  Ie: 20.0.

- Volume slider/knob/field.

- Mute button.

- Stop button.

- Restart same clip after stopping without having to re-upload.

- Adjust gap, total duration, number of tracks then restart without having to re-upload.

- Adjust gap, total duration, number of tracks on the fly!

- Volume for each track.

- Pan for each track.

- Speed for each track (possibly as an option instead of gap, or combine gap and speed).

- Pitch shift for each track.

- Pause and scrubbing would be amazing.  Would be easy with rendered audio of course, but probably very hard to implement if unrendered.

- Is it possible or desirable to process the audio somehow (compression?) so the first time through isn't 10x louder than the rest?

- There must be a better way to schedule sounds than setTimeout.

- Multiple phases at the same time.  With different clips and/or different settings.

- Add ability to slow down or speed up (change the tempo) on the fly.  This means what we're using as milli/seconds actually is some metrical substrate that starts out matching milli/seconds but their values can actually be changed.  Maybe also change the values displayed to the user for gap, period duration, etc.




def linear(track_number, gap):
    return track_number * gap

def fib(a=1, b=1):
    print float(b) / a
    a = b
    b = a + b
    return fib(a, b)

class Fib(object):
    def __init__(self, a=1, b=1):
        self.a = a
        self.b = b
    @property
    def ratio(self):
        return float(self.b) / self.a
    def next(self):
        ratio = self.ratio
        a = self.a
        self.a = self.b
        self.b = a + self.b
        return ratio


class Phase(object):
    def __init__(self, dur, gap, num_tracks):
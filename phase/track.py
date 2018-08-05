import sox


class Track(object):
    def __init__(self, phase, track_number):
        self.phase = phase
        self.track_number = track_number

        self.file_name = '{}track-{}.wav'.format(phase.temp_folder, track_number)

        self.mute_first = False
        self.mute_last = False
        if track_number != phase.solo_track_number:
            # Mute one of the repetitions in this track
            if phase.solo_repetition_number == 0:
                self.mute_first = True
            elif phase.solo_repetition_number == phase.repeat_count - 1:
                self.mute_last = True
            # TODO: Support repetition numbers other than first and last

        self.gain_db = phase.gain_dbs[track_number]

        self.checker_track(
            self.file_name,
            local_gap=phase.gap * (track_number + 1))

    def checker_track(self, temp_output_file, local_gap):
        """Repeat the sample on alternating tracks so the fade in and out can overlap"""

        track_a_file = self.phase.temp_folder + 'track-a.wav'
        track_b_file = self.phase.temp_folder + 'track-b.wav'

        half, remainder = divmod(self.phase.repeat_count, 2)
        track_a_repeat_count = half + remainder - 1
        track_b_repeat_count = half - 1

        # Soloing
        mute_last_a = False
        mute_last_b = False
        if self.mute_last:
            if remainder:
                # There are an odd number of repeats, so the muted last repetition is in track A
                mute_last_a = True
            else:
                # There are an even number of repeats, so the muted last repetition is in track B
                mute_last_b = True

        self.make_track(
                track_a_file,
                local_gap,
                track_a_repeat_count,
                mute_first=self.mute_first,
                mute_last=mute_last_a)
        self.make_track(
                track_b_file,
                local_gap,
                track_b_repeat_count,
                mute_last=mute_last_b,
                has_initial_rest=True)

        cbn = sox.Combiner()
        cbn.build([track_a_file, track_b_file], temp_output_file, 'mix-power')

    def make_track(self,
            temp_output_file,
            local_gap,
            local_repeat_count,
            has_initial_rest=False,
            mute_first=False,
            mute_last=False):

        rest_duration = self.phase.sample.full_duration + local_gap - self.phase.sample.start_pad_duration - self.phase.sample.end_pad_duration

        if mute_first or mute_last:
            local_repeat_count -= 1

        tfm = sox.Transformer()
        tfm.pad(end_duration=rest_duration)
        if local_repeat_count > 0:
            tfm.repeat(count=local_repeat_count)
        if has_initial_rest:
            tfm.pad(start_duration=rest_duration + ((self.phase.sample.full_duration - rest_duration) / 2.0))

        # Soloing
        if mute_first:
            tfm.pad(start_duration=self.phase.sample.full_duration + rest_duration)
        if mute_last:
            tfm.pad(end_duration=self.phase.sample.full_duration + rest_duration)

        tfm.gain(gain_db=self.gain_db + self.phase.gain)

        tfm.build(self.phase.sample.file_name, temp_output_file)

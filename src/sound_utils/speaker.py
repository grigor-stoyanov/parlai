"""The speaker: plays raw 16-bit audio."""

import sounddevice as sd

from sound_utils.audio_device import AudioDevice


class Speaker(AudioDevice):
    label = "Output"
    channels_key = "max_output_channels"
    default_slot = 1
    check_settings = staticmethod(sd.check_output_settings)

    def play(self, audio: bytes) -> None:
        """Play raw audio through the chosen speaker, with playback gain applied."""
        with sd.RawOutputStream(
            device=self.resolve(),
            samplerate=self.settings.sample_rate,
            channels=self.settings.channels,
            dtype="int16",
        ) as stream:
            stream.write(self.apply_gain(audio, self.settings.playback_gain))

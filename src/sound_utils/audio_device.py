"""Base class for a sound device: choose it, check it opens, save audio. Subclasses: Microphone, Speaker."""

import logging
import wave
from pathlib import Path

import sounddevice as sd

from config.settings import Settings
from event_logger.json_log import log_event
from sound_utils.audio_levels import AudioLevels
from sound_utils.device_picker import NoAudioDeviceError, PlatformDevicePicker

SAMPLE_WIDTH_BYTES = 2  # 16-bit audio

logger = logging.getLogger(__name__)


class AudioDevice(AudioLevels, PlatformDevicePicker):
    """A sound device we can pick, check and save audio for. Subclasses fill in the attributes."""

    # label and channels_key (needed by the picker) are set by Microphone and Speaker.
    default_slot: int  # position in sd.default.device: 0 = input, 1 = output
    hint: str = ""  # extra advice appended to "can't be opened" errors
    # staticmethod so the sounddevice function is not bound to self when called.
    check_settings = staticmethod(sd.check_input_settings)

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def requested(self) -> str | None:
        """An explicit device from settings (index or name substring); None means choose for me."""
        return None

    def choose(self) -> int:
        """Pick a device from what is plugged in right now, without opening it."""
        return self.pick(
            list(sd.query_devices()), sd.default.device[self.default_slot], self.requested()
        )

    def resolve(self) -> int:
        """Choose a device and check it opens with our settings, so failures are clear."""
        index = self.choose()
        try:
            self.check_settings(
                device=index,
                samplerate=self.settings.sample_rate,
                channels=self.settings.channels,
                dtype="int16",
            )
        except sd.PortAudioError as error:
            name = sd.query_devices(index)["name"]
            raise NoAudioDeviceError(
                f"{self.label} device {index} ({name}) can't be opened: {error}.{self.hint}"
            ) from error
        name = sd.query_devices(index)["name"]
        log_event(
            logger,
            logging.INFO,
            "audio_device",
            f"{self.label.lower()} device selected",
            index=index,
            name=name,
            sample_rate=self.settings.sample_rate,
        )
        return index

    def save_wav(self, path: Path, audio: bytes) -> None:
        """Write raw 16-bit audio to a .wav file, creating the folder if needed."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(path), "wb") as wav:
            wav.setnchannels(self.settings.channels)
            wav.setsampwidth(SAMPLE_WIDTH_BYTES)
            wav.setframerate(self.settings.sample_rate)
            wav.writeframes(audio)

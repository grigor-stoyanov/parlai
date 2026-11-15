"""The microphone: lists input devices and records raw 16-bit audio."""

import queue
from typing import Any

import sounddevice as sd

from sound_utils.audio_device import AudioDevice


class Microphone(AudioDevice):
    label = "Input"
    channels_key = "max_input_channels"
    default_slot = 0
    hint = " Set PARLAI_INPUT_DEVICE to another one from the list."
    check_settings = staticmethod(sd.check_input_settings)

    def requested(self) -> str | None:
        return self.settings.input_device

    def list_devices(self) -> None:
        """Print every input device with its host API, marking the one parlai will use."""
        devices = sd.query_devices()
        host_apis = sd.query_hostapis()
        chosen = self.choose()
        for index, device in enumerate(devices):
            if device[self.channels_key] > 0:
                api = host_apis[device["hostapi"]]["name"]
                marker = "  <- selected" if index == chosen else ""
                print(f"{index}: {device['name']} [{api}]{marker}")

    def record(self, seconds: float) -> bytes:
        """
        Record from the chosen microphone.

        :param seconds: how long to record.
        :return: raw 16-bit audio as one continuous byte string, with input gain applied.
        """
        blocks: queue.Queue[bytes] = queue.Queue()

        # indata is a raw cffi buffer (not a numpy array, since we use RawInputStream).
        def on_audio(indata: Any, frames: int, time_info: Any, status: sd.CallbackFlags) -> None:
            blocks.put(bytes(indata))

        device = self.resolve()
        blocks_needed = int(seconds * self.settings.sample_rate / self.settings.block_size)
        with sd.RawInputStream(
            device=device,
            samplerate=self.settings.sample_rate,
            channels=self.settings.channels,
            dtype="int16",
            blocksize=self.settings.block_size,
            callback=on_audio,
        ):
            collected = [blocks.get() for _ in range(blocks_needed)]
        return self.apply_gain(b"".join(collected), self.settings.input_gain)

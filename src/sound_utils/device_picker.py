"""Choosing a device from a list: the user's request first, else per-platform defaults."""

import sys
from collections.abc import Mapping, Sequence
from typing import Any

# On Linux PortAudio only sees ALSA. These ALSA plugin devices forward to the sound server
# (PipeWire/PulseAudio), so they follow the user's real default device. Raw hw:X,Y devices
# bypass that routing and can be busy or silent, so they are never chosen automatically.
LINUX_PREFERRED_NAMES = ("pipewire", "pulse", "default")


class NoAudioDeviceError(RuntimeError):
    """No usable microphone or speaker could be chosen."""


class DevicePicker:
    """
    Mixin that chooses a device index. Needs `label` and `channels_key` from the class using it.
    On Windows and macOS PortAudio's default follows the OS, so it is trusted.
    """

    label: str  # "Input" or "Output", used in error messages
    channels_key: str  # which field of sd.query_devices() says the device can do our job

    @classmethod
    def pick(
        cls,
        devices: Sequence[Mapping[str, Any]],
        default_index: int,
        requested: str | None = None,
    ) -> int:
        """
        Choose a device index from a device list. Pure, so it can be tested without hardware.

        :param devices: what sd.query_devices() returns.
        :param default_index: PortAudio's default for this kind of device; -1 when it has none.
        :param requested: an index or a name substring, or None.
        :raises NoAudioDeviceError: if the request matches nothing or no device can do the job.
        """
        usable = [i for i, d in enumerate(devices) if d[cls.channels_key] > 0]
        if not usable:
            raise NoAudioDeviceError(f"No {cls.label.lower()} devices found.")

        if requested:
            if requested.isdigit() and int(requested) in usable:
                return int(requested)
            matches = [i for i in usable if requested.lower() in devices[i]["name"].lower()]
            if not matches:
                raise NoAudioDeviceError(f"{requested!r} matches no {cls.label.lower()} device.")
            return matches[0]

        return cls.choose_default(devices, usable, default_index)

    @classmethod
    def choose_default(
        cls, devices: Sequence[Mapping[str, Any]], usable: list[int], default_index: int
    ) -> int:
        """Trust PortAudio's default if it can do the job, else the first usable device."""
        return default_index if default_index in usable else usable[0]


class LinuxDevicePicker(DevicePicker):
    """Prefers the sound-server plugins over PortAudio's guess, which ignores PipeWire."""

    @classmethod
    def choose_default(
        cls, devices: Sequence[Mapping[str, Any]], usable: list[int], default_index: int
    ) -> int:
        # PortAudio on ALSA invents a default (the first device, usually a raw hw: one) when ALSA
        # has no "default" PCM. So a hw: default is not trusted if a plugin is available.
        default_is_raw_hw = default_index in usable and "(hw:" in devices[default_index]["name"]
        if default_is_raw_hw or default_index not in usable:
            for wanted in LINUX_PREFERRED_NAMES:
                for i in usable:
                    if devices[i]["name"].lower() == wanted:
                        return i
        return super().choose_default(devices, usable, default_index)


# Chosen once at import: the platform does not change while we run.
PlatformDevicePicker = LinuxDevicePicker if sys.platform.startswith("linux") else DevicePicker

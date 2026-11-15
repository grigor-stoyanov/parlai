import pytest

from sound_utils.audio_device import NoAudioDeviceError
from sound_utils.microphone import Microphone
from sound_utils.speaker import Speaker


def dev(name, inputs=1, outputs=0):
    return {"name": name, "max_input_channels": inputs, "max_output_channels": outputs}


DEVICES = [dev("hdmi", 0), dev("HD-Audio Generic: ALC245 Analog (hw:2,0)"), dev("pipewire"), dev("pulse")]


def test_explicit_index_wins():
    assert Microphone.pick(DEVICES, default_index=-1, requested="3") == 3


def test_explicit_name_substring_is_case_insensitive():
    assert Microphone.pick(DEVICES, default_index=-1, requested="ALC") == 1


def test_unmatched_request_is_an_error():
    with pytest.raises(NoAudioDeviceError):
        Microphone.pick(DEVICES, default_index=-1, requested="usb mic")


def test_valid_portaudio_default_is_used():
    assert Microphone.pick(DEVICES, default_index=3) == 3


def test_falls_back_to_first_input_device():
    devices = [dev("out", 0), dev("USB Mic"), dev("Other")]
    assert Microphone.pick(devices, default_index=-1) == 1


def test_no_input_devices_is_an_error():
    with pytest.raises(NoAudioDeviceError):
        Microphone.pick([dev("hdmi", 0)], default_index=-1)


def test_speaker_ignores_input_only_devices():
    devices = [dev("mic", 1, 0), dev("speakers", 0, 2)]
    assert Speaker.pick(devices, default_index=-1) == 1

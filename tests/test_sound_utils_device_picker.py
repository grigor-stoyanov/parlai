from sound_utils.device_picker import DevicePicker, LinuxDevicePicker


def dev(name):
    return {"name": name}


# Shaped like the PipeWire case: hw first (also PortAudio's invented default), plugins later.
DEVICES = [dev("hdmi"), dev("HD-Audio Generic: ALC245 Analog (hw:2,0)"), dev("pipewire"), dev("pulse")]
USABLE = [1, 2, 3]


def test_no_default_prefers_pipewire_over_hw():
    assert LinuxDevicePicker.choose_default(DEVICES, USABLE, default_index=-1) == 2


def test_hw_default_is_overridden_by_pipewire():
    assert LinuxDevicePicker.choose_default(DEVICES, USABLE, default_index=1) == 2


def test_non_hw_default_is_kept():
    assert LinuxDevicePicker.choose_default(DEVICES, USABLE, default_index=3) == 3


def test_hw_default_is_kept_when_no_sound_server_plugin():
    devices = [dev("Mic (hw:0,0)"), dev("Other (hw:1,0)")]
    assert LinuxDevicePicker.choose_default(devices, [0, 1], default_index=1) == 1


def test_default_picker_ignores_plugins_and_trusts_portaudio():
    assert DevicePicker.choose_default(DEVICES, USABLE, default_index=1) == 1
    assert DevicePicker.choose_default(DEVICES, USABLE, default_index=-1) == 1

import array

from sound_utils.audio_levels import AudioLevels

apply_gain = AudioLevels.apply_gain


def samples(*values):
    return array.array("h", values).tobytes()


def test_gain_of_one_leaves_audio_unchanged():
    audio = samples(100, -200, 300)
    assert apply_gain(audio, 1.0) == audio


def test_gain_scales_samples():
    assert apply_gain(samples(100, -200), 2.0) == samples(200, -400)
    assert apply_gain(samples(100, -200), 0.5) == samples(50, -100)


def test_loud_samples_clip_instead_of_wrapping():
    assert apply_gain(samples(30000, -30000), 2.0) == samples(32767, -32768)

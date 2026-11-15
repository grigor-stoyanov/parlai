import array

import pytest

from sound_utils.audio_levels import SILENCE_DBFS, AudioLevels

measure_levels = AudioLevels.measure_levels


def samples(*values):
    return array.array("h", values).tobytes()


def test_full_scale_square_wave_is_zero_dbfs():
    peak, rms = measure_levels(samples(32767, -32767, 32767, -32767))
    assert peak == pytest.approx(0.0)
    assert rms == pytest.approx(0.0)


def test_half_amplitude_is_about_minus_6_dbfs():
    peak, rms = measure_levels(samples(16384, -16384))
    assert peak == pytest.approx(-6.0, abs=0.1)
    assert rms == pytest.approx(-6.0, abs=0.1)


def test_peak_is_higher_than_rms_for_a_spiky_signal():
    peak, rms = measure_levels(samples(0, 0, 0, 20000))
    assert peak > rms


def test_silence_and_empty_audio_use_the_floor():
    assert measure_levels(samples(0, 0)) == (SILENCE_DBFS, SILENCE_DBFS)
    assert measure_levels(b"") == (SILENCE_DBFS, SILENCE_DBFS)

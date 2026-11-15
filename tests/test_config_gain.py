import pytest

from config.settings import ConfigError, load_settings


def test_gains_default_to_one():
    settings = load_settings({})
    assert settings.input_gain == 1.0
    assert settings.playback_gain == 1.0


def test_gains_are_read_from_env():
    settings = load_settings({"PARLAI_INPUT_GAIN": "2.5", "PARLAI_PLAYBACK_GAIN": "3"})
    assert settings.input_gain == 2.5
    assert settings.playback_gain == 3.0


@pytest.mark.parametrize("value", ["abc", "0", "-1", "nan", "inf"])
def test_bad_gain_is_rejected_with_e003(value):
    with pytest.raises(ConfigError) as error:
        load_settings({"PARLAI_PLAYBACK_GAIN": value})
    assert "PARLAI-E003" in str(error.value)
    assert "PARLAI_PLAYBACK_GAIN" in str(error.value)

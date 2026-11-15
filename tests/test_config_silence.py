import pytest

from config.settings import ConfigError, load_settings


def test_utterance_silence_defaults_to_500_ms():
    assert load_settings({}).utterance_silence_ms == 500


def test_utterance_silence_is_read_from_env():
    assert load_settings({"PARLAI_UTTERANCE_SILENCE_MS": "800"}).utterance_silence_ms == 800


@pytest.mark.parametrize("value", ["abc", "0", "-5", "0.5"])
def test_bad_utterance_silence_is_rejected_with_e001(value):
    with pytest.raises(ConfigError) as error:
        load_settings({"PARLAI_UTTERANCE_SILENCE_MS": value})

    assert "PARLAI-E001" in str(error.value)
    assert "PARLAI_UTTERANCE_SILENCE_MS" in str(error.value)

import pytest

from config.settings import ConfigError, load_settings


def test_utterance_max_defaults_to_15_seconds():
    assert load_settings({}).utterance_max_ms == 15000


def test_utterance_max_is_read_from_env():
    assert load_settings({"PARLAI_UTTERANCE_MAX_MS": "8000"}).utterance_max_ms == 8000


@pytest.mark.parametrize("value", ["abc", "0", "-5", "0.5"])
def test_bad_utterance_max_is_rejected_with_e001(value):
    with pytest.raises(ConfigError) as error:
        load_settings({"PARLAI_UTTERANCE_MAX_MS": value})

    assert "PARLAI-E001" in str(error.value)
    assert "PARLAI_UTTERANCE_MAX_MS" in str(error.value)

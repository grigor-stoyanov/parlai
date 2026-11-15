import pytest

from config.settings import ConfigError, load_settings


def test_whisper_defaults_to_small_english_on_auto_device():
    settings = load_settings({})

    assert settings.whisper_model == "small.en"
    assert settings.whisper_device == "auto"


def test_whisper_values_are_read_from_env():
    settings = load_settings({"PARLAI_WHISPER_MODEL": "base.en", "PARLAI_WHISPER_DEVICE": "CPU"})

    assert settings.whisper_model == "base.en"
    assert settings.whisper_device == "cpu"


def test_empty_whisper_values_use_the_defaults():
    settings = load_settings({"PARLAI_WHISPER_MODEL": "", "PARLAI_WHISPER_DEVICE": ""})

    assert (settings.whisper_model, settings.whisper_device) == ("small.en", "auto")


def test_unknown_device_is_rejected_with_e201_and_lists_the_allowed_values():
    with pytest.raises(ConfigError) as error:
        load_settings({"PARLAI_WHISPER_DEVICE": "tpu"})

    message = str(error.value)
    assert "PARLAI-E201" in message
    assert "PARLAI_WHISPER_DEVICE" in message
    assert "auto or cuda or cpu" in message

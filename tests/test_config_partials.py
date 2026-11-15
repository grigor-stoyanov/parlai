import pytest

from config.settings import ConfigError, load_settings


def test_partials_default_to_every_700_ms_over_the_latest_8_seconds():
    settings = load_settings({})

    assert settings.partial_interval_ms == 700
    assert settings.partial_window_ms == 8000


def test_partial_settings_are_read_from_env():
    settings = load_settings(
        {"PARLAI_PARTIAL_INTERVAL_MS": "1000", "PARLAI_PARTIAL_WINDOW_MS": "5000"}
    )

    assert settings.partial_interval_ms == 1000
    assert settings.partial_window_ms == 5000


def test_an_interval_of_zero_turns_partials_off():
    assert load_settings({"PARLAI_PARTIAL_INTERVAL_MS": "0"}).partial_interval_ms == 0


@pytest.mark.parametrize("value", ["abc", "-1", "0.5"])
def test_a_bad_interval_is_rejected_with_e004(value):
    with pytest.raises(ConfigError) as error:
        load_settings({"PARLAI_PARTIAL_INTERVAL_MS": value})

    assert "PARLAI-E004" in str(error.value)
    assert "PARLAI_PARTIAL_INTERVAL_MS" in str(error.value)


@pytest.mark.parametrize("value", ["abc", "0", "-5"])
def test_a_bad_window_is_rejected_with_e001(value):
    with pytest.raises(ConfigError) as error:
        load_settings({"PARLAI_PARTIAL_WINDOW_MS": value})

    assert "PARLAI-E001" in str(error.value)
    assert "PARLAI_PARTIAL_WINDOW_MS" in str(error.value)

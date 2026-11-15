import pytest

from config.settings import ConfigError, load_settings


def test_logging_defaults():
    settings = load_settings({})

    assert (str(settings.log_dir), settings.log_level, settings.log_max_mb) == ("logs", "INFO", 50)
    assert (settings.log_keep_days, settings.log_console_level) == (14, "WARNING")
    assert (settings.log_name, settings.log_format) == ("parlai", "json")
    assert "httpx" in settings.log_quiet_loggers


def test_logging_values_are_read_from_env():
    settings = load_settings(
        {"PARLAI_LOG_DIR": "/tmp/x", "PARLAI_LOG_LEVEL": "debug", "PARLAI_LOG_MAX_MB": "10"}
    )

    assert (str(settings.log_dir), settings.log_level, settings.log_max_mb) == (
        "/tmp/x",
        "DEBUG",
        10,
    )


def test_unknown_log_level_is_rejected_with_e301():
    with pytest.raises(ConfigError) as error:
        load_settings({"PARLAI_LOG_LEVEL": "LOUD"})

    assert "PARLAI-E301" in str(error.value)
    assert "DEBUG or INFO or WARNING or ERROR" in str(error.value)


@pytest.mark.parametrize("value", ["abc", "0", "-1"])
def test_bad_max_size_is_rejected_with_e001(value):
    with pytest.raises(ConfigError) as error:
        load_settings({"PARLAI_LOG_MAX_MB": value})

    assert "PARLAI-E001" in str(error.value)


def test_a_log_dir_that_is_a_file_is_rejected_with_e002(tmp_path):
    file = tmp_path / "afile"
    file.write_text("x")

    with pytest.raises(ConfigError) as error:
        load_settings({"PARLAI_LOG_DIR": str(file)})

    assert "PARLAI-E002" in str(error.value)


def test_keep_days_and_console_level_are_read_from_env():
    settings = load_settings({"PARLAI_LOG_KEEP_DAYS": "3", "PARLAI_LOG_CONSOLE_LEVEL": "off"})

    assert (settings.log_keep_days, settings.log_console_level) == (3, "OFF")


@pytest.mark.parametrize("value", ["abc", "0", "-1"])
def test_bad_keep_days_is_rejected_with_e001(value):
    with pytest.raises(ConfigError) as error:
        load_settings({"PARLAI_LOG_KEEP_DAYS": value})

    assert "PARLAI-E001" in str(error.value)
    assert "PARLAI_LOG_KEEP_DAYS" in str(error.value)


def test_unknown_console_level_is_rejected_with_e302():
    with pytest.raises(ConfigError) as error:
        load_settings({"PARLAI_LOG_CONSOLE_LEVEL": "LOUD"})

    assert "PARLAI-E302" in str(error.value)
    assert "OFF" in str(error.value)


def test_name_format_and_quiet_loggers_are_read_from_env():
    settings = load_settings(
        {
            "PARLAI_LOG_NAME": "my-app_2",
            "PARLAI_LOG_FORMAT": "TEXT",
            "PARLAI_LOG_QUIET_LOGGERS": "a.b, c ,,d",
        }
    )

    assert (settings.log_name, settings.log_format) == ("my-app_2", "text")
    assert settings.log_quiet_loggers == ("a.b", "c", "d")


def test_quiet_loggers_none_means_no_loggers_and_empty_means_the_default():
    assert load_settings({"PARLAI_LOG_QUIET_LOGGERS": "none"}).log_quiet_loggers == ()
    assert "httpx" in load_settings({"PARLAI_LOG_QUIET_LOGGERS": " "}).log_quiet_loggers


@pytest.mark.parametrize("value", ["a/b", "..", "my log", "x.y", "name\\z"])
def test_a_log_name_that_is_not_a_plain_word_is_rejected_with_e303(value):
    with pytest.raises(ConfigError) as error:
        load_settings({"PARLAI_LOG_NAME": value})

    assert "PARLAI-E303" in str(error.value)


def test_unknown_log_format_is_rejected_with_e304():
    with pytest.raises(ConfigError) as error:
        load_settings({"PARLAI_LOG_FORMAT": "xml"})

    assert "PARLAI-E304" in str(error.value)
    assert "json or text" in str(error.value)

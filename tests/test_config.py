from pathlib import Path

import pytest

from config.settings import ConfigError, Settings, load_settings


def message_for(env):
    with pytest.raises(ConfigError) as error:
        load_settings(env)
    return str(error.value)


def test_defaults_when_nothing_is_set():
    settings = load_settings({})

    assert settings == Settings(
        sample_rate=16000,
        block_size=512,
        channels=1,
        recordings_dir=Path("recordings"),
    )


def test_valid_env_values_override_the_defaults():
    env = {
        "PARLAI_SAMPLE_RATE": "16000",
        "PARLAI_BLOCK_SIZE": "512",
        "PARLAI_CHANNELS": "1",
        "PARLAI_RECORDINGS_DIR": "/tmp/audio",
    }

    settings = load_settings(env)

    assert settings == Settings(
        sample_rate=16000,
        block_size=512,
        channels=1,
        recordings_dir=Path("/tmp/audio"),
    )


@pytest.mark.parametrize("name", ["PARLAI_SAMPLE_RATE", "PARLAI_BLOCK_SIZE", "PARLAI_CHANNELS"])
@pytest.mark.parametrize("value", ["abc", "0", "-5", "1.5"])
def test_non_numbers_are_rejected_with_e001(name, value):
    message = message_for({name: value})

    assert "PARLAI-E001" in message
    assert name in message


def test_unsupported_sample_rate_is_rejected_with_e101_and_lists_the_allowed_values():
    message = message_for({"PARLAI_SAMPLE_RATE": "44100"})

    assert "PARLAI-E101" in message
    assert "PARLAI_SAMPLE_RATE" in message
    assert "16000" in message
    assert "44100" in message


@pytest.mark.parametrize("rate", ["8000", "22050", "48000"])
def test_only_16000_hz_is_accepted_because_the_vad_and_whisper_need_it(rate):
    message = message_for({"PARLAI_SAMPLE_RATE": rate})

    assert "PARLAI-E101" in message
    assert rate in message


def test_more_than_one_channel_is_rejected_with_e103():
    message = message_for({"PARLAI_CHANNELS": "2"})

    assert "PARLAI-E103" in message
    assert "PARLAI_CHANNELS" in message


@pytest.mark.parametrize(
    "rate, block",
    [("16000", "256"), ("16000", "480"), ("16000", "1024")],
)
def test_block_size_must_match_the_sample_rate_e102(rate, block):
    message = message_for({"PARLAI_SAMPLE_RATE": rate, "PARLAI_BLOCK_SIZE": block})

    assert "PARLAI-E102" in message
    assert "PARLAI_BLOCK_SIZE" in message


def test_block_size_message_says_which_size_the_rate_requires():
    message = message_for({"PARLAI_SAMPLE_RATE": "16000", "PARLAI_BLOCK_SIZE": "256"})

    assert "512" in message


def test_block_size_is_not_checked_when_the_sample_rate_itself_is_invalid():
    message = message_for({"PARLAI_SAMPLE_RATE": "44100", "PARLAI_BLOCK_SIZE": "512"})

    assert "PARLAI-E101" in message
    assert "PARLAI-E102" not in message


def test_all_problems_are_reported_together():
    message = message_for({"PARLAI_SAMPLE_RATE": "abc", "PARLAI_CHANNELS": "2"})

    assert "PARLAI-E001" in message
    assert "PARLAI-E103" in message


def test_recordings_dir_that_is_a_file_is_rejected_with_e002(tmp_path):
    a_file = tmp_path / "not_a_folder"
    a_file.write_text("")

    message = message_for({"PARLAI_RECORDINGS_DIR": str(a_file)})

    assert "PARLAI-E002" in message
    assert "PARLAI_RECORDINGS_DIR" in message


def test_block_size_follows_the_sample_rate_when_it_is_not_set():
    assert load_settings({"PARLAI_SAMPLE_RATE": "16000"}).block_size == 512

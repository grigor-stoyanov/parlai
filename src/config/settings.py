"""The Settings record and load_settings, which builds it from the PARLAI_* variables.

Reading and checking each group of settings is in audio_settings, speech_settings and
log_settings; the rules they check against are in rules.py.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from config import rules
from config.audio_settings import read_audio_settings
from config.log_settings import read_log_settings
from config.speech_settings import read_speech_settings


class ConfigError(ValueError):
    """One or more settings are invalid. The message lists every problem."""


@dataclass(frozen=True)
class Settings:
    sample_rate: int
    block_size: int
    channels: int
    recordings_dir: Path
    # None = pick automatically; otherwise a device index or a name substring.
    input_device: str | None = None
    # Software volume multipliers (1.0 = unchanged), applied to the mic and to playback.
    input_gain: float = 1.0
    playback_gain: float = 1.0
    # Speech recognition: a faster-whisper model name, and where it runs (auto, cuda or cpu).
    whisper_model: str = rules.DEFAULT_WHISPER_MODEL
    whisper_device: str = rules.DEFAULT_WHISPER_DEVICE
    # How long you must stay silent, in milliseconds, before an utterance counts as finished.
    utterance_silence_ms: int = rules.DEFAULT_UTTERANCE_SILENCE_MS
    # The longest one utterance can run, in milliseconds. Then it is finished and listening
    # carries on as a new one.
    utterance_max_ms: int = rules.DEFAULT_UTTERANCE_MAX_MS
    # Live text while speaking: how often (0 = off) and over how much of the latest audio.
    partial_interval_ms: int = rules.DEFAULT_PARTIAL_INTERVAL_MS
    partial_window_ms: int = rules.DEFAULT_PARTIAL_WINDOW_MS
    # Logging: daily files go in log_dir; the oldest are deleted past log_max_mb in total.
    log_dir: Path = Path("logs")
    log_level: str = rules.DEFAULT_LOG_LEVEL
    log_max_mb: int = rules.DEFAULT_LOG_MAX_MB
    log_keep_days: int = rules.DEFAULT_LOG_KEEP_DAYS
    log_console_level: str = rules.DEFAULT_LOG_CONSOLE_LEVEL
    log_name: str = rules.DEFAULT_LOG_NAME
    log_format: str = rules.DEFAULT_LOG_FORMAT
    # Third-party loggers turned down to warnings so they don't flood the log.
    log_quiet_loggers: tuple[str, ...] = rules.DEFAULT_QUIET_LOGGERS


def load_settings(env: Mapping[str, str]) -> Settings:
    """
    Build Settings from environment variables, using defaults for any that are missing or empty.

    :param env: the variables to read, normally os.environ.
    :raises ConfigError: if any value is invalid; the message names every broken rule.
    """
    problems: list[str] = []
    values = {
        **read_audio_settings(env, problems),
        **read_speech_settings(env, problems),
        **read_log_settings(env, problems),
    }
    if problems:
        raise ConfigError("\n".join(problems))
    return Settings(**values)

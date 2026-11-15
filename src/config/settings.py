"""Reads and checks the PARLAI_* environment variables against the rules in rules.py."""

import math
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from config import rules


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


def _positive_int(
    env: Mapping[str, str], name: str, default: int, problems: list[str]
) -> int | None:
    """Return the setting as a positive int, or None (and record a problem) if it is not one."""
    raw = env.get(name) or str(default)
    try:
        value = int(raw)
    except ValueError:
        value = 0
    if value <= 0:
        problems.append(rules.NOT_A_POSITIVE_NUMBER.violation(name, raw))
        return None
    return value


def _gain(env: Mapping[str, str], name: str, problems: list[str]) -> float:
    """Return the setting as a positive finite float (default 1.0), or record a problem."""
    raw = (env.get(name) or "1.0").strip()
    try:
        value = float(raw)
    except ValueError:
        value = 0.0
    if not math.isfinite(value) or value <= 0:
        problems.append(rules.NOT_A_POSITIVE_GAIN.violation(name, raw))
        return 1.0
    return value


def _logger_names(raw: str | None) -> tuple[str, ...]:
    """A comma-separated list of logger names. Empty means the default list, "none" means none."""
    if raw is None or not raw.strip():
        return rules.DEFAULT_QUIET_LOGGERS
    if raw.strip().lower() == "none":
        return ()
    return tuple(name.strip() for name in raw.split(",") if name.strip())


def load_settings(env: Mapping[str, str]) -> Settings:
    """
    Build Settings from environment variables, using defaults for any that are missing or empty.

    If PARLAI_BLOCK_SIZE is not set, it follows the sample rate (256 at 8000 Hz, 512 at 16000 Hz).

    :param env: the variables to read, normally os.environ.
    :raises ConfigError: if any value is invalid; the message names every broken rule.
    """
    problems: list[str] = []

    sample_rate = _positive_int(env, "PARLAI_SAMPLE_RATE", rules.DEFAULT_SAMPLE_RATE, problems)
    sample_rate_ok = sample_rate in rules.ALLOWED_SAMPLE_RATES
    if sample_rate is not None and not sample_rate_ok:
        allowed = rules.join_with_or(rules.ALLOWED_SAMPLE_RATES)
        problems.append(
            rules.SAMPLE_RATE.violation("PARLAI_SAMPLE_RATE", sample_rate, allowed=allowed)
        )

    default_block_size = rules.BLOCK_SIZE_FOR_RATE.get(sample_rate, rules.DEFAULT_BLOCK_SIZE)
    block_size = _positive_int(env, "PARLAI_BLOCK_SIZE", default_block_size, problems)
    if block_size is not None and sample_rate_ok:
        required = rules.BLOCK_SIZE_FOR_RATE[sample_rate]
        if block_size != required:
            problems.append(
                rules.BLOCK_SIZE.violation(
                    "PARLAI_BLOCK_SIZE", block_size, required=required, rate=sample_rate
                )
            )

    channels = _positive_int(env, "PARLAI_CHANNELS", rules.DEFAULT_CHANNELS, problems)
    if channels is not None and channels not in rules.ALLOWED_CHANNELS:
        allowed = rules.join_with_or(rules.ALLOWED_CHANNELS)
        problems.append(rules.CHANNELS.violation("PARLAI_CHANNELS", channels, allowed=allowed))

    recordings_dir = Path(env.get("PARLAI_RECORDINGS_DIR") or "recordings")
    if recordings_dir.exists() and not recordings_dir.is_dir():
        problems.append(rules.NOT_A_FOLDER.violation("PARLAI_RECORDINGS_DIR", str(recordings_dir)))

    input_gain = _gain(env, "PARLAI_INPUT_GAIN", problems)
    playback_gain = _gain(env, "PARLAI_PLAYBACK_GAIN", problems)

    whisper_model = (env.get("PARLAI_WHISPER_MODEL") or rules.DEFAULT_WHISPER_MODEL).strip()
    whisper_device = (
        (env.get("PARLAI_WHISPER_DEVICE") or rules.DEFAULT_WHISPER_DEVICE).strip().lower()
    )
    if whisper_device not in rules.ALLOWED_WHISPER_DEVICES:
        allowed = rules.join_with_or(rules.ALLOWED_WHISPER_DEVICES)
        problems.append(
            rules.WHISPER_DEVICE.violation("PARLAI_WHISPER_DEVICE", whisper_device, allowed=allowed)
        )

    utterance_silence_ms = _positive_int(
        env, "PARLAI_UTTERANCE_SILENCE_MS", rules.DEFAULT_UTTERANCE_SILENCE_MS, problems
    )

    log_dir = Path(env.get("PARLAI_LOG_DIR") or "logs")
    if log_dir.exists() and not log_dir.is_dir():
        problems.append(rules.NOT_A_FOLDER.violation("PARLAI_LOG_DIR", str(log_dir)))
    log_level = (env.get("PARLAI_LOG_LEVEL") or rules.DEFAULT_LOG_LEVEL).strip().upper()
    if log_level not in rules.ALLOWED_LOG_LEVELS:
        allowed = rules.join_with_or(rules.ALLOWED_LOG_LEVELS)
        problems.append(rules.LOG_LEVEL.violation("PARLAI_LOG_LEVEL", log_level, allowed=allowed))
    log_max_mb = _positive_int(env, "PARLAI_LOG_MAX_MB", rules.DEFAULT_LOG_MAX_MB, problems)
    log_keep_days = _positive_int(
        env, "PARLAI_LOG_KEEP_DAYS", rules.DEFAULT_LOG_KEEP_DAYS, problems
    )
    console_level = (
        (env.get("PARLAI_LOG_CONSOLE_LEVEL") or rules.DEFAULT_LOG_CONSOLE_LEVEL).strip().upper()
    )
    if console_level not in rules.ALLOWED_CONSOLE_LEVELS:
        allowed = rules.join_with_or(rules.ALLOWED_CONSOLE_LEVELS)
        problems.append(
            rules.LOG_CONSOLE_LEVEL.violation(
                "PARLAI_LOG_CONSOLE_LEVEL", console_level, allowed=allowed
            )
        )

    log_name = (env.get("PARLAI_LOG_NAME") or rules.DEFAULT_LOG_NAME).strip()
    if not re.fullmatch(rules.LOG_NAME_PATTERN, log_name):
        problems.append(rules.LOG_NAME.violation("PARLAI_LOG_NAME", log_name))
    log_format = (env.get("PARLAI_LOG_FORMAT") or rules.DEFAULT_LOG_FORMAT).strip().lower()
    if log_format not in rules.ALLOWED_LOG_FORMATS:
        allowed = rules.join_with_or(rules.ALLOWED_LOG_FORMATS)
        problems.append(
            rules.LOG_FORMAT.violation("PARLAI_LOG_FORMAT", log_format, allowed=allowed)
        )
    log_quiet_loggers = _logger_names(env.get("PARLAI_LOG_QUIET_LOGGERS"))

    if problems:
        raise ConfigError("\n".join(problems))
    input_device = (env.get("PARLAI_INPUT_DEVICE") or "").strip() or None
    return Settings(
        sample_rate,
        block_size,
        channels,
        recordings_dir,
        input_device,
        input_gain,
        playback_gain,
        whisper_model,
        whisper_device,
        utterance_silence_ms,
        log_dir,
        log_level,
        log_max_mb,
        log_keep_days,
        console_level,
        log_name,
        log_format,
        log_quiet_loggers,
    )

"""Reads and checks the PARLAI_* environment variables against the rules in rules.py."""

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

    if problems:
        raise ConfigError("\n".join(problems))
    return Settings(sample_rate, block_size, channels, recordings_dir)

"""The audio settings: format, folder for recordings, microphone and volume."""

from collections.abc import Mapping
from typing import Any

from config import parsers, rules


def read_audio_settings(env: Mapping[str, str], problems: list[str]) -> dict[str, Any]:
    """If PARLAI_BLOCK_SIZE is not set, it follows the sample rate (512 at 16000 Hz)."""
    sample_rate = parsers.positive_int(
        env, "PARLAI_SAMPLE_RATE", rules.DEFAULT_SAMPLE_RATE, problems
    )
    sample_rate_ok = sample_rate in rules.ALLOWED_SAMPLE_RATES
    if sample_rate is not None and not sample_rate_ok:
        allowed = rules.join_with_or(rules.ALLOWED_SAMPLE_RATES)
        problems.append(
            rules.SAMPLE_RATE.violation("PARLAI_SAMPLE_RATE", sample_rate, allowed=allowed)
        )

    default_block_size = rules.BLOCK_SIZE_FOR_RATE.get(sample_rate, rules.DEFAULT_BLOCK_SIZE)
    block_size = parsers.positive_int(env, "PARLAI_BLOCK_SIZE", default_block_size, problems)
    if block_size is not None and sample_rate_ok:
        required = rules.BLOCK_SIZE_FOR_RATE[sample_rate]
        if block_size != required:
            problems.append(
                rules.BLOCK_SIZE.violation(
                    "PARLAI_BLOCK_SIZE", block_size, required=required, rate=sample_rate
                )
            )

    channels = parsers.positive_int(env, "PARLAI_CHANNELS", rules.DEFAULT_CHANNELS, problems)
    if channels is not None and channels not in rules.ALLOWED_CHANNELS:
        allowed = rules.join_with_or(rules.ALLOWED_CHANNELS)
        problems.append(rules.CHANNELS.violation("PARLAI_CHANNELS", channels, allowed=allowed))

    return {
        "sample_rate": sample_rate,
        "block_size": block_size,
        "channels": channels,
        "recordings_dir": parsers.folder(env, "PARLAI_RECORDINGS_DIR", "recordings", problems),
        "input_device": (env.get("PARLAI_INPUT_DEVICE") or "").strip() or None,
        "input_gain": parsers.gain(env, "PARLAI_INPUT_GAIN", problems),
        "playback_gain": parsers.gain(env, "PARLAI_PLAYBACK_GAIN", problems),
    }

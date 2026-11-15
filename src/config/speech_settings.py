"""The speech recognition settings: the Whisper model, where it runs, and utterance timing."""

from collections.abc import Mapping
from typing import Any

from config import parsers, rules


def read_speech_settings(env: Mapping[str, str], problems: list[str]) -> dict[str, Any]:
    return {
        "whisper_model": (env.get("PARLAI_WHISPER_MODEL") or rules.DEFAULT_WHISPER_MODEL).strip(),
        "whisper_device": parsers.choice(
            env,
            "PARLAI_WHISPER_DEVICE",
            rules.DEFAULT_WHISPER_DEVICE,
            rules.ALLOWED_WHISPER_DEVICES,
            rules.WHISPER_DEVICE,
            problems,
        ),
        "utterance_silence_ms": parsers.positive_int(
            env, "PARLAI_UTTERANCE_SILENCE_MS", rules.DEFAULT_UTTERANCE_SILENCE_MS, problems
        ),
        "utterance_max_ms": parsers.positive_int(
            env, "PARLAI_UTTERANCE_MAX_MS", rules.DEFAULT_UTTERANCE_MAX_MS, problems
        ),
        "partial_interval_ms": parsers.whole_number(
            env, "PARLAI_PARTIAL_INTERVAL_MS", rules.DEFAULT_PARTIAL_INTERVAL_MS, problems
        ),
        "partial_window_ms": parsers.positive_int(
            env, "PARLAI_PARTIAL_WINDOW_MS", rules.DEFAULT_PARTIAL_WINDOW_MS, problems
        ),
    }

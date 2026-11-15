"""Turns the millisecond settings into counts of microphone blocks (512 samples, 32 ms)."""

import math

from config.settings import Settings


def _block_ms(settings: Settings) -> float:
    return 1000 * settings.block_size / settings.sample_rate


def silence_blocks(settings: Settings) -> int:
    """How many silent blocks in a row end an utterance, rounded up so it is never shorter."""
    return max(1, math.ceil(settings.utterance_silence_ms / _block_ms(settings)))


def partial_interval_blocks(settings: Settings) -> int:
    """How many blocks pass between partial texts. 0 means partials are off."""
    if settings.partial_interval_ms == 0:
        return 0
    return max(1, round(settings.partial_interval_ms / _block_ms(settings)))


def partial_window_blocks(settings: Settings) -> int:
    """How many of the latest blocks a partial text covers, rounded down."""
    return max(1, int(settings.partial_window_ms / _block_ms(settings)))


def utterance_max_blocks(settings: Settings) -> int:
    """How many blocks one utterance may have, rounded down so it is never longer."""
    return max(1, int(settings.utterance_max_ms / _block_ms(settings)))

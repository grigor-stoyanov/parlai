import array
import math

import pytest

from speech_to_text.voice_activity_detection import BLOCK_SAMPLES, Vad


def tone_block(offset=0):
    samples = (
        int(8000 * math.sin(2 * math.pi * 440 * (offset + i) / 16000)) for i in range(BLOCK_SAMPLES)
    )
    return array.array("h", samples).tobytes()


def test_silence_is_not_speech():
    vad = Vad()

    assert not any(vad.is_speech(bytes(BLOCK_SAMPLES * 2)) for _ in range(10))


def test_a_plain_tone_is_not_speech():
    vad = Vad()

    assert not any(vad.is_speech(tone_block(i * BLOCK_SAMPLES)) for i in range(10))


@pytest.mark.parametrize("samples", [0, 256, 511, 513, 1024])
def test_blocks_of_the_wrong_size_are_rejected(samples):
    with pytest.raises(ValueError, match="512"):
        Vad().is_speech(bytes(samples * 2))

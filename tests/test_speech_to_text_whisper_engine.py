import array

import numpy as np
import pytest

from speech_to_text.whisper_engine import audio_to_samples, join_segments


def audio(*values):
    return array.array("h", values).tobytes()


def test_samples_are_scaled_to_between_minus_one_and_one():
    samples = audio_to_samples(audio(0, 16384, -16384, 32767, -32768))

    assert samples.tolist() == pytest.approx([0.0, 0.5, -0.5, 32767 / 32768, -1.0])


def test_samples_are_32_bit_floats_as_whisper_expects():
    assert audio_to_samples(audio(1, 2, 3)).dtype == np.float32


def test_no_audio_gives_no_samples():
    assert len(audio_to_samples(b"")) == 0


def test_segments_are_joined_with_single_spaces():
    assert join_segments([" Hello there.", " How are you?"]) == "Hello there. How are you?"


def test_stray_spaces_around_the_text_are_removed():
    assert join_segments(["  hi  "]) == "hi"


def test_no_segments_give_empty_text():
    assert join_segments([]) == ""

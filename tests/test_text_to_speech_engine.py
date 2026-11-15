from config.settings import load_settings
from text_to_speech.tts_engine import TTSEngine


def test_mock_audio_is_longer_for_more_words():
    engine = TTSEngine(load_settings({}))

    assert len(engine.synthesize("one two three four")) > len(engine.synthesize("one"))


def test_mock_audio_is_whole_16_bit_samples():
    assert len(TTSEngine(load_settings({})).synthesize("hello there")) % 2 == 0

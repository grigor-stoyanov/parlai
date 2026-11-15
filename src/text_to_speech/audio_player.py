"""Speaks text, or plays audio, through the speaker."""

from config.settings import Settings
from sound_utils.speaker import Speaker
from text_to_speech.tts_engine import TTSEngine


class AudioPlayer(Speaker):
    def __init__(self, settings: Settings) -> None:
        super().__init__(settings)
        self.engine = TTSEngine(settings)

    def speak(self, text: str) -> None:
        self.play(self.engine.synthesize(text))

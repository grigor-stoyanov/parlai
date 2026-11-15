"""Listens on the microphone and turns speech into text."""

from config.settings import Settings
from sound_utils.microphone import Microphone
from speech_to_text.whisper_engine import WhisperEngine


class SpeechRecognizer(Microphone):
    def __init__(self, settings: Settings) -> None:
        super().__init__(settings)
        self.engine = WhisperEngine()

    def listen(self, seconds: float) -> str:
        return self.engine.transcribe(self.record(seconds))

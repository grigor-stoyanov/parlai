"""Mock speech recognition: stands in for faster-whisper until M1."""


class WhisperEngine:
    def transcribe(self, audio: bytes) -> str:
        return "hello this is mocked speech"

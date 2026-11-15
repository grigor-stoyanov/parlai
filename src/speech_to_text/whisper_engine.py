"""Speech recognition with faster-whisper, on the GPU if one works, else the CPU."""

import logging

import numpy as np
from faster_whisper import WhisperModel

from config.settings import Settings

logger = logging.getLogger(__name__)

SAMPLE_RATE = 16000
INT16_SCALE = 32768.0
COMPUTE_TYPES = {"cuda": "float16", "cpu": "int8"}


def audio_to_samples(audio: bytes) -> np.ndarray:
    """Raw 16-bit mic audio as the floats between -1 and 1 that Whisper takes."""
    return np.frombuffer(audio, dtype=np.int16).astype(np.float32) / INT16_SCALE


def join_segments(texts: list[str]) -> str:
    """Whisper returns one text per segment, each with stray spaces. Make it one sentence."""
    return " ".join(text.strip() for text in texts).strip()


class WhisperEngine:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.model: WhisperModel | None = None

    def load(self) -> None:
        """Load the model, downloading it first if it is not in the cache. Slow, so do it early."""
        if self.model is not None:
            return
        devices = (
            ["cuda", "cpu"]
            if self.settings.whisper_device == "auto"
            else [self.settings.whisper_device]
        )
        for device in devices:
            try:
                self.model = self._load_on(device)
                logger.info("Whisper model %s loaded on %s", self.settings.whisper_model, device)
                return
            except (RuntimeError, ValueError) as error:
                if device == devices[-1]:
                    raise
                logger.warning("Whisper can't use the %s (%s), trying the CPU", device, error)

    def _load_on(self, device: str) -> WhisperModel:
        model = WhisperModel(
            self.settings.whisper_model, device=device, compute_type=COMPUTE_TYPES[device]
        )
        # The GPU libraries are only loaded on the first real run, so a model that "loaded"
        # can still fail. Run one second of silence now so that failure happens here.
        segments, _ = model.transcribe(np.zeros(SAMPLE_RATE, dtype=np.float32))
        list(segments)
        return model

    def transcribe(self, audio: bytes) -> str:
        self.load()
        # Our VAD already cut the audio to one utterance, so Whisper's own VAD stays off.
        segments, _ = self.model.transcribe(
            audio_to_samples(audio), vad_filter=False, condition_on_previous_text=False
        )
        return join_segments([segment.text for segment in segments])

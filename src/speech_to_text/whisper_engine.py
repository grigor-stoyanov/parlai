"""Speech recognition with faster-whisper, on the GPU if one works, else the CPU."""

import logging
import time
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel
from faster_whisper.utils import download_model

from config.settings import Settings
from event_logger.json_log import log_event

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
        path = self._find_model()
        devices = (
            ["cuda", "cpu"]
            if self.settings.whisper_device == "auto"
            else [self.settings.whisper_device]
        )
        for device in devices:
            started = time.monotonic()
            try:
                self.model = self._load_on(path, device)
            except (RuntimeError, ValueError) as error:
                if device == devices[-1]:
                    raise
                log_event(
                    logger,
                    logging.WARNING,
                    "model_device",
                    f"model can't run on the {device}, trying the CPU",
                    device=device,
                    reason=str(error),
                )
                continue
            log_event(
                logger,
                logging.INFO,
                "model",
                "model loaded",
                model=self.settings.whisper_model,
                device=device,
                compute_type=COMPUTE_TYPES[device],
                seconds=round(time.monotonic() - started, 1),
            )
            return

    def _find_model(self) -> str:
        """Where the model files are: a folder the user gave, the cache, or a fresh download."""
        name = self.settings.whisper_model
        if Path(name).is_dir():
            log_event(logger, logging.INFO, "model", "using model folder", path=name)
            return name
        try:
            path = download_model(name, local_files_only=True)
            log_event(logger, logging.INFO, "model", "using cached model", model=name, path=path)
        except FileNotFoundError:
            log_event(
                logger,
                logging.INFO,
                "model",
                "model not in cache, downloading (first run, needs internet)",
                model=name,
            )
            started = time.monotonic()
            path = download_model(name)
            log_event(
                logger,
                logging.INFO,
                "model",
                "model downloaded",
                model=name,
                path=path,
                seconds=round(time.monotonic() - started, 1),
            )
        return path

    def _load_on(self, path: str, device: str) -> WhisperModel:
        model = WhisperModel(path, device=device, compute_type=COMPUTE_TYPES[device])
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

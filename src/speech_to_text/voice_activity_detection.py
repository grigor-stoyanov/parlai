"""Voice activity detection: says whether a block of mic audio contains speech."""

import logging
import os

import numpy as np
import onnxruntime
from faster_whisper.utils import get_assets_path

from event_logger.json_log import log_event

BLOCK_SAMPLES = 512
CONTEXT_SAMPLES = 64
INT16_SCALE = 32768.0

logger = logging.getLogger(__name__)


class Vad:
    """
    Silero VAD on the model file that ships with faster-whisper, run one block at a time.

    The model is a small recurrent network: it remembers the previous blocks, so blocks must be
    fed in order. faster-whisper's own wrapper resets that memory on every call, which is why
    we keep our own. It only supports 512-sample blocks at 16 kHz.
    """

    def __init__(self, threshold: float = 0.5) -> None:
        path = os.path.join(get_assets_path(), "silero_vad_v6.onnx")
        options = onnxruntime.SessionOptions()
        options.inter_op_num_threads = 1
        options.intra_op_num_threads = 1
        options.log_severity_level = 4
        self.session = onnxruntime.InferenceSession(
            path, providers=["CPUExecutionProvider"], sess_options=options
        )
        self.threshold = threshold
        log_event(
            logger,
            logging.INFO,
            "vad",
            "voice activity detector ready",
            model=path,
            threshold=threshold,
        )
        self.h = np.zeros((1, 1, 128), dtype=np.float32)
        self.c = np.zeros((1, 1, 128), dtype=np.float32)
        # The model also looks at the last 64 samples of the previous block.
        self.context = np.zeros(CONTEXT_SAMPLES, dtype=np.float32)

    def is_speech(self, block: bytes) -> bool:
        """
        :param block: 512 raw 16-bit samples (16 kHz, mono) from the microphone.
        :raises ValueError: if the block is not exactly 512 samples.
        """
        samples = np.frombuffer(block, dtype=np.int16).astype(np.float32) / INT16_SCALE
        if len(samples) != BLOCK_SAMPLES:
            raise ValueError(f"Vad needs {BLOCK_SAMPLES}-sample blocks, got {len(samples)}")
        window = np.concatenate([self.context, samples])[np.newaxis, :]
        probability, self.h, self.c = self.session.run(
            None, {"input": window, "h": self.h, "c": self.c}
        )
        self.context = samples[-CONTEXT_SAMPLES:]
        return float(probability.ravel()[0]) >= self.threshold

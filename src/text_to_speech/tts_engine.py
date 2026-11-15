"""Mock speech synthesis: stands in for Kokoro or Piper until M6."""

import array
import math

from config.settings import Settings

TONE_HZ = 440
SECONDS_PER_WORD = 0.25
VOLUME = 8000


class TTSEngine:
    def __init__(self, settings: Settings) -> None:
        self.sample_rate = settings.sample_rate

    def synthesize(self, text: str) -> bytes:
        seconds = SECONDS_PER_WORD * len(text.split())
        count = int(seconds * self.sample_rate)
        samples = array.array(
            "h",
            (
                int(VOLUME * math.sin(2 * math.pi * TONE_HZ * i / self.sample_rate))
                for i in range(count)
            ),
        )
        return samples.tobytes()

"""Volume maths on raw 16-bit audio bytes: no hardware, no sounddevice."""

import array
import math

INT16_MIN, INT16_MAX = -32768, 32767
SILENCE_DBFS = -96.0  # floor for silent audio; log10(0) would be -infinity


class AudioLevels:
    """Mixin giving every audio device gain and level measuring. Holds no state."""

    @staticmethod
    def apply_gain(audio: bytes, gain: float) -> bytes:
        """
        Multiply raw 16-bit samples by gain.

        Results are clipped to the int16 range: without that, a loud sample would wrap around
        to the opposite sign and sound like a crack instead of just being loud.
        """
        if gain == 1.0:
            return audio
        samples = array.array("h", audio)  # "h" = signed 16-bit, native byte order
        for i, sample in enumerate(samples):
            samples[i] = max(INT16_MIN, min(INT16_MAX, round(sample * gain)))
        return samples.tobytes()

    @staticmethod
    def measure_levels(audio: bytes) -> tuple[float, float]:
        """
        Measure raw 16-bit audio as (peak, rms) in dBFS, where 0 is the loudest possible sample.

        Peak near 0 means clipping risk; RMS is the average loudness, which is what we hear.
        """
        samples = array.array("h", audio)
        if not samples:
            return SILENCE_DBFS, SILENCE_DBFS
        peak = max(abs(sample) for sample in samples)
        rms = math.sqrt(sum(sample * sample for sample in samples) / len(samples))
        return AudioLevels._to_dbfs(peak), AudioLevels._to_dbfs(rms)

    @staticmethod
    def _to_dbfs(level: float) -> float:
        if level < 1:
            return SILENCE_DBFS
        return max(SILENCE_DBFS, 20 * math.log10(level / INT16_MAX))

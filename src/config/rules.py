"""The rules every setting must follow, each with a code and a description.

The code and description end up in the error message, so someone who sets a wrong
value sees which rule they broke and why it exists.
"""

from dataclasses import dataclass

DEFAULT_SAMPLE_RATE = 16000
DEFAULT_BLOCK_SIZE = 512
DEFAULT_CHANNELS = 1
DEFAULT_UTTERANCE_SILENCE_MS = 500
DEFAULT_WHISPER_MODEL = "small.en"
DEFAULT_WHISPER_DEVICE = "auto"

ALLOWED_SAMPLE_RATES = (8000, 16000)
BLOCK_SIZE_FOR_RATE = {8000: 256, 16000: 512}
ALLOWED_CHANNELS = (1,)
ALLOWED_WHISPER_DEVICES = ("auto", "cuda", "cpu")


@dataclass(frozen=True)
class Rule:
    code: str
    description: str

    def violation(self, name: str, got: object, **details: object) -> str:
        """Build the error message for a value that breaks this rule."""
        return f"{self.code} {name} {self.description.format(**details)}, got {got!r}"


NOT_A_POSITIVE_NUMBER = Rule("PARLAI-E001", "must be a positive whole number")
NOT_A_POSITIVE_GAIN = Rule(
    "PARLAI-E003", "must be a positive number (1.0 leaves the volume unchanged)"
)
NOT_A_FOLDER = Rule("PARLAI-E002", "must be a folder, not a file")
SAMPLE_RATE = Rule(
    "PARLAI-E101",
    "must be {allowed}: the only rates silero-vad accepts, and standard for audio drivers",
)
BLOCK_SIZE = Rule(
    "PARLAI-E102",
    "must be {required} at {rate} Hz: the exact block size silero-vad takes at that rate",
)
CHANNELS = Rule(
    "PARLAI-E103",
    "must be {allowed}: Whisper and the VAD both expect a single (mono) channel",
)

WHISPER_DEVICE = Rule(
    "PARLAI-E201",
    "must be {allowed}: auto uses the GPU if one works, else the CPU",
)


def join_with_or(values: tuple[int | str, ...]) -> str:
    """Format allowed values for a message, for example '8000 or 16000'."""
    return " or ".join(str(value) for value in values)

"""Keeps the audio of the utterance being spoken, plus a little from just before it."""

from collections import deque

# Blocks of audio kept from just before speech starts (about 0.3 s), because the VAD needs a
# moment to notice speech and the first syllable would otherwise be cut off.
PRE_ROLL_BLOCKS = 10


class UtteranceBuffer:
    def __init__(self) -> None:
        self.pre_roll: deque[bytes] = deque(maxlen=PRE_ROLL_BLOCKS)
        self.blocks: list[bytes] | None = None  # None while nobody is speaking

    @property
    def active(self) -> bool:
        """True while an utterance is in progress."""
        return self.blocks is not None

    def recent(self, count: int) -> bytes:
        """The audio of the last `count` blocks of the utterance in progress."""
        return b"".join(self.blocks[-count:])

    def add(self, block: bytes, started: bool, ended: bool) -> bytes | None:
        """
        Take the next microphone block.

        :param started: the segmenter says an utterance began with this block.
        :param ended: the segmenter says an utterance ended with this block.
        :return: the whole utterance's audio if it just ended, otherwise None.
        """
        # Started and ended in the same block means the length limit cut a long utterance and
        # the speaker is still talking: this block closes the old one and opens the next.
        if started and not ended:
            self.blocks = list(self.pre_roll)
        if self.blocks is None:
            self.pre_roll.append(block)
            return None
        self.blocks.append(block)
        if not ended:
            return None

        audio = b"".join(self.blocks)
        # After a cut the next utterance starts with the last 0.3 s of this one as pre-roll,
        # so the word at the seam is not chopped in half (it may appear twice).
        self.blocks = self.blocks[-PRE_ROLL_BLOCKS:] if started else None
        self.pre_roll.clear()
        return audio

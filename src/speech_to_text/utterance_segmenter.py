"""Turns a stream of speech/silence flags into SpeechStart and SpeechEnd events."""

from event_bus.bus import EventBus
from event_bus.events import SpeechEnd, SpeechStart


class UtteranceSegmenter:
    def __init__(
        self, bus: EventBus, silence_chunks_to_end: int = 3, max_chunks: int | None = None
    ) -> None:
        """
        :param bus: the event bus that SpeechStart and SpeechEnd are published to.
        :param silence_chunks_to_end: how many silent chunks in a row end an utterance.
        :param max_chunks: the most chunks one utterance may have (None = no limit). Reaching
            it ends the utterance, and if the speaker is still talking a new one starts at once.
        """
        self.bus = bus
        self.silence_chunks_to_end = silence_chunks_to_end
        self.max_chunks = max_chunks
        self.speaking = False
        self.silent_chunks = 0
        self.chunks = 0

    def feed(self, is_speech: bool) -> None:
        """
        Give the segmenter the next chunk's verdict.

        :param is_speech: True if the chunk contains speech, False if it is silence.
        :return: nothing; events are published on the bus instead.
        """
        if is_speech:
            self.silent_chunks = 0
            if not self.speaking:
                self._start()
        elif self.speaking:
            self.silent_chunks += 1
            if self.silent_chunks == self.silence_chunks_to_end:
                self._end()

        if self.speaking:
            self.chunks += 1
            if self.max_chunks is not None and self.chunks >= self.max_chunks:
                # Too long: finish it now. Only carry on if this very chunk is speech; if it is
                # a pause there is nothing to carry on with, and the next speech starts afresh.
                self._end()
                if is_speech:
                    self._start()

    def _start(self) -> None:
        self.speaking = True
        self.chunks = 0
        self.bus.publish(SpeechStart())

    def _end(self) -> None:
        self.speaking = False
        self.silent_chunks = 0
        self.bus.publish(SpeechEnd())

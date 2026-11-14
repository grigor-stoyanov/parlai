"""Turns a stream of speech/silence flags into SpeechStart and SpeechEnd events."""

from event_bus.bus import EventBus
from event_bus.events import SpeechEnd, SpeechStart


class UtteranceSegmenter:
    def __init__(self, bus: EventBus, silence_chunks_to_end: int = 3) -> None:
        """
        :param bus: the event bus that SpeechStart and SpeechEnd are published to.
        :param silence_chunks_to_end: how many silent chunks in a row end an utterance.
        """
        self.bus = bus
        self.silence_chunks_to_end = silence_chunks_to_end
        self.speaking = False
        self.silent_chunks = 0

    def feed(self, is_speech: bool) -> None:
        """
        Give the segmenter the next chunk's verdict.

        :param is_speech: True if the chunk contains speech, False if it is silence.
        :return: nothing; events are published on the bus instead.
        """
        if is_speech:
            self.silent_chunks = 0
            if not self.speaking:
                self.speaking = True
                self.bus.publish(SpeechStart())
        elif self.speaking:
            self.silent_chunks += 1
            if self.silent_chunks == self.silence_chunks_to_end:
                self.speaking = False
                self.silent_chunks = 0
                self.bus.publish(SpeechEnd())

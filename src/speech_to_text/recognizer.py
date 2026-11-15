"""Listens on the microphone and turns speech into text."""

import queue
from collections import deque

from config.settings import Settings
from event_bus.bus import EventBus
from event_bus.events import FinalText, SpeechEnd, SpeechStart
from sound_utils.microphone import Microphone
from speech_to_text.utterance_segmenter import UtteranceSegmenter
from speech_to_text.voice_activity_detection import Vad
from speech_to_text.whisper_engine import WhisperEngine

# Blocks of audio kept from just before speech starts (about 0.3 s), because the VAD needs a
# moment to notice speech and the first syllable would otherwise be cut off.
PRE_ROLL_BLOCKS = 10


class SpeechRecognizer(Microphone):
    def __init__(
        self,
        settings: Settings,
        bus: EventBus | None = None,
        vad: Vad | None = None,
        engine: WhisperEngine | None = None,
    ) -> None:
        super().__init__(settings)
        self.bus = bus or EventBus()
        self.vad = vad or Vad()
        self.engine = engine or WhisperEngine()
        self.segmenter = UtteranceSegmenter(self.bus)
        self.starts = self.bus.subscribe(SpeechStart)
        self.ends = self.bus.subscribe(SpeechEnd)
        self.pre_roll: deque[bytes] = deque(maxlen=PRE_ROLL_BLOCKS)
        self.utterance: list[bytes] | None = None

    def process(self, block: bytes) -> None:
        """Take the next microphone block. Publishes FinalText when an utterance has ended."""
        self.segmenter.feed(self.vad.is_speech(block))
        started = self._drain(self.starts)
        ended = self._drain(self.ends)

        if started:
            self.utterance = list(self.pre_roll)
        if self.utterance is None:
            self.pre_roll.append(block)
        else:
            self.utterance.append(block)

        if ended:
            text = self.engine.transcribe(b"".join(self.utterance))
            self.bus.publish(FinalText(text))
            self.utterance = None
            self.pre_roll.clear()

    def listen(self, seconds: float) -> str:
        return self.engine.transcribe(self.record(seconds))

    @staticmethod
    def _drain(inbox: queue.Queue) -> bool:
        """Empty the inbox and say whether anything was in it."""
        found = not inbox.empty()
        while not inbox.empty():
            inbox.get_nowait()
        return found

"""Listens on the microphone and turns speech into text."""

import queue

from config.settings import Settings
from event_bus.bus import EventBus
from event_bus.events import FinalText, PartialText, SpeechEnd, SpeechStart
from sound_utils.microphone import Microphone
from speech_to_text.block_timing import (
    partial_interval_blocks,
    partial_window_blocks,
    silence_blocks,
    utterance_max_blocks,
)
from speech_to_text.transcription_worker import TranscriptionWorker
from speech_to_text.utterance_buffer import UtteranceBuffer
from speech_to_text.utterance_segmenter import UtteranceSegmenter
from speech_to_text.voice_activity_detection import Vad
from speech_to_text.whisper_engine import WhisperEngine


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
        self.engine = engine or WhisperEngine(settings)
        self.segmenter = UtteranceSegmenter(
            self.bus, silence_blocks(settings), utterance_max_blocks(settings)
        )
        self.starts = self.bus.subscribe(SpeechStart)
        self.ends = self.bus.subscribe(SpeechEnd)
        self.buffer = UtteranceBuffer()
        self.partial_every = partial_interval_blocks(settings)  # 0 = no partials
        self.partial_window = partial_window_blocks(settings)
        self.blocks_since_partial = 0
        self.worker = TranscriptionWorker(
            self.engine,
            on_final=lambda text: self.bus.publish(FinalText(text)),
            on_partial=self._publish_partial,
        )

    def _publish_partial(self, text: str) -> None:
        if text:  # noise often gives an empty text, which would only blank the display
            self.bus.publish(PartialText(text))

    def prepare(self) -> None:
        """Load the speech model now (downloads it the first time) so listening starts fast."""
        self.engine.load()

    def start(self) -> None:
        """Start the transcription thread. Call before process(), and stop() when done."""
        self.worker.start()

    def stop(self) -> None:
        """Finish transcribing what was already heard, then stop the thread."""
        self.worker.stop()

    def process(self, block: bytes) -> None:
        """
        Take the next microphone block. When an utterance has ended it is handed to the worker
        thread; FinalText is published from there a moment later, so this never waits for Whisper.
        """
        self.segmenter.feed(self.vad.is_speech(block))
        started = self._drain(self.starts)
        ended = self._drain(self.ends)
        audio = self.buffer.add(block, started, ended)
        if audio is not None:
            self.worker.submit_final(audio)
            self.blocks_since_partial = 0
        else:
            self._send_partial_when_due()

    def _send_partial_when_due(self) -> None:
        """While someone is speaking, ask for a live text every so many blocks."""
        if not self.partial_every or not self.buffer.active:
            self.blocks_since_partial = 0
            return
        self.blocks_since_partial += 1
        if self.blocks_since_partial >= self.partial_every:
            self.blocks_since_partial = 0
            self.worker.submit_partial(self.buffer.recent(self.partial_window))

    def listen(self, seconds: float) -> str:
        return self.engine.transcribe(self.record(seconds))

    @staticmethod
    def _drain(inbox: queue.Queue) -> bool:
        """Empty the inbox and say whether anything was in it."""
        found = not inbox.empty()
        while not inbox.empty():
            inbox.get_nowait()
        return found

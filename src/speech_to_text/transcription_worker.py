"""Runs Whisper on its own thread, so the microphone loop never waits for it."""

import logging
import threading
from collections.abc import Callable

from speech_to_text.job_queues import FINAL, JobQueues
from speech_to_text.whisper_engine import WhisperEngine

logger = logging.getLogger(__name__)


class TranscriptionWorker:
    def __init__(
        self,
        engine: WhisperEngine,
        on_final: Callable[[str], None],
        on_partial: Callable[[str], None],
    ) -> None:
        """
        :param engine: transcribes audio. Only this worker's thread calls it once started.
        :param on_final: called on the worker thread with the text of each final job, in order.
        :param on_partial: called on the worker thread with the text of a partial job.
        """
        self.engine = engine
        self.on_final = on_final
        self.on_partial = on_partial
        self.jobs = JobQueues()
        self.thread: threading.Thread | None = None

    def start(self) -> None:
        # A daemon thread, so a crash in the main loop can never hang the exit on this one.
        self.thread = threading.Thread(target=self._run, name="transcription", daemon=True)
        self.thread.start()

    def submit_final(self, audio: bytes) -> None:
        """Queue a finished utterance and return at once. It also cancels a waiting partial."""
        self.jobs.add_final(audio)

    def submit_partial(self, audio: bytes) -> None:
        """Queue audio for a live partial and return at once, replacing one still waiting."""
        self.jobs.add_partial(audio)

    def stop(self) -> None:
        """Finish every final already submitted, then end the thread. A waiting partial is dropped."""
        if self.thread is None:
            return
        self.jobs.add_stop()
        self.thread.join()
        self.thread = None

    def _run(self) -> None:
        while (job := self.jobs.next()) is not None:
            kind, audio = job
            self._transcribe(audio, self.on_final if kind == FINAL else self.on_partial)

    def _transcribe(self, audio: bytes, deliver: Callable[[str], None]) -> None:
        try:
            deliver(self.engine.transcribe(audio))
        except Exception:
            # One bad job must not kill the thread: the next utterance should still work.
            # The audio and any text stay out of the log.
            logger.exception(
                "transcription failed",
                extra={"label": "error", "fields": {"audio_bytes": len(audio)}},
            )

"""The two queues of transcription jobs, and the rules for which job comes next.

- finals: the audio of a finished utterance. Never dropped, handled in order, and always
  before any partial.
- partials: a quick look at an utterance still in progress, for live text. Only the newest is
  kept, because an older one is already out of date.
"""

import queue
import threading

FINAL = "final"
PARTIAL = "partial"

# Queued behind the finals by add_stop(), so every final submitted before it is handled first.
_STOP = None


class JobQueues:
    def __init__(self) -> None:
        self.finals: queue.Queue[bytes | None] = queue.Queue()
        # Room for one job: add_partial swaps a waiting one for the newer one.
        self.partials: queue.Queue[bytes] = queue.Queue(maxsize=1)
        # Set whenever a job is added. A thread can only block on one thing, so next() sleeps
        # on this instead of on the two queues.
        self.has_work = threading.Event()

    def add_final(self, audio: bytes) -> None:
        self._drop_waiting_partial()  # the final text replaces it, so it would only be stale
        self.finals.put(audio)
        self.has_work.set()

    def add_partial(self, audio: bytes) -> None:
        self._drop_waiting_partial()
        # Only one thread adds partials and the slot was just emptied, so this always fits.
        self.partials.put_nowait(audio)
        self.has_work.set()

    def add_stop(self) -> None:
        self.finals.put(_STOP)
        self.has_work.set()

    def next(self) -> tuple[str, bytes] | None:
        """
        Wait for the next job.

        :return: ("final" or "partial", audio), or None once the stop marker is reached.
            A partial still waiting at that point is dropped.
        """
        while True:
            try:
                audio = self.finals.get_nowait()
            except queue.Empty:
                pass
            else:
                return None if audio is _STOP else (FINAL, audio)
            try:
                return (PARTIAL, self.partials.get_nowait())
            except queue.Empty:
                pass
            # Nothing left. Clear after waking and before looking again: a job added from now
            # on sets the event again, so none can arrive unnoticed.
            self.has_work.wait()
            self.has_work.clear()

    def _drop_waiting_partial(self) -> None:
        try:
            self.partials.get_nowait()
        except queue.Empty:
            pass

"""Writes every event on the bus to the log, from its own thread so a slow disk never delays audio."""

import logging
import queue
import threading
from dataclasses import asdict, is_dataclass

from event_bus.bus import EventBus
from event_logger.json_log import log_event

logger = logging.getLogger("parlai.events")


class EventLogger:
    def __init__(self, bus: EventBus, include_text: bool = False) -> None:
        """
        :param include_text: also log transcripts. Off unless the log level is DEBUG, because
            what people say is private.
        """
        self.include_text = include_text
        self.inbox = bus.subscribe_all()
        self._stopping = threading.Event()
        self._thread = threading.Thread(target=self._run, name="event-logger", daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        """Stop the thread, then write whatever is still waiting so the last events are not lost."""
        self._stopping.set()
        self._thread.join(timeout=2)
        while not self.inbox.empty():
            self.log(self.inbox.get_nowait())

    def log(self, event: object) -> None:
        fields = asdict(event) if is_dataclass(event) else {"value": repr(event)}
        # Transcripts are private: only their length is logged unless include_text is on.
        if "text" in fields:
            text = fields.pop("text")
            fields["chars"] = len(text)
            if self.include_text:
                fields["text"] = text
        log_event(logger, logging.INFO, type(event).__name__, "event published", **fields)

    def _run(self) -> None:
        while not self._stopping.is_set():
            try:
                self.log(self.inbox.get(timeout=0.2))
            except queue.Empty:
                pass

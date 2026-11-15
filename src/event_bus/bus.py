"""A tiny publish/subscribe bus. Parts of the app talk through it, not to each other.

Inboxes are queue.Queue, which is thread-safe, so any thread (mic, recogniser, server)
can publish, and any thread can read its inbox.
"""

import queue
from collections import defaultdict


class EventBus:
    def __init__(self) -> None:
        # event type -> the inboxes of everyone who subscribed to that type
        self._inboxes: dict[type, list[queue.Queue]] = defaultdict(list)
        # inboxes that get every event, whatever its type (used by the event logger)
        self._everything: list[queue.Queue] = []

    def subscribe(self, event_type: type) -> queue.Queue:
        """Return an inbox that receives every future event of this type."""
        inbox: queue.Queue = queue.Queue()
        self._inboxes[event_type].append(inbox)
        return inbox

    def subscribe_all(self) -> queue.Queue:
        """Return an inbox that receives every future event, of any type."""
        inbox: queue.Queue = queue.Queue()
        self._everything.append(inbox)
        return inbox

    def publish(self, event: object) -> None:
        """Put the event in the inbox of every subscriber of its type, and of every subscribe_all."""
        for inbox in [*self._inboxes[type(event)], *self._everything]:
            inbox.put(event)

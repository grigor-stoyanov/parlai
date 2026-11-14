"""Main loop: wires the packages in src/ together.

Run with `uv run python main.py` (or the project's .venv interpreter in PyCharm).
"""

import argparse
import queue
import time

from event_bus.bus import EventBus
from event_bus.events import SpeechEnd, SpeechStart
from speech_to_text.utterance_segmenter import UtteranceSegmenter

MOCK_AUDIO = "..SSS..SS......SS....IMASNAKE"


def print_events(*inboxes: queue.Queue) -> None:
    for inbox in inboxes:
        while not inbox.empty():
            print(f"   -> {inbox.get_nowait()}")


def main(argv: list[str] | None = None, pause: float = 0.5) -> None:
    # argv is injectable so tests don't parse pytest's own command-line flags.
    parser = argparse.ArgumentParser(prog="parlai", description="Talk to AI with your voice.")
    parser.parse_args(argv)

    bus = EventBus()
    starts = bus.subscribe(SpeechStart)
    ends = bus.subscribe(SpeechEnd)
    segmenter = UtteranceSegmenter(bus)

    for i, chunk in enumerate(MOCK_AUDIO):
        segmenter.feed(chunk == "S")
        print(f"{i:2} {chunk}")
        print_events(starts, ends)
        time.sleep(pause)


if __name__ == "__main__":
    main()

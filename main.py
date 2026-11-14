"""Main loop: wires the packages in src/ together.

Run with `uv run python main.py` (or the project's .venv interpreter in PyCharm).
"""

import argparse
import queue
import time

from event_bus.bus import EventBus
from event_bus.events import FinalText, PartialText


def drain(name: str, inbox: queue.Queue) -> None:
    """Print everything currently waiting in an inbox."""
    while not inbox.empty():
        print(f"{name} got: {inbox.get_nowait()}")


def main(argv: list[str] | None = None, pause: float = 0.5) -> None:
    # argv is injectable so tests don't parse pytest's own command-line flags.
    parser = argparse.ArgumentParser(prog="parlai", description="Talk to AI with your voice.")
    parser.parse_args(argv)

    bus = EventBus()

    terminal = bus.subscribe(FinalText)
    browser = bus.subscribe(PartialText)

    for text in ["Hel", "Hello", "Hello wor"]:
        print(f"published PartialText({text!r})")
        bus.publish(PartialText(text))
        time.sleep(pause)
    print("published FinalText('Hello world')")
    bus.publish(FinalText("Hello world"))
    time.sleep(pause)

    print("--- subscribers start reading ---")
    drain("browser", browser)
    drain("terminal", terminal)


if __name__ == "__main__":
    main()

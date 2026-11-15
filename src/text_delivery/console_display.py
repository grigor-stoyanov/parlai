"""Shows recognised text on this terminal: one line that is redrawn while you speak.

Live text (PartialText) is drawn over the same line again and again, then the final text
replaces it and the line is kept. Only "\\r" and spaces are used, no ANSI codes, so it also
works in older Windows consoles.
"""

import shutil
import sys
from collections.abc import Callable
from typing import TextIO

from event_bus.events import FinalText, PartialText


class ConsoleDisplay:
    def __init__(self, out: TextIO = sys.stdout, width: Callable[[], int] | None = None) -> None:
        """
        :param out: where to write, normally the terminal.
        :param width: the terminal's width in characters, looked up on every draw so a resized
            window is respected.
        """
        self.out = out
        self.width = width or (lambda: shutil.get_terminal_size().columns)
        self.shown = 0  # characters now on the live line, so a shorter text can cover them

    def handle(self, event: object) -> None:
        """Show an event if it is text. Anything else (speech start, end...) is ignored."""
        if isinstance(event, PartialText):
            self.show_partial(event.text)
        elif isinstance(event, FinalText):
            self.show_final(event.text)

    def show_partial(self, text: str) -> None:
        """Draw live text on the current line, cut to its last words if it would not fit."""
        self._redraw(self._fit(text))

    def show_final(self, text: str) -> None:
        """Replace the live line with the final text and move on to a new line."""
        if not text.strip():
            self._redraw("")  # nothing was recognised: just clear the live line
            return
        self._redraw(text)
        self.out.write("\n")
        self.out.flush()
        self.shown = 0

    def _fit(self, text: str) -> str:
        """A line longer than the terminal wraps, and "\\r" could not get back to its start."""
        room = max(2, self.width() - 1)
        if len(text) <= room:
            return text
        return "…" + text[-(room - 1) :]

    def _redraw(self, text: str) -> None:
        cover = " " * max(0, self.shown - len(text))
        self.out.write(f"\r{text}{cover}")
        self.out.flush()
        self.shown = len(text)

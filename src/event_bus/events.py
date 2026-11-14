"""Things that can happen in the app. Each event is a small, unchangeable record."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SpeechStart:
    """The user started speaking."""


@dataclass(frozen=True)
class SpeechEnd:
    """The user stopped speaking."""


@dataclass(frozen=True)
class PartialText:
    """Text recognised so far while the user is still speaking. May change."""

    text: str


@dataclass(frozen=True)
class FinalText:
    """Final recognised text for one utterance."""

    text: str


@dataclass(frozen=True)
class AiTextChunk:
    """A piece of an AI reply, to be spoken (Phase 2)."""

    text: str

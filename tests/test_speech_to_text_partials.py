from config.settings import load_settings
from event_bus.bus import EventBus
from event_bus.events import PartialText
from speech_to_text.block_timing import partial_interval_blocks, partial_window_blocks
from speech_to_text.recognizer import SpeechRecognizer

# 320 ms is 10 blocks between partials, and 640 ms is the latest 20 blocks.
SETTINGS = load_settings({"PARLAI_PARTIAL_INTERVAL_MS": "320", "PARLAI_PARTIAL_WINDOW_MS": "640"})
END = "." * 16  # 500 ms of silence ends an utterance


class PatternVad:
    """Says speech for each 'S' in the pattern and silence for each '.', in order."""

    def __init__(self, pattern):
        self.verdicts = iter(c == "S" for c in pattern)

    def is_speech(self, block):
        return next(self.verdicts)


class RecordingWorker:
    """Stands in for the worker thread and just remembers what it was asked to transcribe."""

    def __init__(self):
        self.partials = []
        self.finals = []

    def submit_partial(self, audio):
        self.partials.append(audio)

    def submit_final(self, audio):
        self.finals.append(audio)


def run(pattern, settings=SETTINGS):
    recognizer = SpeechRecognizer(settings, EventBus(), vad=PatternVad(pattern), engine=object())
    recognizer.worker = RecordingWorker()
    for number in range(len(pattern)):
        recognizer.process(bytes([number]))
    return recognizer.worker


def test_a_partial_is_asked_for_every_interval_while_speaking():
    worker = run("S" * 35)

    assert len(worker.partials) == 3


def test_nothing_is_asked_for_before_the_first_interval_has_passed():
    assert run("S" * 9).partials == []


def test_a_partial_covers_the_utterance_so_far_until_it_is_longer_than_the_window():
    worker = run("S" * 35)

    assert worker.partials[0] == bytes(range(10))
    assert worker.partials[1] == bytes(range(20))


def test_a_partial_covers_only_the_latest_window_of_a_long_utterance():
    worker = run("S" * 35)

    assert worker.partials[2] == bytes(range(10, 30))


def test_partials_off_when_the_interval_is_zero():
    settings = load_settings({"PARLAI_PARTIAL_INTERVAL_MS": "0"})

    assert run("S" * 100, settings).partials == []


def test_no_partials_while_nobody_is_speaking():
    assert run("." * 100).partials == []


def test_a_final_starts_the_count_again_for_the_next_utterance():
    # partials at blocks 10 and 20 of the first utterance, which ends at block 28
    worker = run("S" * 12 + END + "S" * 9)

    assert len(worker.finals) == 1
    assert len(worker.partials) == 2  # 9 blocks of the next utterance are not yet due


def test_an_empty_partial_text_is_not_published():
    bus = EventBus()
    partials = bus.subscribe(PartialText)
    recognizer = SpeechRecognizer(SETTINGS, bus, vad=PatternVad(""), engine=object())

    recognizer._publish_partial("")
    recognizer._publish_partial("hello")

    assert partials.get_nowait() == PartialText("hello")
    assert partials.empty()


def test_700_ms_is_22_blocks_between_partials():
    assert partial_interval_blocks(load_settings({"PARLAI_PARTIAL_INTERVAL_MS": "700"})) == 22


def test_an_interval_of_zero_is_zero_blocks():
    assert partial_interval_blocks(load_settings({"PARLAI_PARTIAL_INTERVAL_MS": "0"})) == 0


def test_a_tiny_interval_is_still_at_least_one_block():
    assert partial_interval_blocks(load_settings({"PARLAI_PARTIAL_INTERVAL_MS": "1"})) == 1


def test_8_seconds_is_250_blocks_and_the_window_rounds_down():
    assert partial_window_blocks(load_settings({"PARLAI_PARTIAL_WINDOW_MS": "8000"})) == 250
    assert partial_window_blocks(load_settings({"PARLAI_PARTIAL_WINDOW_MS": "8010"})) == 250

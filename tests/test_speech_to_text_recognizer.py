from config.settings import load_settings
from event_bus.bus import EventBus
from event_bus.events import FinalText
from speech_to_text.recognizer import PRE_ROLL_BLOCKS, SpeechRecognizer, silence_blocks

SETTINGS = load_settings({})
SILENCE_BLOCKS_TO_END = silence_blocks(SETTINGS)
END = "." * SILENCE_BLOCKS_TO_END


class PatternVad:
    """Says speech for each 'S' in the pattern and silence for each '.', in order."""

    def __init__(self, pattern):
        self.verdicts = iter(c == "S" for c in pattern)

    def is_speech(self, block):
        return next(self.verdicts)


class RecordingEngine:
    def __init__(self):
        self.heard = []

    def transcribe(self, audio):
        self.heard.append(audio)
        return "some text"


def run(pattern):
    bus = EventBus()
    finals = bus.subscribe(FinalText)
    engine = RecordingEngine()
    recognizer = SpeechRecognizer(SETTINGS, bus, vad=PatternVad(pattern), engine=engine)
    for number in range(len(pattern)):
        recognizer.process(bytes([number]))
    return finals, engine


def test_an_utterance_publishes_one_final_text():
    finals, _ = run("." * 20 + "SS" + END)

    assert finals.get_nowait() == FinalText("some text")
    assert finals.empty()


def test_the_engine_gets_the_pre_roll_the_speech_and_the_silence_that_ended_it():
    _, engine = run("." * 20 + "SS" + END)

    first_block = 20 - PRE_ROLL_BLOCKS
    assert engine.heard == [bytes(range(first_block, 22 + SILENCE_BLOCKS_TO_END))]


def test_silence_alone_publishes_nothing():
    finals, engine = run("." * 30)

    assert finals.empty()
    assert engine.heard == []


def test_two_utterances_publish_two_final_texts():
    finals, engine = run("..SS" + END + "..SSS" + END)

    assert finals.qsize() == 2
    assert len(engine.heard) == 2


def test_pre_roll_is_shorter_when_speech_starts_early():
    _, engine = run("..." + "SS" + END)

    assert engine.heard == [bytes(range(5 + SILENCE_BLOCKS_TO_END))]


def test_the_second_utterance_does_not_contain_audio_from_the_first():
    _, engine = run("SS" + END + "...." + "SS" + END)

    first_end = 2 + SILENCE_BLOCKS_TO_END
    assert engine.heard == [
        bytes(range(first_end)),
        bytes(range(first_end, first_end + 4 + 2 + SILENCE_BLOCKS_TO_END)),
    ]


def test_a_short_pause_inside_speech_stays_one_utterance():
    finals, engine = run("SS.SS" + END)

    assert finals.qsize() == 1
    assert engine.heard == [bytes(range(5 + SILENCE_BLOCKS_TO_END))]


def test_a_pause_just_under_the_limit_does_not_split_the_utterance():
    finals, _ = run("SS" + "." * (SILENCE_BLOCKS_TO_END - 1) + "SS" + END)

    assert finals.qsize() == 1


def test_a_pause_at_the_limit_splits_the_utterance():
    finals, _ = run("SS" + END + "SS" + END)

    assert finals.qsize() == 2


def test_an_utterance_still_in_progress_publishes_nothing():
    finals, engine = run("..SSS")

    assert finals.empty()
    assert engine.heard == []


def test_500_ms_of_silence_is_16_blocks_at_16_khz():
    assert silence_blocks(load_settings({"PARLAI_UTTERANCE_SILENCE_MS": "500"})) == 16


def test_silence_is_rounded_up_so_it_is_never_shorter_than_asked():
    assert silence_blocks(load_settings({"PARLAI_UTTERANCE_SILENCE_MS": "1000"})) == 32


def test_a_tiny_silence_still_needs_at_least_one_block():
    assert silence_blocks(load_settings({"PARLAI_UTTERANCE_SILENCE_MS": "1"})) == 1


def test_the_silence_setting_changes_when_an_utterance_ends():
    settings = load_settings({"PARLAI_UTTERANCE_SILENCE_MS": "100"})

    assert silence_blocks(settings) < SILENCE_BLOCKS_TO_END

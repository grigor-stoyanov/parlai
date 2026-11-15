import wave
from pathlib import Path

from config.settings import load_settings
from event_bus.bus import EventBus
from event_bus.events import FinalText
from speech_to_text.block_timing import silence_blocks
from speech_to_text.recognizer import SpeechRecognizer
from speech_to_text.voice_activity_detection import BLOCK_SAMPLES, Vad

# A real recording of the project author saying "Hello, this is a test of the voice activity
# detector.", trimmed to the speech plus about a quarter of a second of silence each side.
CLIP = Path(__file__).parent / "fixtures" / "speech_16k_mono.wav"
BLOCK_BYTES = BLOCK_SAMPLES * 2
# Partials off: a partial job would reach the engine too and change what it "heard".
SETTINGS = load_settings({"PARLAI_PARTIAL_INTERVAL_MS": "0"})
SILENCE = bytes(BLOCK_BYTES)


def clip_blocks():
    with wave.open(str(CLIP)) as clip:
        assert (clip.getframerate(), clip.getnchannels(), clip.getsampwidth()) == (16000, 1, 2)
        audio = clip.readframes(clip.getnframes())
    return [audio[i : i + BLOCK_BYTES] for i in range(0, len(audio) - BLOCK_BYTES + 1, BLOCK_BYTES)]


def padded_blocks(lead, trail):
    return [SILENCE] * lead + clip_blocks() + [SILENCE] * trail


def test_the_vad_hears_speech_in_a_real_clip_and_silence_around_it():
    lead, trail = 10, 20
    vad = Vad()

    verdicts = [vad.is_speech(block) for block in padded_blocks(lead, trail)]

    speech = verdicts[lead : len(verdicts) - trail]
    assert not any(verdicts[:lead])
    assert sum(speech) >= len(speech) // 2
    assert not any(verdicts[-trail:])


def test_a_real_clip_through_the_recogniser_is_one_utterance():
    bus = EventBus()
    finals = bus.subscribe(FinalText)

    class Engine:
        def transcribe(self, audio):
            return "text"

    recognizer = SpeechRecognizer(SETTINGS, bus, engine=Engine())
    recognizer.start()
    for block in padded_blocks(lead=10, trail=silence_blocks(SETTINGS) + 5):
        recognizer.process(block)
    recognizer.stop()  # waits for the worker thread, so the text has been published

    assert finals.qsize() == 1


def test_the_recogniser_gives_the_engine_the_speech_not_just_silence():
    heard = []

    class Engine:
        def transcribe(self, audio):
            heard.append(audio)
            return "text"

    recognizer = SpeechRecognizer(SETTINGS, EventBus(), engine=Engine())
    recognizer.start()
    for block in padded_blocks(lead=10, trail=silence_blocks(SETTINGS) + 5):
        recognizer.process(block)
    recognizer.stop()

    assert len(heard) == 1
    assert any(heard[0])
    assert len(heard[0]) >= len(b"".join(clip_blocks())) // 2

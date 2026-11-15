"""Main loop: wires the packages in src/ together.

Run with `uv run python main.py` (or the project's .venv interpreter in PyCharm).
"""

import argparse
import os
import time

from dotenv import load_dotenv

from config.settings import ConfigError, Settings, load_settings
from event_bus.bus import EventBus
from event_bus.events import SpeechEnd, SpeechStart
from speech_to_text.recognizer import SpeechRecognizer
from speech_to_text.utterance_segmenter import UtteranceSegmenter
from text_to_speech.audio_player import AudioPlayer


def mic_check(settings: Settings, seconds: float = 5) -> None:
    path = settings.recordings_dir / "mic_check.wav"
    recognizer = SpeechRecognizer(settings)
    player = AudioPlayer(settings)
    recognizer.list_devices()
    print(f"Recording {seconds:g} seconds, speak now...")
    audio = recognizer.record(seconds)
    player.save_wav(path, audio)
    peak, rms = recognizer.measure_levels(audio)
    print(f"Levels: peak {peak:.1f} dBFS, average (RMS) {rms:.1f} dBFS")
    print(f"Saved {path}, playing it back...")
    player.play(audio)


def main(argv: list[str] | None = None, pause: float = 0.5) -> None:
    # argv is injectable so tests don't parse pytest's own command-line flags.
    parser = argparse.ArgumentParser(prog="parlai", description="Talk to AI with your voice.")
    parser.add_argument(
        "--mic-check", action="store_true", help="record 5 seconds and play it back"
    )
    parser.add_argument(
        "--voice-demo", action="store_true", help="after the demo: mic to mock text to mock voice"
    )
    args = parser.parse_args(argv)

    load_dotenv()
    try:
        settings = load_settings(os.environ)
    except ConfigError as error:
        parser.exit(2, f"parlai: invalid settings\n{error}\n")

    if args.mic_check:
        mic_check(settings)
        return

    mock_audio = "..SSS..SS......SS....imasnake"
    bus = EventBus()
    starts = bus.subscribe(SpeechStart)
    ends = bus.subscribe(SpeechEnd)
    segmenter = UtteranceSegmenter(bus)

    for i, chunk in enumerate(mock_audio):
        segmenter.feed(chunk == "S")
        print(f"{i:2} {chunk}")
        for inbox in (starts, ends):
            while not inbox.empty():
                print(f"   -> {inbox.get_nowait()}")
        time.sleep(pause)


    recognizer = SpeechRecognizer(settings)
    player = AudioPlayer(settings)
    print("Speak for 3 seconds...")
    text = recognizer.listen(3)
    print(f"Heard: {text}")
    print(f"Speaking: {text}")
    player.speak(text)


if __name__ == "__main__":
    main()

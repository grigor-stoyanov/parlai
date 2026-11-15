"""Main loop: wires the packages in src/ together.

Run with `uv run python main.py` (or the project's .venv interpreter in PyCharm).
"""

import argparse
import os

from dotenv import load_dotenv

from config.settings import ConfigError, Settings, load_settings
from event_bus.bus import EventBus
from event_bus.events import FinalText
from speech_to_text.recognizer import SpeechRecognizer
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


def main(argv: list[str] | None = None) -> None:
    # argv is injectable so tests don't parse pytest's own command-line flags.
    parser = argparse.ArgumentParser(prog="parlai", description="Talk to AI with your voice.")
    parser.add_argument(
        "--mic-check", action="store_true", help="record 5 seconds and play it back"
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

    live_bus = EventBus()
    finals = live_bus.subscribe(FinalText)
    live_recognizer = SpeechRecognizer(settings, live_bus)
    print("Loading the speech model (downloads once, then works offline)...")
    live_recognizer.prepare()
    print("Speak, Ctrl-C to stop")
    try:
        for block in live_recognizer.blocks():
            live_recognizer.process(block)
            while not finals.empty():
                print(finals.get_nowait().text)
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()

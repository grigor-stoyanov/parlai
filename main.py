"""Main loop: wires the packages in src/ together.

Run with `uv run python main.py` (or the project's .venv interpreter in PyCharm).
"""

import argparse
import os
import queue
import time

from dotenv import load_dotenv

from config.settings import ConfigError, Settings, load_settings
from event_bus.bus import EventBus
from event_logger.bus_logger import EventLogger
from event_logger.lifecycle import log_crash, log_exit, log_startup
from event_logger.logging_setup import setup_logging
from speech_to_text.recognizer import SpeechRecognizer
from text_delivery.console_display import ConsoleDisplay
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


def show_events(events: queue.Queue, display: ConsoleDisplay) -> None:
    """Show every event that has arrived. The texts come from the transcription thread."""
    while not events.empty():
        display.handle(events.get_nowait())


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

    setup_logging(settings)
    log_startup(settings)
    started_at = time.monotonic()
    reason = "finished"
    event_log = None
    try:
        if args.mic_check:
            mic_check(settings)
            return

        live_bus = EventBus()
        event_log = EventLogger(live_bus, include_text=settings.log_level == "DEBUG")
        event_log.start()
        # One inbox for everything, so a partial can never be shown after its final text.
        events = live_bus.subscribe_all()
        display = ConsoleDisplay()
        live_recognizer = SpeechRecognizer(settings, live_bus)
        print("Loading the speech model (downloads once, then works offline)...")
        live_recognizer.prepare()
        print("Speak, Ctrl-C to stop")
        live_recognizer.start()
        try:
            for block in live_recognizer.blocks():
                live_recognizer.process(block)
                show_events(events, display)
        except KeyboardInterrupt:
            print()
            reason = "stopped by user"
        finally:
            # Finishes the sentence still being transcribed, so the last words are not lost.
            live_recognizer.stop()
            show_events(events, display)
    except Exception as error:
        reason = "crashed"
        log_crash(error)
        raise
    finally:
        if event_log is not None:
            event_log.stop()
        log_exit(reason, started_at)


if __name__ == "__main__":
    main()

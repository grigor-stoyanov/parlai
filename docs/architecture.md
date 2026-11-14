# Architecture

```
 Mic ─▶ AudioCapture ─▶ VAD ─▶ STT engine ─▶ Event bus ─┬▶ TerminalSink (PTY inject)
        (sounddevice)  (silero) (faster-whisper)        └▶ WebSocketSink ─▶ browser input
                                                                │
 Speaker ◀─ AudioPlayer ◀─ TTS engine ◀─ TextCleaner ◀──────────┴─ Sources: PTY tee / browser DOM
            (sounddevice)  (Kokoro/Piper)                                    (Phase 2)
```

The app runs as a few plain threads (mic, recogniser, server); the packages talk through a small event bus built on thread-safe `queue.Queue`. Events: `partial_text`, `final_text`, `speech_start`, `speech_end`, `ai_text_chunk`.

## Packages (in `src/`)
Each package does one job and does not orchestrate. The root `main.py` is the main loop that wires them together. Packages and modules exist as docstring-only placeholders; each is filled in at its milestone.

| Package | Job | Interface | Starts at |
|---|---|---|---|
| `speech_to_text` | mic capture, VAD, Whisper | `STTEngine.transcribe_stream(audio_chunks) -> AsyncIterator[Transcript]` | M1 |
| `event_bus` | small thread-safe bus the others talk through | `publish(event)`, `subscribe()` | M3 |
| `text_delivery` | sinks: PTY injection, WebSocket to browser | `Sink.emit(event)` | M3 |
| `text_to_speech` | text cleaning, TTS engine, playback | `TTSEngine.synthesize(text) -> AsyncIterator[bytes]` | M6 |
| `ai_output_capture` | sources: PTY tee, browser DOM | `Source` yields AI output text | M6 |

## Layout
```
parlai/
├── CLAUDE.md
├── docs/
├── pyproject.toml
├── main.py                 # main loop; run with `uv run python main.py`
├── src/
│   ├── speech_to_text/     # audio_capture, vad, whisper_engine
│   ├── event_bus/          # events, bus
│   ├── text_delivery/      # terminal_sink, websocket_sink
│   ├── text_to_speech/     # text_cleaner, tts_engine, audio_player
│   └── ai_output_capture/  # terminal_source, browser_source
├── web/                    # minimal HTML client and test page (M3)
└── tests/
```

Each new package must be added to `packages = [...]` under `[tool.hatch.build.targets.wheel]` in `pyproject.toml`, then `uv sync`. Plain `python3 main.py` fails because the system Python can't see the venv; use `uv run` or the `.venv` interpreter.

## Milestones
1. **M0:** project scaffold (`uv init`, deps, CLI skeleton).
2. **M1:** mic capture, VAD and faster-whisper print finals to stdout.
3. **M2:** partial results (rolling-window re-transcription).
4. **M3:** WebSocket server and an HTML page where the input fills live.
5. **M4:** PTY wrapper that injects text into a CLI (e.g. `python main.py run -- claude`).
6. **M5:** push-to-talk, mute, auto-submit.
7. **M6 (Phase 2):** PTY output tee, text cleaner, TTS playback, barge-in.
8. **M7 (optional):** speaker verification, browser extension for arbitrary pages.

## Conventions
- Python 3.12, type hints, `ruff` for lint and format.
- Threads and `queue.Queue`, no asyncio unless a real need appears. Keep the audio callback thread free of blocking work and hand off via queues.
- Never log raw audio or transcripts at INFO level.
- Commands: `uv sync`, `uv run python main.py`, `uv run pytest`, `uv run ruff check .`

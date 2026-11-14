# Dependencies (proposed)

| Purpose | Choice | Why / alternative |
|---|---|---|
| Language/tooling | Python 3.12, `uv` | Best audio/ML ecosystem |
| Mic/speaker I/O | `sounddevice` (+ `portaudio`) | Simple; works with PipeWire |
| VAD | `silero-vad` (or `webrtcvad`) | Accurate, light |
| STT | `faster-whisper` | Local, fast, streaming-friendly. Alternatives: `whisper.cpp`, `RealtimeSTT`, Vosk (lighter, less accurate) |
| Server/WebSocket | `websockets` (its thread-based sync API) | Browser transport. Avoids asyncio; check thread-safety of sending in M3 |
| Terminal injection | stdlib `pty` / `ptyprocess`, `pexpect` | Wrap the CLI in a PTY and write to its stdin |
| TTS (Phase 2) | `kokoro` or `piper-tts` | Local, good quality on CPU |
| Config/CLI | stdlib `argparse` for now | Swap to `typer` only if the CLI grows |
| Tests | `pytest` | |

System packages (Arch): `portaudio`, `pipewire-alsa`, optionally CUDA/`cudnn` for GPU.

Note: system Python is 3.14; the project pins 3.12 via `.python-version` (uv fetches it) because ML wheels (ctranslate2 etc.) lag behind. Runtime dependencies start empty and are added per milestone.

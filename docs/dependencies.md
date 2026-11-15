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
| Env file | `python-dotenv` | Loads `.env` into the environment; `config` validates the values at startup |
| Config/CLI | stdlib `argparse` for now | Swap to `typer` only if the CLI grows |
| Tests | `pytest` | |
| Packaging (dev) | `pyinstaller` | Bundles Python and the app for users without Python. Build per OS, no cross-compiling. Alternatives: Nuitka (slower builds), cx_Freeze (fewer audio hooks) |
| CI builds | GitHub Actions | Builds the Windows and Linux binaries on their own OS runners (`.github/workflows/build.yml`) |

System packages (Arch): `portaudio`, `pipewire-alsa`, optionally CUDA/`cudnn` for GPU. Built binaries do not bundle system sound libraries or drivers; per-OS requirements are in the README.

Note: system Python is 3.14; the project pins 3.12 via `.python-version` (uv fetches it) because ML wheels (ctranslate2 etc.) lag behind. Runtime dependencies start empty and are added per milestone.

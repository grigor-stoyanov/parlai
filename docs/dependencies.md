# Dependencies (proposed)

| Purpose | Choice | Why / alternative |
|---|---|---|
| Language/tooling | Python 3.12, `uv` | Best audio/ML ecosystem |
| Mic/speaker I/O | `sounddevice` (+ `portaudio`) | Simple; works with PipeWire |
| VAD | Silero VAD model file bundled in `faster-whisper`, run with `onnxruntime` and `numpy` in our own stateful wrapper (`speech_to_text/voice_activity_detection.py`) | Accurate, light, no torch. faster-whisper's own wrapper resets the model's memory on every call, so it can't be used block by block. Limits: only 512-sample blocks at 16 kHz, so 8000 Hz in config is not usable with it. We rely on faster-whisper's internal model file (`assets/silero_vad_v6.onnx`) and its input shapes, so faster-whisper is pinned to 1.2.x. Not chosen: the `silero-vad` package (pulls in torch), `webrtcvad` (10/20/30 ms frames, our block is 32 ms) |
| STT | `faster-whisper` (brings `ctranslate2`, `av`, `tokenizers`, `huggingface-hub`) | Local, fast, streaming-friendly. The recogniser still uses a mock engine until the real model is wired in. Alternatives: `whisper.cpp`, `RealtimeSTT`, Vosk (lighter, less accurate) |
| Server/WebSocket | `websockets` (its thread-based sync API) | Browser transport. Avoids asyncio; check thread-safety of sending in M3 |
| Terminal injection | stdlib `pty` / `ptyprocess`, `pexpect` | Wrap the CLI in a PTY and write to its stdin |
| TTS (Phase 2) | `kokoro` or `piper-tts` | Local, good quality on CPU |
| Env file | `python-dotenv` | Loads `.env` into the environment; `config` validates the values at startup |
| Config/CLI | stdlib `argparse` for now | Swap to `typer` only if the CLI grows |
| Tests | `pytest` | |
| Packaging (dev) | `pyinstaller` | Bundles Python and the app for users without Python. Build per OS, no cross-compiling. Alternatives: Nuitka (slower builds), cx_Freeze (fewer audio hooks) |
| CI builds | GitHub Actions | Builds the Windows and Linux binaries on their own OS runners (`.github/workflows/release.yml`, run manually) |

System packages (Arch): `portaudio`, `pipewire-alsa`, optionally CUDA/`cudnn` for GPU. Built binaries do not bundle system sound libraries or drivers; per-OS requirements are in the README.

Note: system Python is 3.14; the project pins 3.12 via `.python-version` (uv fetches it) because ML wheels (ctranslate2 etc.) lag behind. Runtime dependencies start empty and are added per milestone.

# Dependencies (proposed)

| Purpose | Choice | Why / alternative |
|---|---|---|
| Language/tooling | Python 3.12, `uv` | Best audio/ML ecosystem |
| Mic/speaker I/O | `sounddevice` (+ `portaudio`) | Simple; works with PipeWire |
| VAD | Silero VAD model file bundled in `faster-whisper`, run with `onnxruntime` and `numpy` in our own stateful wrapper (`speech_to_text/voice_activity_detection.py`) | Accurate, light, no torch. faster-whisper's own wrapper resets the model's memory on every call, so it can't be used block by block. Limits: only 512-sample blocks at 16 kHz, so config accepts nothing else (`PARLAI_SAMPLE_RATE` must be 16000, `PARLAI_BLOCK_SIZE` 512). We rely on faster-whisper's internal model file (`assets/silero_vad_v6.onnx`) and its input shapes, so faster-whisper is pinned to 1.2.x. Not chosen: the `silero-vad` package (pulls in torch), `webrtcvad` (10/20/30 ms frames, our block is 32 ms) |
| STT | `faster-whisper` (brings `ctranslate2`, `av`, `tokenizers`, `huggingface-hub`) | Local, fast, streaming-friendly. Model `small.en` by default, set with `PARLAI_WHISPER_MODEL`. Runs on the GPU (float16) when one works, else the CPU (int8), chosen with `PARLAI_WHISPER_DEVICE` (`auto` tries the GPU, runs one second of silence to prove the CUDA libraries load, and falls back to the CPU). The model downloads from Hugging Face into its cache on first start, then works offline. Alternatives: `whisper.cpp`, `RealtimeSTT`, Vosk (lighter, less accurate) |
| Server/WebSocket | `websockets` (its thread-based sync API) | Browser transport. Avoids asyncio; check thread-safety of sending in M3 |
| Terminal injection | stdlib `pty` / `ptyprocess`, `pexpect` | Wrap the CLI in a PTY and write to its stdin |
| TTS (Phase 2) | `kokoro` or `piper-tts` | Local, good quality on CPU |
| Env file | `python-dotenv` | Loads `.env` into the environment; `config` validates the values at startup |
| Config/CLI | stdlib `argparse` for now | Swap to `typer` only if the CLI grows |
| Tests | `pytest` | |
| GPU (optional) | `nvidia-cublas-cu12`, `nvidia-cudnn-cu12` 9.x in the `cuda` extra (`uv sync --extra cuda`) | CUDA 12 libraries for ctranslate2 on NVIDIA GPUs, about 1.2 GB. Arch's `cuda` package is CUDA 13 and does not work. Loaded into our process by `speech_to_text/cuda_libraries.py` (no `LD_LIBRARY_PATH`), never bundled in the binaries. Linux tested; Windows (`os.add_dll_directory`) not tested |
| Packaging (dev) | `pyinstaller` | Bundles Python and the app for users without Python. Build per OS, no cross-compiling. Alternatives: Nuitka (slower builds), cx_Freeze (fewer audio hooks) |
| CI builds | GitHub Actions | Builds the Windows and Linux binaries on their own OS runners (`.github/workflows/release.yml`, run manually) |

System packages (Arch): `portaudio`, `pipewire-alsa`, optionally CUDA/`cudnn` for GPU. Built binaries do not bundle system sound libraries or drivers; what each OS needs is in [requirements.md](requirements.md).

Note: system Python is 3.14; the project pins 3.12 via `.python-version` (uv fetches it) because ML wheels (ctranslate2 etc.) lag behind. Runtime dependencies start empty and are added per milestone.

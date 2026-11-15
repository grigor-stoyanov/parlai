# parlai

A local voice interface for talking to AI. Speak into your microphone and the recognised text is streamed live into a terminal or an HTML input. Later, AI replies are read back to you as speech.

Everything runs locally: no audio leaves your machine.

## Status

Speech to text works in the terminal: it listens to your microphone, detects when you speak, and prints what you said, on the GPU if one works and otherwise the CPU. Not built yet: live partial text while you speak, sending text into another terminal or a browser input, and spoken AI replies (the speech engine is still a mock). See the status of every feature in [docs/project-requirements.md](docs/project-requirements.md), what a machine needs in [docs/requirements.md](docs/requirements.md), and the milestones in [docs/architecture.md](docs/architecture.md).

## Setup

Requires [uv](https://docs.astral.sh/uv/). It installs the pinned Python 3.12 for you.

```bash
uv sync
```

## Configure

Optional. Copy `.env.example` to `.env` and change the values (audio settings, recordings folder). Invalid values stop the app at startup with a message naming the variable and the broken rule (codes `PARLAI-E001` to `E103`, defined in `src/config/rules.py`). Allowed: sample rate 16000 (the voice activity detector and Whisper only take 16 kHz), block size 512 to match, 1 channel. `PARLAI_UTTERANCE_SILENCE_MS` (default 500) is how long you must pause before the text for what you said appears: lower is faster but splits sentences at small pauses, higher waits longer. Speech recognition: `PARLAI_WHISPER_MODEL` (default `small.en`) and `PARLAI_WHISPER_DEVICE` (`auto`, `cuda` or `cpu`; `auto` uses the GPU when it works, else the CPU). The first run downloads the model from Hugging Face (about 0.5 GB for `small.en`; no audio is sent) and later runs work offline.

## Run

```bash
uv run python main.py
uv run python main.py --mic-check   # record 5 seconds and play it back
```

Plain `python3 main.py` won't work, because the system Python can't see the project's virtual environment. In PyCharm, set the interpreter to `.venv`.

## Logs

Everything is logged to `logs/parlai.log` (folder set by `PARLAI_LOG_DIR`, name by `PARLAI_LOG_NAME`) as one JSON object per line. Set `PARLAI_LOG_FORMAT=text` for plain readable lines instead. Every line has a `time`, `level`, `source` (which module wrote it) and `label` (what kind of line: `startup`, `vad`, `model`, `audio_device`, `SpeechStart`, `SpeechEnd`, `FinalText`, `error`, `exit`). At midnight the file is renamed `parlai-YYYY-MM-DD.log`. Libraries that log every request, such as the model downloader, are turned down to warnings; the list is `PARLAI_LOG_QUIET_LOGGERS` (a comma-separated list of logger names, or `none`). Files older than `PARLAI_LOG_KEEP_DAYS` (default 14) are deleted, and the oldest are deleted first whenever the folder grows past `PARLAI_LOG_MAX_MB` (default 50). The terminal shows warnings and errors; change that with `PARLAI_LOG_CONSOLE_LEVEL` (`DEBUG`, `INFO`, `WARNING`, `ERROR` or `OFF`).

A run logs its version, Python and library versions and settings at startup, whether the speech model came from the cache or was downloaded, which devices were chosen, every speech event, any crash with its traceback, and why it exited.

Transcripts are private: at the default `INFO` level `FinalText` lines only record the number of characters. `PARLAI_LOG_LEVEL=DEBUG` adds the text, so use it only while debugging. Raw audio is never logged.

```bash
tail -f logs/parlai.log
jq 'select(.level != "INFO")' logs/parlai.log   # only warnings and errors
```

## Faster recognition on an NVIDIA GPU (optional)

Speech recognition runs on the CPU by default and uses a GPU automatically when one works (`PARLAI_WHISPER_DEVICE=auto`). For an NVIDIA GPU it needs NVIDIA's CUDA 12 libraries (cuBLAS and cuDNN 9), which are not part of the driver. From a source checkout:

```bash
uv sync --extra cuda
uv run python main.py
```

The log should then say `loaded CUDA libraries from the cuda extra` and `model loaded ... device="cuda"`. The libraries are loaded inside the app only, so no `LD_LIBRARY_PATH` is needed and other programs are not affected. About 1.2 GB is downloaded once. A plain `uv sync` afterwards removes them again, so keep using `--extra cuda`.

If they are missing or fail to load, the log says why and the app runs on the CPU. AMD, Intel and Apple GPUs are not supported for recognition and always use the CPU.

The built binaries do not include CUDA (it is large, and like drivers it belongs to the machine). To use an NVIDIA GPU with a binary, the CUDA 12 libraries must already be findable on the machine: on Linux install cuBLAS 12 and cuDNN 9 so the system loader sees them (or start it as `LD_LIBRARY_PATH=/folder/with/the/libs ./parlai/parlai`), on Windows install them and put their `bin` folders on `PATH`. I have not tested this on Windows.

## Build a binary

For testing on machines without Python. PyInstaller can't cross-compile, so build on the OS you target:

```bash
uv run pyinstaller --noconfirm --distpath dist --workpath build packaging/parlai.spec
dist/parlai/parlai --mic-check
```

Binaries are built and released by one manual GitHub Actions workflow, "Release". Nothing is built on push.

1. Tag the commit you want to release and push the tag: `git tag v0.1.0 && git push origin v0.1.0`.
2. In the Actions tab, run "Release" and enter the tag. Tick Linux and/or Windows to choose what gets built.
3. The workflow builds the ticked ones from that tag and publishes a GitHub Release with `parlai-linux-x86_64.tar.gz` and/or `parlai-windows-x86_64.zip` attached.

It stops with a message if the tag doesn't exist or nothing is ticked. If a release for the tag already exists, delete it first.

### What the binary needs on the machine

The binary does not bundle drivers or system sound libraries. It connects to whatever the user already has, so the audio stack must be there.

Linux:
- PortAudio must be installed: `libportaudio2` on Debian and Ubuntu, `portaudio` on Arch and Fedora. Without it the app fails at startup with a PortAudio error.
- Most desktops need the ALSA bridge to the sound server for the right microphone to be picked automatically: `pipewire-alsa` for PipeWire, `libasound2-plugins` for PulseAudio. Without it only raw `hw:` devices appear, which can be busy or silent. Set `PARLAI_INPUT_DEVICE` to choose one by hand.
- The Linux build is made on Ubuntu 22.04, so it needs glibc 2.35 or newer: Debian 12, Ubuntu 22.04 and newer, current Fedora and Arch all work; Debian 11 does not.
- x86_64 only for now.

Windows:
- Nothing to install for audio. The Microsoft Visual C++ Redistributable (x64) may be needed by the speech libraries; not verified. The PortAudio DLL ships inside the `sounddevice` package and is bundled, since Windows has no system copy. Audio goes through Windows' own drivers.
- Microphone access must be allowed: Settings, Privacy and security, Microphone, "Let desktop apps access your microphone".
- The exe is unsigned, so SmartScreen or an antivirus may warn about it. This is common for PyInstaller builds.
- Device selection on Windows and macOS trusts the system default, and has not been tested there yet.

### Check that a binary works

Download it (from the Release page, or from the finished "Release" run's artifacts), extract it, and run it on a machine of that OS. A binary built on one OS can't be tested on another.

```bash
tar -xzf parlai-linux-x86_64.tar.gz          # Windows: unzip parlai-windows-x86_64.zip
./parlai/parlai --mic-check                  # Windows: .\parlai\parlai.exe --mic-check
./parlai/parlai                              # then speak; the first run downloads the model
```

What good looks like:
- `--mic-check` lists your input devices, marks one `<- selected`, prints the levels line, and you hear your voice back.
- The plain run prints `Speak, Ctrl-C to stop`, then each sentence you say as text.
- `logs/parlai.log` has a `startup` line with real version numbers (not `unknown`), a `vad` line, a `model` line (`using cached model`, or `downloading` the first time), an `audio_device` line, and on Ctrl-C an `exit` line with `reason: "stopped by user"`.

A crash at start with an `ImportError` means a library is missing from the bundle (a packaging bug, please report it). A PortAudio error means the system library from the list above is not installed.

## Develop

```bash
uv run pytest            # tests
uv run ruff check .      # lint
uv run ruff format .     # format
```

## Layout

```
main.py                  main loop that wires the packages together
src/
  config/                settings from PARLAI_* environment variables, checked at startup
  sound_utils/           shared microphone and speaker classes, device choice, gain, wav
  event_logger/          JSON log lines (events, startup, errors, exit) in daily files
  speech_to_text/        recogniser on the microphone, voice activity detection, Whisper
  event_bus/             small thread-safe bus the packages talk through
  text_delivery/         send text to a terminal (PTY) or browser input
  text_to_speech/        audio player on the speaker, speech engine (Phase 2)
  ai_output_capture/     read AI replies from a terminal or page (Phase 2)
tests/
packaging/               PyInstaller spec for the binaries
docs/                    system and project requirements, dependencies, architecture
```

## Security

See [SECURITY.md](SECURITY.md) for how to report a vulnerability and the design rules.

## License

[PolyForm Noncommercial 1.0.0](LICENSE). The code is open to read, run, modify and share for personal and other noncommercial use. Using it for a commercial purpose, for example inside a company, needs a separate paid licence: email grigor.stoyanov@hotmail.com or open an issue at https://github.com/grigor-stoyanov/parlai/issues to ask.

Versions up to and including v0.2.1 were released under the MIT licence and stay MIT for anyone who already has them. The new terms apply to later versions.

## Docs

- [System requirements](docs/requirements.md) (hardware, drivers and libraries needed)
- [Project requirements](docs/project-requirements.md) (features, status, open questions)
- [Dependencies](docs/dependencies.md)
- [Architecture](docs/architecture.md)

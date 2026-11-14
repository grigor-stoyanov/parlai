# parlai

A local voice interface for talking to AI. Speak into your microphone and the recognised text is streamed live into a terminal or an HTML input. Later, AI replies are read back to you as speech.

Everything runs locally: no audio leaves your machine.

## Status

Early scaffold. The package layout is in place, but there is no working speech recognition yet. See the milestones in [docs/architecture.md](docs/architecture.md).

## Setup

Requires [uv](https://docs.astral.sh/uv/). It installs the pinned Python 3.12 for you.

```bash
uv sync
```

## Configure

Optional. Copy `.env.example` to `.env` and change the values (audio settings, recordings folder). Invalid values stop the app at startup with a message naming the variable and the broken rule (codes `PARLAI-E001` to `E103`, defined in `src/config/rules.py`). Allowed: sample rate 8000 or 16000, block size 256 or 512 to match, 1 channel.

## Run

```bash
uv run python main.py
```

Plain `python3 main.py` won't work, because the system Python can't see the project's virtual environment. In PyCharm, set the interpreter to `.venv`.

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
  speech_to_text/        mic capture, voice activity detection, Whisper
  event_bus/             small thread-safe bus the packages talk through
  text_delivery/         send text to a terminal (PTY) or browser input
  text_to_speech/        speak AI replies (Phase 2)
  ai_output_capture/     read AI replies from a terminal or page (Phase 2)
tests/
docs/                    requirements, dependencies, architecture
```

## Security

See [SECURITY.md](SECURITY.md) for how to report a vulnerability and the design rules.

## License

[MIT](LICENSE)

## Docs

- [Requirements](docs/requirements.md)
- [Dependencies](docs/dependencies.md)
- [Architecture](docs/architecture.md)

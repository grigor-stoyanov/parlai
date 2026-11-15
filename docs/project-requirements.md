# Project requirements

What parlai should do, with status. What a machine needs to run it is in [requirements.md](requirements.md).

Status as of the M1 work: **done** = working and run by hand, **partial** = some of it works, **todo** = not started. See [architecture.md](architecture.md) for how it is built.

## Phase 1: speech to text
- F1. Capture microphone audio on Linux (Arch, PipeWire). **Done.** Linux picks the `pipewire`/`pulse` ALSA devices because PortAudio's own default ignores PipeWire; Windows and macOS trust the OS default (untested).
- F2. Voice activity detection: only transcribe while speaking; detect end of utterance. **Done.** Silero VAD on 512-sample blocks at 16 kHz. An utterance ends after a configurable silence (`PARLAI_UTTERANCE_SILENCE_MS`, default 500 ms), with about 0.3 s of audio kept from before speech starts.
- F3. Streaming transcription: show partial text while speaking, then a final corrected text per utterance. **Partial.** Final text per utterance works (faster-whisper, `small.en`); partials are M2.
- F3a. Cap the length of one utterance (about 30 s, the size of Whisper's window) so a long monologue cannot block recognition for seconds. **Todo.**
- F3b. Transcription must not block the microphone loop: text should keep appearing while the user speaks, not only after each sentence is processed. **Todo** (needs a worker thread; today Whisper runs inside the mic loop).
- F4. Output sinks (pluggable): **Todo.** Today the final text is printed to the terminal.
  - Terminal: type into the target terminal session (PTY wrapper around e.g. `claude`, or stdout pipe).
  - Browser: push text to an `<input>`/`<textarea>` via WebSocket (small JS client or userscript/extension).
- F5. Controls: push-to-talk hotkey and/or always-listening mode, mute toggle, send behaviour (auto-submit on silence vs. manual Enter). **Todo.** Today it is always listening until Ctrl-C.
- F6. English first; the language is configurable. **Partial.** The model is configurable (`PARLAI_WHISPER_MODEL`, default the English-only `small.en`); a separate language setting comes with a multilingual model.

## Phase 2: text to speech
- F7. Capture AI output from a terminal (PTY tee) or a page (DOM observer over WebSocket). **Todo.**
- F8. Clean text before speaking: strip ANSI codes, markdown and code blocks (summarise or skip code). **Todo.**
- F9. Stream audio sentence by sentence so speech starts before the reply finishes. **Todo.** `AudioPlayer.speak` and the speaker device exist, but the engine is a mock that plays a tone.
- F10. Barge-in: speaking interrupts playback. **Todo.**

## Cross-cutting
- F11. Configuration through `PARLAI_*` environment variables or a `.env` file, validated at startup. A bad value stops the app with a message naming the variable and a rule code (`PARLAI-E001` and up). **Done.**
- F12. Logging for debugging: one JSON (or plain text) line per event, startup, model load, error and exit, in daily files that are deleted by age and total size. Transcripts are never logged at the default level, raw audio never. **Done.**
- F13. Run on an NVIDIA GPU when one works and otherwise on the CPU, chosen automatically and overridable (`PARLAI_WHISPER_DEVICE`). The CUDA 12 libraries are an optional install (`uv sync --extra cuda`). **Done on Linux**, Windows untested.
- F14. Ship binaries so people can try it without Python: Linux and Windows, built by a manual GitHub Actions workflow and attached to a release. **Partial.** The Linux binary builds and runs; the Windows one is untested, macOS is not built, and none are signed.
- F15. Binaries and installs never bundle drivers or system sound or GPU libraries; the app connects to what the machine already has and says clearly in the log when something is missing. **Done** (see the README for what each OS needs).

## Non-functional
- Local and private by default: no audio leaves the machine. The only network use is downloading the speech model from Hugging Face once, then it works offline.
- Never log raw audio, and never transcripts at INFO or above.
- Latency target: final text within about 1 s of the end of speech on CPU, faster on GPU. Measured on one short clip (3.7 to 3.8 s of speech, `small.en`): about 1.2 s on CPU and about 0.2 to 0.3 s on the RTX 5070 GPU, on top of the 0.5 s silence that ends the utterance. Long utterances are not measured yet, which is why the cap (F3a) comes first.
- Audio format is fixed by the VAD and Whisper: 16 kHz, mono, 16-bit, 512-sample blocks. Config rejects anything else.
- Modular: STT engine, sink and TTS engine are swappable behind small interfaces.
- Simple to run: one command (`uv run python main.py`), or the binary.
- Platforms: Linux (tested), Windows (built, untested). The Linux binary needs glibc 2.35 or newer (Debian 12, Ubuntu 22.04 and newer) and x86_64.

## Decisions made
- VAD: Silero model file from faster-whisper, run with onnxruntime in our own wrapper that keeps the model's memory between blocks. No torch.
- STT: faster-whisper, model `small.en` by default, int8 on CPU and float16 on GPU.
- GPU: RTX 5070 Laptop (Blackwell) works with the pip CUDA 12 libraries. Arch's own `cuda` package is CUDA 13 and does not work with this ctranslate2. The libraries are loaded inside the app, with no `LD_LIBRARY_PATH`.
- Packaging: PyInstaller, one build per OS, Linux built on Ubuntu 22.04 for old-glibc compatibility.
- Code signing, when we release: apply to SignPath Foundation for Windows (free for open source, needs a first release and a published code signing policy); macOS needs a paid Apple Developer ID.

## Open questions
- "Picks up my voice": plain mic capture, or speaker verification (only respond to *your* voice)? Assumed plain capture. Speaker ID is an optional later feature (e.g. `speechbrain` ECAPA embeddings).
- Primary terminal and AI CLI (Claude Code, other)? Primary browser?
- Hotkey style: global (needs Wayland/X11 specifics) or terminal-local?
- Partials (M2): how often to re-transcribe, and over how much audio, so the text stays live without the cost growing with the utterance?
- Utterance cap: what length, and should hitting it end the utterance and carry on listening as a new one?
- Whisper model: is `small.en` accurate enough, or `medium.en` or a multilingual model, now that the GPU makes bigger ones affordable?
- macOS: build and support it? It would need an Apple Developer ID to avoid the Gatekeeper block.
- Windows GPU: the CUDA preload path (`os.add_dll_directory`) and the binary's behaviour with CUDA installed are untested.
- Where a binary keeps its logs and the downloaded model: today `logs/` in the working directory and the Hugging Face cache. A per-user folder may suit installed apps better.

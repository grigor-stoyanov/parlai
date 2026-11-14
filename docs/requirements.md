# Requirements

## Phase 1: speech to text
- F1. Capture microphone audio on Linux (Arch, PipeWire).
- F2. Voice activity detection: only transcribe while speaking; detect end of utterance.
- F3. Streaming transcription: show partial text while speaking, then a final corrected text per utterance.
- F4. Output sinks (pluggable):
  - Terminal: type into the target terminal session (PTY wrapper around e.g. `claude`, or stdout pipe).
  - Browser: push text to an `<input>`/`<textarea>` via WebSocket (small JS client or userscript/extension).
- F5. Controls: push-to-talk hotkey and/or always-listening mode, mute toggle, send behaviour (auto-submit on silence vs. manual Enter).
- F6. English first; the language is configurable.

## Phase 2: text to speech
- F7. Capture AI output from a terminal (PTY tee) or a page (DOM observer over WebSocket).
- F8. Clean text before speaking: strip ANSI codes, markdown and code blocks (summarise or skip code).
- F9. Stream audio sentence by sentence so speech starts before the reply finishes.
- F10. Barge-in: speaking interrupts playback.

## Non-functional
- Local and private by default: no audio leaves the machine.
- Latency target: final text within ~1s of end of speech on CPU, faster on GPU.
- Modular: STT engine, sink and TTS engine are swappable behind small interfaces.
- Simple to run: one command (`uv run python main.py`).

## Open questions
- "Picks up my voice": plain mic capture, or speaker verification (only respond to *your* voice)? Assumed plain capture. Speaker ID is an optional later feature (e.g. `speechbrain` ECAPA embeddings).
- GPU: RTX 5070 Laptop (Blackwell). Decided: try CUDA with faster-whisper; needs a recent CUDA/cuDNN, to be verified in M1. CPU fallback.
- Primary terminal and AI CLI (Claude Code, other)? Primary browser?
- Hotkey style: global (needs Wayland/X11 specifics) or terminal-local?

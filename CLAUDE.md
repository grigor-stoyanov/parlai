# parlai

A local voice interface for talking to AI.

## What it does
- Captures my microphone, recognises speech locally, and streams the text live into a terminal or an HTML input so I can talk to an AI.
- Later: reads AI responses from a terminal or HTML page and speaks them back.

## What it does not do
- No cloud speech services; audio never leaves the machine.
- Not a general dictation or desktop assistant. It only feeds a terminal or an HTML input, and reads AI replies back.
- Does not talk to an AI model itself. It only moves text between my voice and an existing AI CLI or web UI.
- Does not log raw audio or transcripts at INFO level.

## How we work (co-developing, not vibecoding)

### Do
- Work in small steps: one milestone or change at a time.
- Explain non-trivial pieces first (what, how, why this over the alternatives) and wait for agreement before writing them.
- Ask when there is a real decision (library, interface shape, behaviour). Mention small obvious defaults.
- Write plain code: clear names, short functions, one job per module. If we can't both explain it, simplify it.
- Comment the why, especially for non-obvious audio, threading and PTY details.
- End each step with something we can run, plus the expected output.
- Test logic that can break quietly (text cleaning, utterance segmentation).
- Report honestly: what works, what was only partly tested, what is unknown.
- Prefer the standard library when it is good enough.
- Update `docs/` in the same step as any decision that changes it.

### Don't
- Don't build ahead of what we agreed on.
- Don't silently pick a library, interface or behaviour.
- Don't add a dependency, abstraction or config option without a concrete need right now.
- Don't write clever or dense code that needs a long explanation.
- Don't mock hardware I/O in tests that prove nothing.
- Don't hide errors or claim something works without running it.
- Don't commit, delete or restructure anything without asking.
- Don't dump large amounts of code at once; keep each change reviewable.

## Details (read only when needed)
- Requirements and open questions: `docs/requirements.md`
- Dependencies: `docs/dependencies.md`
- Architecture, layout, milestones, conventions and commands: `docs/architecture.md`

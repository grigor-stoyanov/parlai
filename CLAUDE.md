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

## Licence
- parlai is under the PolyForm Noncommercial 1.0.0 licence (from v0.2.2; v0.2.1 and earlier stay MIT). Free for personal and other noncommercial use. Companies need a paid licence from the author, who also signs a Windows build on request.
- It is source-available, not OSI open source. That rules out SignPath Foundation signing and means we sell commercial licences on the side, so everything we ship must allow that.
- Dependencies: every new one needs a licence check before it is added, and its licence must allow redistribution inside a closed-terms, noncommercial-only app. Ask first. Do not add GPL, AGPL or other strong copyleft code, "non-commercial" or research-only licences, or anything we cannot redistribute in the binaries. LGPL and MPL need an explicit decision from the user. Check what a wheel bundles inside it too, not only its own licence.
- When dependencies change, regenerate `THIRD_PARTY_NOTICES.md` and record the licence in `docs/dependencies.md`.

## How we work (co-developing, not vibecoding)

### Do
- Work in small steps: one milestone or change at a time.
- Explain non-trivial pieces first (what, how, why this over the alternatives) and wait for agreement before writing them.
- Ask when there is a real decision (library, interface shape, behaviour). Mention small obvious defaults.
- Write plain code: clear names, short functions, one job per module. If we can't both explain it, simplify it.
- Comment the why, especially for non-obvious audio, threading and PTY details.
- End each step with something we can run, plus the expected output.
- Test logic that can break quietly (text cleaning, utterance segmentation).
- Name test files `tests/test_<package>*.py` (e.g. `test_speech_to_text_utterance.py`) so the test hook can find them.
- Report honestly: what works, what was only partly tested, what is unknown.
- Prefer the standard library when it is good enough.
- Update `docs/` in the same step as any decision that changes it.

### Don't
- Don't build ahead of what we agreed on.
- Don't silently pick a library, interface or behaviour.
- Don't add a dependency, abstraction or config option without a concrete need right now.
- Don't write clever or dense code that needs a long explanation.
- Don't mock hardware I/O in tests that prove nothing.
- Don't run tests (pytest or any test command) yourself. A Stop hook already runs the relevant tests after code changes and the `test-report` skill reports them. See `.claude/hooks/` and `.claude/skills/test-report/`.
- Don't fix, analyze or re-run on a test report unless asked. Report it and wait.
- Don't hide errors or claim something works without running it (run the app itself; tests are the hook's job).
- Don't commit, delete or restructure anything without asking.
- Don't dump large amounts of code at once; keep each change reviewable.

## Details (read only when needed)
- Requirements and open questions: `docs/requirements.md`
- Feature status, decisions and findings: `docs/project-requirements.md`. Private: it is in `.gitignore` and not tracked, so keep it out of commits and do not link to it from public files.
- Dependencies: `docs/dependencies.md`; third-party licence texts: `THIRD_PARTY_NOTICES.md`
- Architecture, layout, milestones, conventions and commands: `docs/architecture.md`

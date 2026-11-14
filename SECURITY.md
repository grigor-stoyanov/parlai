# Security Policy

## Supported versions

This is an early-stage personal project. Only the latest commit on the main branch is supported.

## Reporting a vulnerability

Please don't open a public issue for security problems.

Report privately through GitHub: the repository's **Security** tab, then **Report a vulnerability**. Include what you found, how to reproduce it, and what you think the impact is.

This is a spare-time project, so there is no guaranteed response time. I'll acknowledge reports as soon as I can.

## Security design

The app runs locally and is meant to stay that way. These rules apply to the code:

- **Local only:** no audio or transcripts are sent to cloud services by this app.
- **Localhost server:** the WebSocket server binds to `127.0.0.1` only, checks the `Origin` header, and requires a random per-run token. This blocks other web pages from connecting to it.
- **No auto-submit by default:** text injected into a terminal is not followed by Enter unless you opt in. Only AI CLIs are wrapped, never a bare shell.
- **No raw audio saved by default:** recordings are written only when a debug option asks for it.
- **Untrusted text:** AI replies and page content are only spoken, never executed or interpreted.
- **Dependencies:** versions are pinned in `uv.lock`; new dependencies need a concrete reason.

Note that if you point the wrapped CLI or web page at a cloud AI, what you say is sent to that service. That is outside this app's control.

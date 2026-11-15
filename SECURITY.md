# Security Policy

## Supported versions

This is an early-stage personal project. Only the latest release and the latest commit on the main branch are supported. Older releases, including v0.2.1 and earlier (the MIT-licensed ones), get no security fixes.

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
- **Dependencies:** versions are pinned in `uv.lock`. New dependencies need a concrete reason and a licence check (see [CLAUDE.md](CLAUDE.md)), and bundled libraries are listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). The binaries leave out libraries the app does not use, such as PyAV and FFmpeg, to keep the attack surface small.

## Binaries

Download binaries only from this repository's GitHub Releases. They are not code-signed, so Windows SmartScreen or an antivirus may warn about them. Builds are made by the manual GitHub Actions workflow from a tagged commit, and you can always build from source instead.

The app is licensed under PolyForm Noncommercial 1.0.0 (see [LICENSE](LICENSE)). Reporting a vulnerability does not need a licence and is always welcome, including from companies.

Note that if you point the wrapped CLI or web page at a cloud AI, what you say is sent to that service. That is outside this app's control.

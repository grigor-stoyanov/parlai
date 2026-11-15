"""Runtime hook: stand in for PyAV (`av`) in the built binaries.

faster-whisper does `import av` at the top of audio.py, but only uses it in `decode_audio`
(reading audio files). parlai passes microphone numpy arrays, so it never calls that. The real
`av` wheel carries FFmpeg with GPL-licensed codecs, which we do not want to ship, so the spec
excludes it and this stub only lets the import succeed. Any real use fails with a clear error.
"""

import sys
import types


class _MissingAv(types.ModuleType):
    def __getattr__(self, name: str):
        raise ImportError("PyAV (av) is not bundled in this parlai build; reading audio files is unsupported")


sys.modules["av"] = _MissingAv("av")

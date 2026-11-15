import os
import sys

from PyInstaller.utils.hooks import collect_data_files, copy_metadata

root = os.path.abspath(os.path.join(SPECPATH, ".."))

# Sound libraries come from the user's system, so they match their drivers and sound server.
# Only the system names are listed: libraries that wheels carry with them under a hashed name,
# such as PyAV's libasound-c7818c60.so, are not system libraries and must stay.
# On Windows the PortAudio DLL ships inside the sounddevice wheel, so that one stays too.
LINUX_SYSTEM_LIBS = ("libportaudio.so", "libasound.so", "libjack.so", "libdb-")

# Package metadata is only here so the startup log line can report versions.
LOGGED_PACKAGES = ("parlai", "faster-whisper", "ctranslate2", "onnxruntime", "sounddevice")

datas = [
    *collect_data_files("faster_whisper"),  # the Silero VAD model the detector loads
    *[item for name in LOGGED_PACKAGES for item in copy_metadata(name)],
]

# PyAV drags in FFmpeg with GPL codecs and we never decode audio files: leave it out and let the
# runtime hook stand in for it (see stub_av.py).
a = Analysis(
    [os.path.join(root, "main.py")],
    pathex=[os.path.join(root, "src")],
    datas=datas,
    excludes=["av"],
    runtime_hooks=[os.path.join(SPECPATH, "stub_av.py")],
)
if sys.platform.startswith("linux"):
    a.binaries = [b for b in a.binaries if not os.path.basename(b[0]).startswith(LINUX_SYSTEM_LIBS)]

pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="parlai", console=True)
coll = COLLECT(exe, a.binaries, a.datas, name="parlai")

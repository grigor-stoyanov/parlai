import os
import sys

root = os.path.abspath(os.path.join(SPECPATH, ".."))

# Sound libraries come from the user's system, so they match their drivers and sound server.
# On Windows the PortAudio DLL ships inside the sounddevice wheel, so that one stays.
LINUX_SYSTEM_LIBS = ("libportaudio", "libasound", "libjack", "libdb-")

a = Analysis([os.path.join(root, "main.py")], pathex=[os.path.join(root, "src")])
if sys.platform.startswith("linux"):
    a.binaries = [b for b in a.binaries if not os.path.basename(b[0]).startswith(LINUX_SYSTEM_LIBS)]

pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="parlai", console=True)
coll = COLLECT(exe, a.binaries, a.datas, name="parlai")

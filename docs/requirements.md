# System requirements

What a machine needs to run parlai. The built binaries and the project never install drivers, sound libraries or GPU libraries for you: parlai connects to what your machine already has, and its log says what is missing. What parlai should do (features and status) is in [project-requirements.md](project-requirements.md).

**Tested on:** Arch Linux (x86_64) with PipeWire, Python 3.12, 16 CPU cores, 30 GB RAM, NVIDIA RTX 5070 Laptop GPU (8 GB), driver 620.70.06. Everything marked "untested" below is what we expect to work but have not run.

## Any OS: hardware
- **CPU:** 64-bit x86 (x86_64). Speech recognition works on the CPU alone, no GPU needed. ARM builds are not made.
- **Memory:** about 1 GB of free RAM for the default `small.en` model (measured peak: 0.7 GB on the CPU, 0.95 GB with the GPU). Bigger models need more.
- **Disk:**
  - 0.5 GB for the speech model (464 MB for `small.en`), downloaded on first run
  - 420 MB for the unpacked Linux binary
  - up to 50 MB for logs by default (`PARLAI_LOG_MAX_MB`)
  - 2.1 GB more only if you install the NVIDIA libraries for the GPU
- **Microphone:** any input device the system can record from. Recording is mono, 16 kHz.
- **Speakers or headphones:** only for playing back (`--mic-check` now, spoken replies later).
- **Internet:** only to download the speech model once (about 464 MB, from huggingface.co) and to install. After that it works offline, and audio never leaves the machine.
- **GPU (optional):** an NVIDIA card with about 1 GB of free video memory for `small.en` (measured 716 MiB). AMD, Intel and Apple GPUs are not used for recognition and always run on the CPU.

## Linux
Tested on Arch with PipeWire.

Needed:
- A 64-bit x86 distribution. The prebuilt binary needs glibc 2.35 or newer: Debian 12, Ubuntu 22.04 and newer, current Fedora and Arch work. Debian 11 is too old.
- The PortAudio library: `libportaudio2` on Debian and Ubuntu, `portaudio` on Arch and Fedora. Without it the app stops at startup with a PortAudio error.
- A sound server with its ALSA bridge, so the right microphone is picked automatically: `pipewire-alsa` for PipeWire, `libasound2-plugins` (Debian, Ubuntu) or `pulseaudio-alsa` (Arch) for PulseAudio. Without the bridge only raw `hw:` devices appear, which can be busy or silent; set `PARLAI_INPUT_DEVICE` to choose one by hand.

For an NVIDIA GPU (optional):
- The proprietary NVIDIA driver, installed and working: `nvidia-smi` should list your card. It must be recent enough for CUDA 12; Blackwell cards such as the RTX 50 series need a new driver. Check NVIDIA's CUDA compatibility table for your card. The tested driver was 620.70.06.
- cuBLAS 12 and cuDNN 9, which are libraries and not part of the driver:
  - From a source checkout: `uv sync --extra cuda` (about 1.2 GB download).
  - For a binary: install them on the system so the loader finds them, or start it as `LD_LIBRARY_PATH=/folder/with/the/libs ./parlai/parlai`.
  - Arch's own `cuda` package is CUDA 13 and does not work with the speech engine we use.
- You do not need the full CUDA toolkit, a compiler or root.
- If any of it is missing, the log says why and the app runs on the CPU.

## Windows
Built by CI, not tested yet.

Expected to be needed:
- Windows 10 or 11, 64-bit.
- The Microsoft Visual C++ Redistributable (2015 to 2022, x64). The speech libraries usually need it. Not verified.
- Microphone access for desktop apps: Settings, Privacy and security, Microphone, "Let desktop apps access your microphone".

Not needed:
- PortAudio. It ships inside the app, since Windows has no system copy. Audio goes through Windows' own drivers.

For an NVIDIA GPU (optional, untested):
- The NVIDIA driver, and the CUDA 12 libraries (cuBLAS 12 and cuDNN 9, the `cublas64_12.dll` and `cudnn64_9.dll` files) in a folder on `PATH`.
- Without them the app logs a warning and runs on the CPU.

The exe is unsigned, so Windows SmartScreen or an antivirus may warn about it.

## macOS
Not built and not tested. Running from source may work on the CPU, with microphone permission granted to your terminal. There is no GPU support.

## Running from source (any OS)
- [uv](https://docs.astral.sh/uv/), which installs Python 3.12 for you. The project needs exactly Python 3.12.
- The same system libraries as above for your OS.
- `uv sync`, or `uv sync --extra cuda` for the NVIDIA libraries. A plain `uv sync` afterwards removes them again.

## Permissions and files
- Permission to record from the microphone (see the Windows and macOS notes).
- Write access to the folder you run it from: `logs/` for logs and `recordings/` for `--mic-check`. Both folders can be changed in `.env`.
- Network access to huggingface.co the first time, for the model. Nothing else goes over the network, and no ports are opened.

## Check your machine
Linux:
- `ldconfig -p | grep libportaudio` shows the PortAudio library.
- `wpctl status` (PipeWire) or `pactl info` (PulseAudio) shows a running sound server.
- `nvidia-smi` shows your GPU and driver, if you have one.
- Then `./parlai/parlai --mic-check` lists your devices, records and plays back.

Windows (PowerShell):
- `nvidia-smi` shows your GPU and driver, if you have one.
- Then `.\parlai\parlai.exe --mic-check`.

The log (`logs/parlai.log`) records which device and which speech model setup (CPU or GPU) was used, and why a GPU was skipped.

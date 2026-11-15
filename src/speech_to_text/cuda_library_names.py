"""Which CUDA 12 files to load from NVIDIA's pip packages (the `cuda` extra)."""

# Which libraries to load from each pip package, in the order they must be loaded:
# cuBLAS needs cuBLASLt, so that one goes first.
LIBRARIES = {
    "nvidia.cublas": {
        "linux": ("libcublasLt.so.12", "libcublas.so.12"),
        "win32": ("cublasLt64_12.dll", "cublas64_12.dll"),
    },
    "nvidia.cudnn": {
        "linux": ("libcudnn.so.9",),
        "win32": ("cudnn64_9.dll",),
    },
}

# The folder inside each package that holds the files.
LIBRARY_FOLDER = {"linux": "lib", "win32": "bin"}

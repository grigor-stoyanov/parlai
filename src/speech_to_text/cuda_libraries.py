"""Loads NVIDIA's CUDA 12 libraries from the `cuda` extra into this process only."""

import ctypes
import importlib.util
import logging
import os
import sys
from collections.abc import Mapping
from pathlib import Path

from event_logger.json_log import log_event
from speech_to_text.cuda_library_names import LIBRARIES, LIBRARY_FOLDER

logger = logging.getLogger(__name__)


def library_paths(package_dirs: Mapping[str, Path], platform: str) -> list[Path]:
    """
    The library files that exist, in load order.

    :param package_dirs: where each pip package from LIBRARIES is installed. Missing ones are left out.
    :param platform: "linux" or "win32".
    """
    found = []
    for package, names in LIBRARIES.items():
        if package not in package_dirs:
            continue
        folder = package_dirs[package] / LIBRARY_FOLDER[platform]
        found.extend(folder / name for name in names[platform] if (folder / name).exists())
    return found


def _installed_package_dirs() -> dict[str, Path]:
    dirs = {}
    for package in LIBRARIES:
        try:
            spec = importlib.util.find_spec(package)
        except ModuleNotFoundError:  # the whole "nvidia" namespace is missing
            continue
        if spec and spec.submodule_search_locations:
            dirs[package] = Path(next(iter(spec.submodule_search_locations)))
    return dirs


def preload() -> list[Path]:
    """
    Load the CUDA libraries that the `cuda` extra installed, so ctranslate2 finds them without
    LD_LIBRARY_PATH or PATH. This affects only this process, never other programs.

    :return: the files that were loaded. Empty if the extra is not installed.
    """
    platform = "win32" if sys.platform == "win32" else "linux"
    paths = library_paths(_installed_package_dirs(), platform)
    loaded = []
    for path in paths:
        try:
            if platform == "win32":
                os.add_dll_directory(str(path.parent))
            ctypes.CDLL(str(path), mode=ctypes.RTLD_GLOBAL if platform == "linux" else 0)
            loaded.append(path)
        except OSError as error:
            log_event(
                logger,
                logging.WARNING,
                "cuda_libraries",
                "could not load a CUDA library",
                file=path.name,
                reason=str(error),
            )
    if loaded:
        log_event(
            logger,
            logging.INFO,
            "cuda_libraries",
            "loaded CUDA libraries from the cuda extra",
            files=[path.name for path in loaded],
        )
    else:
        log_event(
            logger,
            logging.INFO,
            "cuda_libraries",
            "no CUDA libraries from the cuda extra, relying on the system's",
        )
    return loaded

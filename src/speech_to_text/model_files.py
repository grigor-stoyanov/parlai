"""Finds the speech model's files: a folder the user gave, the cache, or a fresh download."""

import logging
import time
from pathlib import Path

from faster_whisper.utils import download_model

from event_logger.json_log import log_event

logger = logging.getLogger(__name__)


def find_model(name: str) -> str:
    """
    Where the model files are.

    :param name: a faster-whisper model name such as "small.en", or a folder that holds a model.
    :return: the folder with the files. The first use of a name downloads it (needs internet).
    """
    if Path(name).is_dir():
        log_event(logger, logging.INFO, "model", "using model folder", path=name)
        return name
    try:
        path = download_model(name, local_files_only=True)
        log_event(logger, logging.INFO, "model", "using cached model", model=name, path=path)
    except FileNotFoundError:
        log_event(
            logger,
            logging.INFO,
            "model",
            "model not in cache, downloading (first run, needs internet)",
            model=name,
        )
        started = time.monotonic()
        path = download_model(name)
        log_event(
            logger,
            logging.INFO,
            "model",
            "model downloaded",
            model=name,
            path=path,
            seconds=round(time.monotonic() - started, 1),
        )
    return path

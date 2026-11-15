"""Log lines for starting up and exiting, so a log always says what ran and how it ended."""

import logging
import platform
import time
from dataclasses import asdict
from importlib import metadata

from config.settings import Settings
from event_logger.json_log import log_event

logger = logging.getLogger("parlai.lifecycle")

LIBRARIES = ("faster-whisper", "ctranslate2", "onnxruntime", "numpy", "sounddevice")


def _version(package: str) -> str:
    try:
        return metadata.version(package)
    except metadata.PackageNotFoundError:
        return "unknown"


def log_startup(settings: Settings) -> None:
    log_event(
        logger,
        logging.INFO,
        "startup",
        "parlai starting",
        version=_version("parlai"),
        python=platform.python_version(),
        platform=platform.platform(),
        libraries={name: _version(name) for name in LIBRARIES},
        settings=asdict(settings),
    )


def log_exit(reason: str, started_at: float) -> None:
    """
    :param reason: why we are exiting, for example "stopped by user" or "crashed".
    :param started_at: time.monotonic() from when the app started.
    """
    log_event(
        logger,
        logging.INFO,
        "exit",
        "parlai exiting",
        reason=reason,
        uptime_seconds=round(time.monotonic() - started_at, 1),
    )


def log_crash(error: BaseException) -> None:
    logger.error(
        "parlai crashed",
        exc_info=error,
        extra={"label": "error", "fields": {}},
    )

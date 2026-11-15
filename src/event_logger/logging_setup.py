"""Turns logging on: JSON lines into daily files, plus warnings and errors on the terminal."""

import logging
from pathlib import Path

from config.settings import Settings
from event_logger.json_log import JsonFormatter, log_event
from event_logger.log_files import DailyFileHandler, cleanup_logs
from event_logger.text_log import TextFormatter


def setup_logging(settings: Settings) -> Path:
    """
    Start logging to settings.log_dir at settings.log_level, and to the terminal at
    settings.log_console_level (OFF for none). Delete old files if they are too old or too big.

    :return: the folder the log files are in.
    """
    max_bytes = settings.log_max_mb * 1024 * 1024
    file_level = logging.getLevelNamesMapping()[settings.log_level]
    root = logging.getLogger()

    file_handler = DailyFileHandler(
        settings.log_dir, settings.log_name, max_bytes, settings.log_keep_days
    )
    file_handler.setLevel(file_level)
    file_handler.setFormatter(JsonFormatter() if settings.log_format == "json" else TextFormatter())
    root.addHandler(file_handler)
    root_level = file_level

    if settings.log_console_level != "OFF":
        console_level = logging.getLevelNamesMapping()[settings.log_console_level]
        console = logging.StreamHandler()
        console.setLevel(console_level)
        console.setFormatter(logging.Formatter("parlai: %(levelname)s %(message)s"))
        root.addHandler(console)
        root_level = min(file_level, console_level)
    # The root level is the lowest either handler needs; each handler then filters for itself.
    root.setLevel(root_level)

    for name in settings.log_quiet_loggers:
        logging.getLogger(name).setLevel(logging.WARNING)

    for path in cleanup_logs(
        settings.log_dir, settings.log_name, max_bytes, settings.log_keep_days
    ):
        log_event(
            logging.getLogger(__name__),
            logging.INFO,
            "cleanup",
            "deleted old log file",
            file=path.name,
        )
    return settings.log_dir

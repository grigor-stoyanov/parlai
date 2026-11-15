"""One JSON object per log line. Every line has a time, level, source and label."""

import json
import logging
from datetime import datetime
from typing import Any


def log_event(logger: logging.Logger, level: int, label: str, message: str, **fields: Any) -> None:
    """
    Write a log line with a short machine-readable label and extra fields.

    :param logger: its name becomes the line's source, for example speech_to_text.whisper_engine.
    :param label: what kind of line this is, for example startup, model, audio_device, error.
    :param fields: extra data for the line. Never put raw audio or transcripts here at INFO.
    """
    logger.log(level, message, extra={"label": label, "fields": fields})


def timestamp(record: logging.LogRecord) -> str:
    """When the record was made, in local time with the UTC offset."""
    return datetime.fromtimestamp(record.created).astimezone().isoformat(timespec="milliseconds")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        line: dict[str, Any] = {
            "time": timestamp(record),
            "level": record.levelname,
            "source": record.name,
            "label": getattr(record, "label", "log"),
            "message": record.getMessage(),
        }
        for key, value in getattr(record, "fields", {}).items():
            line.setdefault(key, value)
        if record.exc_info:
            line["error"] = f"{record.exc_info[0].__name__}: {record.exc_info[1]}"
            line["traceback"] = self.formatException(record.exc_info)
        return json.dumps(line, default=str)

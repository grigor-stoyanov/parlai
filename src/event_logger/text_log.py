"""The plain-text log format, for reading in a terminal instead of parsing."""

import json
import logging

from event_logger.json_log import timestamp


class TextFormatter(logging.Formatter):
    """For example: 2026-11-15T18:17:12.487+02:00 INFO    speech_to_text.whisper_engine [model] model loaded model="small.en" seconds=1.4"""

    def format(self, record: logging.LogRecord) -> str:
        parts = [
            timestamp(record),
            f"{record.levelname:<7}",
            record.name,
            f"[{getattr(record, 'label', 'log')}]",
            record.getMessage(),
        ]
        for key, value in getattr(record, "fields", {}).items():
            parts.append(f"{key}={json.dumps(value, default=str)}")
        line = " ".join(parts)
        if record.exc_info:
            line += "\n" + self.formatException(record.exc_info)
        return line

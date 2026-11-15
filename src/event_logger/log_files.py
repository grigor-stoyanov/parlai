"""Daily log files, and deleting the oldest ones when they pile up."""

import logging
from datetime import date, timedelta
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


def _file_date(path: Path, name: str) -> date | None:
    """The day a daily file covers, from its name (parlai-2026-11-15.log), or None."""
    try:
        return date.fromisoformat(path.stem[len(name) + 1 :])
    except ValueError:
        return None


def cleanup_logs(
    log_dir: Path, name: str, max_bytes: int, keep_days: int, today: date | None = None
) -> list[Path]:
    """
    Delete daily files older than keep_days, then the oldest ones until the folder fits max_bytes.
    Today's file (name.log) is never deleted, and files that are not this log's are left alone.

    :return: the files that were deleted.
    """
    today = today or date.today()
    daily = sorted(
        path for path in log_dir.glob(f"{name}-*.log") if _file_date(path, name) is not None
    )
    deleted = []

    for path in list(daily):
        if _file_date(path, name) < today - timedelta(days=keep_days):
            path.unlink()
            daily.remove(path)
            deleted.append(path)

    current = log_dir / f"{name}.log"
    total = sum(path.stat().st_size for path in daily)
    total += current.stat().st_size if current.exists() else 0
    while daily and total > max_bytes:
        oldest = daily.pop(0)
        total -= oldest.stat().st_size
        oldest.unlink()
        deleted.append(oldest)
    return deleted


class DailyFileHandler(TimedRotatingFileHandler):
    """Writes name.log, and at midnight renames it name-YYYY-MM-DD.log and cleans up."""

    def __init__(self, log_dir: Path, name: str, max_bytes: int, keep_days: int) -> None:
        log_dir.mkdir(parents=True, exist_ok=True)
        super().__init__(log_dir / f"{name}.log", when="midnight", encoding="utf-8")
        self.log_dir = log_dir
        self.name = name
        self.max_bytes = max_bytes
        self.keep_days = keep_days
        self.namer = self._daily_name

    @staticmethod
    def _daily_name(default_name: str) -> str:
        # The base class names it name.log.2026-11-15; we want name-2026-11-15.log.
        base, _, day = default_name.rpartition(".log.")
        return f"{base}-{day}.log"

    def doRollover(self) -> None:
        super().doRollover()
        for path in cleanup_logs(self.log_dir, self.name, self.max_bytes, self.keep_days):
            logging.getLogger(__name__).info("deleted old log file %s", path.name)

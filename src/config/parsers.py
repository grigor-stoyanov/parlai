"""Small readers for single environment variables. A bad value is added to `problems`."""

import math
from collections.abc import Mapping
from pathlib import Path

from config import rules


def positive_int(
    env: Mapping[str, str], name: str, default: int, problems: list[str]
) -> int | None:
    """Return the setting as a positive int, or None (and record a problem) if it is not one."""
    raw = env.get(name) or str(default)
    try:
        value = int(raw)
    except ValueError:
        value = 0
    if value <= 0:
        problems.append(rules.NOT_A_POSITIVE_NUMBER.violation(name, raw))
        return None
    return value


def whole_number(
    env: Mapping[str, str], name: str, default: int, problems: list[str]
) -> int | None:
    """Return the setting as an int that may be 0, or None (and record a problem) if it is not."""
    raw = env.get(name) or str(default)
    try:
        value = int(raw)
    except ValueError:
        value = -1
    if value < 0:
        problems.append(rules.NOT_A_WHOLE_NUMBER.violation(name, raw))
        return None
    return value


def gain(env: Mapping[str, str], name: str, problems: list[str]) -> float:
    """Return the setting as a positive finite float (default 1.0), or record a problem."""
    raw = (env.get(name) or "1.0").strip()
    try:
        value = float(raw)
    except ValueError:
        value = 0.0
    if not math.isfinite(value) or value <= 0:
        problems.append(rules.NOT_A_POSITIVE_GAIN.violation(name, raw))
        return 1.0
    return value


def choice(
    env: Mapping[str, str],
    name: str,
    default: str,
    allowed: tuple[str, ...],
    rule: rules.Rule,
    problems: list[str],
    *,
    upper: bool = False,
) -> str:
    """Return the setting if it is one of `allowed` (lower case, or upper case if asked)."""
    value = (env.get(name) or default).strip()
    value = value.upper() if upper else value.lower()
    if value not in allowed:
        problems.append(rule.violation(name, value, allowed=rules.join_with_or(allowed)))
    return value


def folder(env: Mapping[str, str], name: str, default: str, problems: list[str]) -> Path:
    """Return the setting as a path, and record a problem if it exists but is not a folder."""
    path = Path(env.get(name) or default)
    if path.exists() and not path.is_dir():
        problems.append(rules.NOT_A_FOLDER.violation(name, str(path)))
    return path


def logger_names(raw: str | None) -> tuple[str, ...]:
    """A comma-separated list of logger names. Empty means the default list, "none" means none."""
    if raw is None or not raw.strip():
        return rules.DEFAULT_QUIET_LOGGERS
    if raw.strip().lower() == "none":
        return ()
    return tuple(name.strip() for name in raw.split(",") if name.strip())

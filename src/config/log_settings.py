"""The logging settings: where the files go, how much is kept, and what is written."""

import re
from collections.abc import Mapping
from typing import Any

from config import parsers, rules


def read_log_settings(env: Mapping[str, str], problems: list[str]) -> dict[str, Any]:
    log_name = (env.get("PARLAI_LOG_NAME") or rules.DEFAULT_LOG_NAME).strip()
    if not re.fullmatch(rules.LOG_NAME_PATTERN, log_name):
        problems.append(rules.LOG_NAME.violation("PARLAI_LOG_NAME", log_name))

    return {
        "log_dir": parsers.folder(env, "PARLAI_LOG_DIR", "logs", problems),
        "log_level": parsers.choice(
            env,
            "PARLAI_LOG_LEVEL",
            rules.DEFAULT_LOG_LEVEL,
            rules.ALLOWED_LOG_LEVELS,
            rules.LOG_LEVEL,
            problems,
            upper=True,
        ),
        "log_max_mb": parsers.positive_int(
            env, "PARLAI_LOG_MAX_MB", rules.DEFAULT_LOG_MAX_MB, problems
        ),
        "log_keep_days": parsers.positive_int(
            env, "PARLAI_LOG_KEEP_DAYS", rules.DEFAULT_LOG_KEEP_DAYS, problems
        ),
        "log_console_level": parsers.choice(
            env,
            "PARLAI_LOG_CONSOLE_LEVEL",
            rules.DEFAULT_LOG_CONSOLE_LEVEL,
            rules.ALLOWED_CONSOLE_LEVELS,
            rules.LOG_CONSOLE_LEVEL,
            problems,
            upper=True,
        ),
        "log_name": log_name,
        "log_format": parsers.choice(
            env,
            "PARLAI_LOG_FORMAT",
            rules.DEFAULT_LOG_FORMAT,
            rules.ALLOWED_LOG_FORMATS,
            rules.LOG_FORMAT,
            problems,
        ),
        "log_quiet_loggers": parsers.logger_names(env.get("PARLAI_LOG_QUIET_LOGGERS")),
    }

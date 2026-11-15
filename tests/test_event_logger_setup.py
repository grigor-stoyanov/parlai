import json
import logging
from datetime import date, timedelta

import pytest

from config.settings import load_settings
from event_logger.lifecycle import _version, log_exit
from event_logger.logging_setup import setup_logging


@pytest.fixture
def clean_root_logger():
    root = logging.getLogger()
    before, level = list(root.handlers), root.level
    yield
    for handler in root.handlers[:]:
        if handler not in before:
            handler.close()
            root.removeHandler(handler)
    root.setLevel(level)


def test_setup_creates_the_log_file_and_writes_json_lines(tmp_path, clean_root_logger):
    setup_logging(load_settings({"PARLAI_LOG_DIR": str(tmp_path / "logs")}))

    log_exit("finished", 0.0)

    line = json.loads((tmp_path / "logs" / "parlai.log").read_text().splitlines()[-1])
    assert (line["label"], line["reason"]) == ("exit", "finished")


def test_setup_deletes_old_files_when_the_folder_is_too_big(tmp_path, clean_root_logger):
    logs = tmp_path / "logs"
    logs.mkdir()
    old = logs / f"parlai-{date.today() - timedelta(days=1)}.log"
    old.write_text("x" * 2 * 1024 * 1024)

    setup_logging(load_settings({"PARLAI_LOG_DIR": str(logs), "PARLAI_LOG_MAX_MB": "1"}))

    assert not old.exists()


def test_the_log_level_setting_is_applied(tmp_path, clean_root_logger):
    setup_logging(load_settings({"PARLAI_LOG_DIR": str(tmp_path), "PARLAI_LOG_LEVEL": "DEBUG"}))

    assert logging.getLogger().level == logging.DEBUG


def test_an_unknown_package_version_is_reported_as_unknown():
    assert _version("no-such-package-xyz") == "unknown"


def test_files_older_than_the_keep_days_setting_are_deleted(tmp_path, clean_root_logger):
    logs = tmp_path / "logs"
    logs.mkdir()
    old = logs / f"parlai-{date.today() - timedelta(days=5)}.log"
    recent = logs / f"parlai-{date.today() - timedelta(days=1)}.log"
    old.write_text("x")
    recent.write_text("x")

    setup_logging(load_settings({"PARLAI_LOG_DIR": str(logs), "PARLAI_LOG_KEEP_DAYS": "3"}))

    assert not old.exists()
    assert recent.exists()


def test_the_console_level_off_adds_no_terminal_output(tmp_path, clean_root_logger):
    before = len(logging.getLogger().handlers)

    setup_logging(
        load_settings({"PARLAI_LOG_DIR": str(tmp_path), "PARLAI_LOG_CONSOLE_LEVEL": "OFF"})
    )

    assert len(logging.getLogger().handlers) == before + 1


def test_the_console_shows_warnings_by_default(tmp_path, clean_root_logger):
    before = len(logging.getLogger().handlers)

    setup_logging(load_settings({"PARLAI_LOG_DIR": str(tmp_path)}))

    handlers = logging.getLogger().handlers[before:]
    assert [h.level for h in handlers if type(h) is logging.StreamHandler] == [logging.WARNING]


def test_a_chatty_console_does_not_make_the_file_chattier(tmp_path, clean_root_logger):
    setup_logging(
        load_settings(
            {
                "PARLAI_LOG_DIR": str(tmp_path),
                "PARLAI_LOG_LEVEL": "WARNING",
                "PARLAI_LOG_CONSOLE_LEVEL": "DEBUG",
            }
        )
    )

    logging.getLogger("some.module").info("this must not reach the file")
    logging.getLogger("some.module").warning("this must")

    lines = (tmp_path / "parlai.log").read_text().splitlines()
    assert [json.loads(line)["message"] for line in lines] == ["this must"]


def test_the_text_format_writes_plain_lines_not_json(tmp_path, clean_root_logger):
    setup_logging(load_settings({"PARLAI_LOG_DIR": str(tmp_path), "PARLAI_LOG_FORMAT": "text"}))

    log_exit("finished", 0.0)

    line = (tmp_path / "parlai.log").read_text().splitlines()[-1]
    assert "[exit]" in line
    assert not line.startswith("{")


def test_a_custom_log_name_names_the_file(tmp_path, clean_root_logger):
    setup_logging(load_settings({"PARLAI_LOG_DIR": str(tmp_path), "PARLAI_LOG_NAME": "myapp"}))

    log_exit("finished", 0.0)

    assert (tmp_path / "myapp.log").exists()
    assert not (tmp_path / "parlai.log").exists()


def test_the_quiet_loggers_setting_turns_those_loggers_down_to_warnings(
    tmp_path, clean_root_logger
):
    setup_logging(
        load_settings({"PARLAI_LOG_DIR": str(tmp_path), "PARLAI_LOG_QUIET_LOGGERS": "chatty.lib"})
    )

    assert logging.getLogger("chatty.lib").level == logging.WARNING

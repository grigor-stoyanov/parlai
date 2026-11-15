import json
import logging

from event_logger.json_log import JsonFormatter, log_event


def format_record(**kwargs):
    record = logging.LogRecord("some.source", logging.INFO, __file__, 1, "hello", None, None)
    for key, value in kwargs.items():
        setattr(record, key, value)
    return json.loads(JsonFormatter().format(record))


def test_every_line_has_time_level_source_label_and_message():
    line = format_record(label="startup")

    assert set(line) == {"time", "level", "source", "label", "message"}
    assert line["level"] == "INFO"
    assert line["source"] == "some.source"
    assert line["label"] == "startup"
    assert line["message"] == "hello"


def test_a_plain_log_call_gets_the_default_label():
    assert format_record()["label"] == "log"


def test_extra_fields_are_added_to_the_line():
    assert format_record(fields={"chars": 5})["chars"] == 5


def test_fields_cannot_overwrite_the_core_keys():
    assert (
        format_record(label="startup", fields={"label": "spoofed", "level": "FAKE"})["label"]
        == "startup"
    )


def test_an_exception_adds_the_error_and_traceback():
    try:
        raise ValueError("broke")
    except ValueError:
        import sys

        record = logging.LogRecord("s", logging.ERROR, __file__, 1, "crashed", None, sys.exc_info())
    line = json.loads(JsonFormatter().format(record))

    assert line["error"] == "ValueError: broke"
    assert "Traceback" in line["traceback"]


def test_log_event_passes_the_label_and_fields_to_the_logger(caplog):
    with caplog.at_level(logging.INFO, logger="test.logger"):
        log_event(logging.getLogger("test.logger"), logging.INFO, "model", "loaded", seconds=1.5)

    record = caplog.records[0]
    assert (record.label, record.fields) == ("model", {"seconds": 1.5})

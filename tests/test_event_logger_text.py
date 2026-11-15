import logging
import sys

from event_logger.text_log import TextFormatter


def record(label="model", fields=None, exc_info=None):
    made = logging.LogRecord("some.source", logging.WARNING, __file__, 1, "loaded", None, exc_info)
    made.label = label
    made.fields = fields or {}
    return made


def test_a_line_reads_time_level_source_label_message_then_fields():
    line = TextFormatter().format(record(fields={"model": "small.en", "seconds": 1.5}))

    time, level, source, label, message, *fields = line.split(" ")
    assert (level, source, label, message) == ("WARNING", "some.source", "[model]", "loaded")
    assert fields == ['model="small.en"', "seconds=1.5"]
    assert "T" in time


def test_an_exception_is_added_below_the_line():
    try:
        raise ValueError("broke")
    except ValueError:
        line = TextFormatter().format(record(exc_info=sys.exc_info()))

    first, _, rest = line.partition("\n")
    assert first.endswith("loaded")
    assert "ValueError: broke" in rest


def test_a_plain_log_call_gets_the_default_label():
    plain = logging.LogRecord("s", logging.INFO, __file__, 1, "hi", None, None)

    assert "[log]" in TextFormatter().format(plain)

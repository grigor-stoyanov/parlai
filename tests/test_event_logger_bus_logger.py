import logging

from event_bus.bus import EventBus
from event_bus.events import FinalText, SpeechStart
from event_logger.bus_logger import EventLogger


def logged(caplog):
    return [(r.label, r.fields) for r in caplog.records if r.name == "parlai.events"]


def test_an_event_is_logged_with_its_type_as_the_label(caplog):
    with caplog.at_level(logging.INFO, logger="parlai.events"):
        EventLogger(EventBus()).log(SpeechStart())

    assert logged(caplog) == [("SpeechStart", {})]


def test_the_transcript_is_hidden_by_default_even_when_debug_logging_is_enabled(caplog):
    with caplog.at_level(logging.DEBUG, logger="parlai.events"):
        EventLogger(EventBus()).log(FinalText("my secret words"))

    assert logged(caplog) == [("FinalText", {"chars": 15})]


def test_the_transcript_is_logged_only_when_include_text_is_on(caplog):
    with caplog.at_level(logging.DEBUG, logger="parlai.events"):
        EventLogger(EventBus(), include_text=True).log(FinalText("my secret words"))

    assert logged(caplog) == [("FinalText", {"chars": 15, "text": "my secret words"})]


def test_events_published_on_the_bus_are_logged_after_start_and_stop(caplog):
    bus = EventBus()
    event_logger = EventLogger(bus)
    with caplog.at_level(logging.INFO, logger="parlai.events"):
        event_logger.start()
        bus.publish(SpeechStart())
        bus.publish(FinalText("hi"))
        event_logger.stop()

    assert [label for label, _ in logged(caplog)] == ["SpeechStart", "FinalText"]

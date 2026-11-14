from event_bus.bus import EventBus
from event_bus.events import FinalText, PartialText


def test_subscriber_gets_published_event():
    bus = EventBus()
    inbox = bus.subscribe(FinalText)

    bus.publish(FinalText("hello"))

    assert inbox.get_nowait() == FinalText("hello")


def test_subscriber_only_gets_its_event_type():
    bus = EventBus()
    inbox = bus.subscribe(FinalText)

    bus.publish(PartialText("hel"))

    assert inbox.empty()


def test_every_subscriber_gets_a_copy():
    bus = EventBus()
    first = bus.subscribe(FinalText)
    second = bus.subscribe(FinalText)

    bus.publish(FinalText("hello"))

    assert first.get_nowait() == FinalText("hello")
    assert second.get_nowait() == FinalText("hello")


def test_events_arrive_in_order():
    bus = EventBus()
    inbox = bus.subscribe(PartialText)

    bus.publish(PartialText("a"))
    bus.publish(PartialText("b"))

    assert inbox.get_nowait() == PartialText("a")
    assert inbox.get_nowait() == PartialText("b")


def test_publish_without_subscribers_is_fine():
    EventBus().publish(FinalText("nobody is listening"))

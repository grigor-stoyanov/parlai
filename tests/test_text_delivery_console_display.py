import io

from event_bus.events import FinalText, PartialText, SpeechStart
from text_delivery.console_display import ConsoleDisplay


def make_display(width=20):
    out = io.StringIO()
    return ConsoleDisplay(out, width=lambda: width), out


def test_a_partial_is_drawn_from_the_start_of_the_line_without_a_newline():
    display, out = make_display()

    display.show_partial("hello")

    assert out.getvalue() == "\rhello"


def test_a_shorter_partial_covers_the_longer_one_before_it():
    display, out = make_display()

    display.show_partial("hello there")
    display.show_partial("hi")

    assert out.getvalue() == "\rhello there" + "\rhi" + " " * 9


def test_a_longer_partial_needs_no_cover():
    display, out = make_display()

    display.show_partial("hi")
    display.show_partial("hello")

    assert out.getvalue() == "\rhi\rhello"


def test_the_final_text_replaces_the_live_line_and_ends_it_with_a_newline():
    display, out = make_display()

    display.show_partial("hello the")
    display.show_final("hello there")

    assert out.getvalue() == "\rhello the\rhello there\n"


def test_a_shorter_final_covers_the_longer_partial():
    display, out = make_display()

    display.show_partial("hello there my")
    display.show_final("hello there")

    assert out.getvalue() == "\rhello there my\rhello there   \n"


def test_the_next_partial_after_a_final_does_not_cover_anything():
    display, out = make_display()

    display.show_partial("hello there")
    display.show_final("hello")
    display.show_partial("a")

    assert out.getvalue().endswith("\n\ra")


def test_a_final_with_no_partial_before_it_is_just_the_text_and_a_newline():
    display, out = make_display()

    display.show_final("hello")

    assert out.getvalue() == "\rhello\n"


def test_a_partial_longer_than_the_line_shows_only_its_last_words():
    display, out = make_display(width=20)

    display.show_partial("one two three four five six")

    shown = out.getvalue().removeprefix("\r")
    assert shown.startswith("…")
    assert shown.endswith("five six")
    assert len(shown) == 19  # one short of the width, so the line never wraps


def test_a_final_longer_than_the_line_is_shown_in_full():
    display, out = make_display(width=10)

    display.show_final("a long sentence that wraps")

    assert out.getvalue() == "\ra long sentence that wraps\n"


def test_an_empty_final_clears_the_live_line_without_a_newline():
    display, out = make_display()

    display.show_partial("noise")
    display.show_final("  ")

    assert out.getvalue() == "\rnoise\r" + " " * 5
    assert "\n" not in out.getvalue()


def test_handle_shows_partial_and_final_events_and_ignores_others():
    display, out = make_display()

    display.handle(SpeechStart())
    display.handle(PartialText("hel"))
    display.handle(FinalText("hello"))

    assert out.getvalue() == "\rhel\rhello\n"

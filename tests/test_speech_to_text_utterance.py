from event_bus.bus import EventBus
from event_bus.events import SpeechEnd, SpeechStart
from speech_to_text.utterance_segmenter import UtteranceSegmenter


def make_segmenter(silence_chunks_to_end=3):
    bus = EventBus()
    starts = bus.subscribe(SpeechStart)
    ends = bus.subscribe(SpeechEnd)
    return UtteranceSegmenter(bus, silence_chunks_to_end), starts, ends


def feed(segmenter, chunks):
    for chunk in chunks:
        segmenter.feed(chunk == "S")


def test_silence_alone_publishes_nothing():
    segmenter, starts, ends = make_segmenter()

    feed(segmenter, "......")

    assert starts.qsize() == 0
    assert ends.qsize() == 0


def test_first_speech_publishes_one_start():
    segmenter, starts, ends = make_segmenter()

    feed(segmenter, "SSS")

    assert starts.qsize() == 1
    assert ends.qsize() == 0


def test_short_gap_does_not_end_the_utterance():
    segmenter, starts, ends = make_segmenter(silence_chunks_to_end=3)

    feed(segmenter, "SS..S")

    assert starts.qsize() == 1
    assert ends.qsize() == 0


def test_not_enough_silence_does_not_end():
    segmenter, starts, ends = make_segmenter(silence_chunks_to_end=3)

    feed(segmenter, "SS..")

    assert ends.qsize() == 0


def test_enough_silence_ends_the_utterance():
    segmenter, starts, ends = make_segmenter(silence_chunks_to_end=3)

    feed(segmenter, "SS...")

    assert ends.qsize() == 1


def test_speech_after_the_end_starts_a_new_utterance():
    segmenter, starts, ends = make_segmenter(silence_chunks_to_end=3)

    feed(segmenter, "S...S")

    assert starts.qsize() == 2
    assert ends.qsize() == 1


def test_more_silence_after_the_end_publishes_nothing_more():
    segmenter, starts, ends = make_segmenter(silence_chunks_to_end=3)

    feed(segmenter, "S.......")

    assert ends.qsize() == 1


def make_capped(max_chunks, silence_chunks_to_end=3):
    bus = EventBus()
    starts = bus.subscribe(SpeechStart)
    ends = bus.subscribe(SpeechEnd)
    return UtteranceSegmenter(bus, silence_chunks_to_end, max_chunks), starts, ends


def test_there_is_no_limit_by_default():
    segmenter, starts, ends = make_segmenter()

    feed(segmenter, "S" * 1000)

    assert starts.qsize() == 1
    assert ends.qsize() == 0


def test_reaching_the_limit_while_speaking_ends_and_starts_a_new_utterance():
    segmenter, starts, ends = make_capped(max_chunks=4)

    feed(segmenter, "SSSS")

    assert ends.qsize() == 1
    assert starts.qsize() == 2


def test_one_chunk_short_of_the_limit_changes_nothing():
    segmenter, starts, ends = make_capped(max_chunks=4)

    feed(segmenter, "SSS")

    assert ends.qsize() == 0
    assert starts.qsize() == 1


def test_the_limit_counts_again_from_the_new_utterance():
    segmenter, starts, ends = make_capped(max_chunks=4)

    feed(segmenter, "SSSSSSSS")

    assert ends.qsize() == 2
    assert starts.qsize() == 3


def test_reaching_the_limit_during_a_pause_ends_without_starting_a_new_one():
    segmenter, starts, ends = make_capped(max_chunks=4)

    feed(segmenter, "SSS.")

    assert ends.qsize() == 1
    assert starts.qsize() == 1


def test_speech_after_a_limit_in_a_pause_starts_a_new_utterance():
    segmenter, starts, _ends = make_capped(max_chunks=4)

    feed(segmenter, "SSS.S")

    assert starts.qsize() == 2


def test_a_normal_end_before_the_limit_resets_the_count():
    segmenter, starts, ends = make_capped(max_chunks=6, silence_chunks_to_end=2)

    feed(segmenter, "SS..SS")

    assert ends.qsize() == 1
    assert starts.qsize() == 2

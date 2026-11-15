import threading
import time

from speech_to_text.transcription_worker import TranscriptionWorker


class EchoEngine:
    """Returns the audio as text, so a test can see what came out and in which order."""

    def transcribe(self, audio):
        return audio.decode()


class BlockedEngine:
    """Holds every transcription until the test lets it go, and says when one has begun."""

    def __init__(self):
        self.began = threading.Event()
        self.release = threading.Event()

    def transcribe(self, audio):
        self.began.set()
        self.release.wait(timeout=5)
        return audio.decode()


class FailsOnceEngine:
    def __init__(self):
        self.calls = 0

    def transcribe(self, audio):
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("model failed")
        return audio.decode()


def wait_for(results, expected, seconds=5):
    """Wait until the results are what we expect. Partials are not covered by stop()."""
    deadline = time.monotonic() + seconds
    while results != expected and time.monotonic() < deadline:
        time.sleep(0.01)
    return results == expected


def make_worker(engine):
    """A worker whose results all land in one list, tagged as final or partial."""
    results = []
    worker = TranscriptionWorker(
        engine,
        on_final=lambda text: results.append(("final", text)),
        on_partial=lambda text: results.append(("partial", text)),
    )
    return worker, results


def busy_worker():
    """A started worker that is in the middle of a job it cannot finish until released."""
    engine = BlockedEngine()
    worker, results = make_worker(engine)
    worker.start()
    worker.submit_final(b"running")
    assert engine.began.wait(timeout=5)
    return worker, engine, results


def test_final_texts_come_out_in_the_order_they_were_submitted():
    worker, results = make_worker(EchoEngine())
    worker.start()

    for word in (b"one", b"two", b"three"):
        worker.submit_final(word)
    worker.stop()

    assert results == [("final", "one"), ("final", "two"), ("final", "three")]


def test_submit_returns_while_the_engine_is_still_busy():
    worker, engine, results = busy_worker()  # would hang here if submit waited for the engine

    assert results == []
    engine.release.set()
    worker.stop()
    assert results == [("final", "running")]


def test_the_engine_runs_on_the_worker_thread_not_the_caller():
    threads = []

    class Engine:
        def transcribe(self, audio):
            threads.append(threading.current_thread())
            return ""

    worker, _ = make_worker(Engine())
    worker.start()
    worker_thread = worker.thread
    worker.submit_final(b"x")
    worker.stop()

    assert threads == [worker_thread]
    assert worker_thread is not threading.main_thread()


def test_stop_finishes_every_final_already_submitted():
    worker, results = make_worker(EchoEngine())
    worker.start()

    for number in range(20):
        worker.submit_final(str(number).encode())
    worker.stop()

    assert len(results) == 20


def test_a_partial_goes_to_the_partial_callback():
    worker, results = make_worker(EchoEngine())
    worker.start()

    worker.submit_partial(b"hel")

    assert wait_for(results, [("partial", "hel")])
    worker.stop()


def test_a_newer_partial_replaces_one_that_is_still_waiting():
    worker, engine, results = busy_worker()

    worker.submit_partial(b"old")
    worker.submit_partial(b"new")
    engine.release.set()

    assert wait_for(results, [("final", "running"), ("partial", "new")])
    worker.stop()


def test_submitting_a_final_cancels_a_waiting_partial():
    worker, engine, results = busy_worker()

    worker.submit_partial(b"partial")
    worker.submit_final(b"second")
    engine.release.set()
    worker.stop()

    # the final replaced the stale partial, and nothing of it is left to show afterwards
    assert results == [("final", "running"), ("final", "second")]


def test_a_partial_submitted_after_a_waiting_final_still_runs_after_it():
    worker, engine, results = busy_worker()

    worker.submit_final(b"second")
    worker.submit_partial(b"live")
    engine.release.set()

    assert wait_for(results, [("final", "running"), ("final", "second"), ("partial", "live")])
    worker.stop()


def test_a_failing_job_is_skipped_and_the_next_one_still_works():
    worker, results = make_worker(FailsOnceEngine())
    worker.start()

    worker.submit_final(b"lost")
    worker.submit_final(b"kept")
    worker.stop()

    assert results == [("final", "kept")]


def test_a_failing_job_is_logged_without_its_audio(caplog):
    worker, _ = make_worker(FailsOnceEngine())
    worker.start()

    worker.submit_final(b"secret words")
    worker.stop()

    record = next(r for r in caplog.records if r.getMessage() == "transcription failed")
    assert record.fields == {"audio_bytes": len(b"secret words")}
    assert "secret words" not in caplog.text


def test_stop_without_start_does_nothing():
    worker, _ = make_worker(EchoEngine())

    worker.stop()

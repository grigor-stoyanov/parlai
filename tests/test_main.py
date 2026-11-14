from main import main


def run_main(capsys):
    main([], pause=0)
    return capsys.readouterr().out.splitlines()


def test_two_utterances_produce_two_starts_and_two_ends(capsys):
    lines = run_main(capsys)

    events = [line.strip() for line in lines if "->" in line]

    assert events == ["-> SpeechStart()", "-> SpeechEnd()", "-> SpeechStart()", "-> SpeechEnd()"]


def test_events_appear_right_after_the_chunk_that_caused_them(capsys):
    lines = run_main(capsys)

    assert lines[lines.index(" 2 S") + 1] == "   -> SpeechStart()"
    assert lines[lines.index("11 .") + 1] == "   -> SpeechEnd()"


def test_a_short_gap_does_not_publish_an_end(capsys):
    lines = run_main(capsys)

    assert lines[lines.index(" 5 .") + 1] == " 6 ."
    assert lines[lines.index(" 6 .") + 1] == " 7 S"

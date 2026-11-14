from main import main


def test_each_subscriber_gets_only_its_own_event_type(capsys):
    main([], pause=0)

    lines = capsys.readouterr().out.splitlines()

    assert "terminal got: FinalText(text='Hello world')" in lines
    assert "browser got: PartialText(text='Hello')" in lines
    assert not any(line.startswith("terminal got: PartialText") for line in lines)
    assert not any(line.startswith("browser got: FinalText") for line in lines)


def test_nothing_is_read_until_publishing_is_done(capsys):
    main([], pause=0)

    lines = capsys.readouterr().out.splitlines()
    first_read = next(i for i, line in enumerate(lines) if "got:" in line)
    last_publish = max(i for i, line in enumerate(lines) if line.startswith("published"))

    assert last_publish < first_read

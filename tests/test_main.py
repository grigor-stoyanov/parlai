from main import main


def test_main_runs(capsys):
    main([])
    assert "scaffold" in capsys.readouterr().out

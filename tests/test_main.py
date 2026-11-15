import pytest
from main import main


def test_invalid_settings_stop_the_app_with_a_clear_message(capsys, monkeypatch):
    monkeypatch.setenv("PARLAI_SAMPLE_RATE", "abc")

    with pytest.raises(SystemExit) as exit_info:
        main([])

    assert exit_info.value.code == 2
    assert "PARLAI_SAMPLE_RATE" in capsys.readouterr().err

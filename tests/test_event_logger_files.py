from datetime import date

from event_logger.log_files import DailyFileHandler, cleanup_logs

TODAY = date(2026, 11, 15)


def make(folder, name, size=10):
    path = folder / name
    path.write_text("x" * size)
    return path


def test_files_older_than_the_keep_days_are_deleted(tmp_path):
    old = make(tmp_path, "parlai-2026-11-01.log")
    recent = make(tmp_path, "parlai-2026-11-14.log")

    deleted = cleanup_logs(tmp_path, "parlai", max_bytes=10_000, keep_days=7, today=TODAY)

    assert deleted == [old]
    assert recent.exists()


def test_the_oldest_files_go_first_when_the_folder_is_too_big(tmp_path):
    oldest = make(tmp_path, "parlai-2026-11-12.log", 100)
    middle = make(tmp_path, "parlai-2026-11-13.log", 100)
    newest = make(tmp_path, "parlai-2026-11-14.log", 100)

    deleted = cleanup_logs(tmp_path, "parlai", max_bytes=250, keep_days=14, today=TODAY)

    assert deleted == [oldest]
    assert middle.exists() and newest.exists()


def test_todays_file_counts_towards_the_size_but_is_never_deleted(tmp_path):
    today_file = make(tmp_path, "parlai.log", 500)
    yesterday = make(tmp_path, "parlai-2026-11-14.log", 100)

    deleted = cleanup_logs(tmp_path, "parlai", max_bytes=300, keep_days=14, today=TODAY)

    assert deleted == [yesterday]
    assert today_file.exists()


def test_files_that_are_not_daily_logs_are_left_alone(tmp_path):
    other = make(tmp_path, "notes.log", 10_000)
    odd = make(tmp_path, "parlai-latest.log", 10_000)

    assert cleanup_logs(tmp_path, "parlai", max_bytes=1, keep_days=14, today=TODAY) == []
    assert other.exists() and odd.exists()


def test_a_folder_that_fits_is_left_alone(tmp_path):
    make(tmp_path, "parlai-2026-11-14.log", 100)

    assert cleanup_logs(tmp_path, "parlai", max_bytes=1000, keep_days=14, today=TODAY) == []


def test_rolled_files_are_named_with_the_date_before_the_extension():
    assert (
        DailyFileHandler._daily_name("logs/parlai.log.2026-11-15") == "logs/parlai-2026-11-15.log"
    )


def test_cleanup_only_touches_files_of_its_own_log_name(tmp_path):
    mine = make(tmp_path, "parlai-2026-11-01.log")
    other = make(tmp_path, "other-2026-11-01.log")

    deleted = cleanup_logs(tmp_path, "parlai", max_bytes=10_000, keep_days=7, today=TODAY)

    assert deleted == [mine]
    assert other.exists()


def test_a_custom_log_name_is_used_for_the_current_file_and_the_daily_files(tmp_path):
    current = make(tmp_path, "myapp.log", 500)
    old = make(tmp_path, "myapp-2026-11-14.log", 100)

    deleted = cleanup_logs(tmp_path, "myapp", max_bytes=300, keep_days=14, today=TODAY)

    assert deleted == [old]
    assert current.exists()

from datetime import datetime, timezone

from app.main import czas_polski


def test_czas_polski_zima():
    czas = datetime(2026, 10, 29, 9, 0, tzinfo=timezone.utc)
    assert czas_polski(czas) == "29.10.2026 10:00"


def test_czas_polski_lato():
    czas = datetime(2026, 7, 15, 9, 0, tzinfo=timezone.utc)
    assert czas_polski(czas) == "15.07.2026 11:00"


def test_czas_polski_brak_terminu():
    assert czas_polski(None) == "brak"

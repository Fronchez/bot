"""Configuration tests."""

from app.core.config import Settings


def test_admin_ids_csv_parsing() -> None:
    settings = Settings(telegram_admin_ids="1,2, 3")
    assert settings.telegram_admin_ids == [1, 2, 3]

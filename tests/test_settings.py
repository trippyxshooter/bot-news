import pytest
from app.config import Settings


def test_admin_ids_json():
    s = Settings(
        TELEGRAM_TOKEN="123:abc",
        TG_CHANNEL_ID="test",
        ADMIN_IDS='["1","2"]',
        OPENAI_API_KEY="key",
        GOOGLE_API_KEY="key"
    )
    assert s.get_admin_ids() == ["1", "2"]

def test_admin_ids_single():
    s = Settings(
        TELEGRAM_TOKEN="123:abc",
        TG_CHANNEL_ID="test",
        ADMIN_IDS='["1"]',
        OPENAI_API_KEY="key",
        GOOGLE_API_KEY="key"
    )
    assert s.get_admin_ids() == ["1"]

def test_admin_ids_invalid():
    s = Settings(
        TELEGRAM_TOKEN="123:abc",
        TG_CHANNEL_ID="test",
        ADMIN_IDS='notalist',
        OPENAI_API_KEY="key",
        GOOGLE_API_KEY="key"
    )
    assert s.get_admin_ids() == [] 
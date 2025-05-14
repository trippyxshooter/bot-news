import pytest
from app.bot import NewsBot
from app.config import Settings

@pytest.fixture
def bot():
    settings = Settings(
        TELEGRAM_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
        TG_CHANNEL_ID="test_channel",
        ADMIN_IDS='["123"]',
        OPENAI_API_KEY="test_key",
        GOOGLE_API_KEY="test_key"
    )
    return NewsBot(settings)

def test_settings():
    settings = Settings()
    assert settings.TELEGRAM_TOKEN is not None
    assert settings.TG_CHANNEL_ID is not None
    assert settings.ADMIN_IDS is not None

def test_bot_initialization():
    settings = Settings(
        TELEGRAM_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
        TG_CHANNEL_ID="test_channel",
        ADMIN_IDS='["123"]',
        OPENAI_API_KEY="test_key",
        GOOGLE_API_KEY="test_key"
    )
    bot = NewsBot(settings)
    assert bot.settings == settings
    assert bot.bot.token == settings.TELEGRAM_TOKEN
    assert bot is not None 
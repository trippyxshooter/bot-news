import pytest
from app.bot import NewsBot
from app.config import Settings
from aiogram.types import Message, User
import asyncio

class DummyMessage:
    def __init__(self, user_id, text):
        self.from_user = type('User', (), {'id': user_id})()
        self.text = text
        self.reply_text = None
    async def reply(self, text):
        self.reply_text = text

@pytest.mark.asyncio
async def test_admin_access():
    settings = Settings(
        TELEGRAM_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
        TG_CHANNEL_ID="test_channel",
        ADMIN_IDS='["42"]',
        OPENAI_API_KEY="key",
        GOOGLE_API_KEY="key"
    )
    bot = NewsBot(settings)
    msg = DummyMessage(user_id=42, text="/stats")
    await bot.handle_admin_command(msg)
    # Якщо адмін, не має бути відмови
    assert msg.reply_text is None or "доступу" not in msg.reply_text

@pytest.mark.asyncio
async def test_non_admin_access():
    settings = Settings(
        TELEGRAM_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
        TG_CHANNEL_ID="test_channel",
        ADMIN_IDS='["42"]',
        OPENAI_API_KEY="key",
        GOOGLE_API_KEY="key"
    )
    bot = NewsBot(settings)
    msg = DummyMessage(user_id=99, text="/stats")
    await bot.handle_admin_command(msg)
    assert msg.reply_text is not None and "доступу" in msg.reply_text 
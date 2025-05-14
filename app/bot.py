from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import structlog
from app.config import Settings, settings
from app.db import db
from app.models import NewsItem
from app.scheduler import NewsScheduler

logger = structlog.get_logger()

class NewsBot:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.bot = Bot(token=settings.TELEGRAM_TOKEN)
        self.dp = Dispatcher()
        self.setup_handlers()

    def setup_handlers(self):
        """Setup message handlers"""
        self.dp.message.register(self.handle_admin_command, Command("stats"))
        self.dp.message.register(self.handle_admin_command, Command("digest"))
        self.dp.message.register(self.handle_admin_command, Command("toggle"))

    async def handle_admin_command(self, message: Message) -> None:
        """Handle admin commands."""
        if not message.from_user:
            return
            
        user_id = str(message.from_user.id)
        if user_id not in self.settings.get_admin_ids():
            await message.reply("⛔️ У вас немає доступу до цієї команди.")
            return

        command = message.text.split()[0] if message.text else ""
        if command == "/stats":
            await self.show_stats(message)
        elif command == "/digest":
            await self.create_digest(message)
        elif command.startswith("/toggle"):
            await self.toggle_feature(message)

    async def show_stats(self, message: Message) -> None:
        """Show statistics for 24 hours / week"""
        day_ago = datetime.now() - timedelta(days=1)
        day_stats = db.get_stats_since(day_ago)
        
        week_ago = datetime.now() - timedelta(days=7)
        week_stats = db.get_stats_since(week_ago)
        
        text = "📊 Статистика бота:\n\n"
        text += "За 24 години:\n"
        text += f"• Оброблено новин: {day_stats['total']}\n"
        text += f"• Breaking news: {day_stats['breaking']}\n"
        text += f"• Середній impact: {day_stats['avg_impact']:.1f}\n\n"
        
        text += "За тиждень:\n"
        text += f"• Оброблено новин: {week_stats['total']}\n"
        text += f"• Breaking news: {week_stats['breaking']}\n"
        text += f"• Середній impact: {week_stats['avg_impact']:.1f}\n"
        
        await message.reply(text)

    async def create_digest(self, message: Message) -> None:
        """Send digest now"""
        try:
            scheduler = NewsScheduler()
            await scheduler.send_daily_digest()
            await message.reply("✅ Дайджест відправлено")
        except Exception as e:
            logger.error("error_sending_digest", error=str(e))
            await message.reply("❌ Помилка при відправці дайджесту")

    async def toggle_feature(self, message: Message) -> None:
        """Toggle source on/off"""
        try:
            source_id = message.text.split()[1]
            success = db.toggle_source(source_id)
            if success:
                await message.reply(f"✅ Джерело {source_id} {'увімкнено' if success else 'вимкнено'}")
            else:
                await message.reply("❌ Джерело не знайдено")
        except IndexError:
            await message.reply("❌ Вкажіть ID джерела: /toggle <source_id>")

    async def start(self):
        """Start the bot"""
        try:
            await self.dp.start_polling(self.bot)
        except Exception as e:
            logger.error("error_starting_bot", error=str(e))
            raise

# For backward compatibility
bot = Bot(token=settings.TELEGRAM_TOKEN)
dp = Dispatcher()

TG_ADMIN_ID = int(getattr(settings, 'TG_ADMIN_ID', 0))

# Список адмінів (ID користувачів Telegram)
ADMIN_IDS = [int(id) for id in settings.get_admin_ids()]

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

async def send_breaking_news(item):
    """Відправити breaking news в канал"""
    try:
        text = f"Breaking News\n\n"
        text += f"{item.title}\n\n"
        text += f"{item.summary}\n\n"
        text += f"{item.url}"
        
        await bot.send_message(
            chat_id=settings.TELEGRAM_CHANNEL_ID,
            text=text,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        logger.info("breaking_news_sent", title=item.title, impact=item.impact)
    except Exception as e:
        logger.error("error_sending_breaking_news", error=str(e), title=item.title)

async def start_bot():
    """Запустить бота"""
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error("error_starting_bot", error=str(e))
        raise 

async def handle_admin_command(self, message: Message) -> None:
    """Handle admin commands."""
    if not message.from_user:
        return
        
    user_id = str(message.from_user.id)
    if user_id not in self.settings.get_admin_ids():
        await message.reply("⛔️ У вас немає доступу до цієї команди.")
        return

    command = message.text.split()[0] if message.text else ""
    if command == "/stats":
        await self.show_stats(message)
    elif command == "/digest":
        await self.create_digest(message)
    elif command.startswith("/toggle"):
        await self.toggle_feature(message) 
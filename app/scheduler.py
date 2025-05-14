import yaml
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import structlog
from datetime import datetime, timedelta
from app.config import settings
from app.fetchers.rss import RSSFetcher
from app.fetchers.api import APIFetcher
from app.fetchers.github import GitHubTrendingFetcher
from app.models import Source
from app.db import db
from app.ranker import Ranker
from app.summarizer import Summarizer

logger = structlog.get_logger()

FETCHER_MAP = {
    'rss': RSSFetcher,
    'api': APIFetcher,
    'scrap': GitHubTrendingFetcher,
}

class NewsScheduler:
    """Планировщик задач для обработки новостей"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.ranker = Ranker()
        self.summarizer = Summarizer()
        self.sources = self._load_sources()
        self.delivery_stats = {"total": 0, "success": 0}
        self.duplicate_stats = {"total": 0, "duplicates": 0}
    
    def _load_sources(self) -> list[Source]:
        """Загрузить источники из конфига"""
        with open(settings.SOURCES_FILE) as f:
            data = yaml.safe_load(f)
            return [Source(**source) for source in data['sources']]
    
    def _is_breaking_news_timely(self, item) -> bool:
        """Проверить, что новость не старше 15 минут"""
        if not item.published:
            return False
        time_diff = datetime.now() - item.published
        return time_diff <= timedelta(minutes=15)
    
    def _is_duplicate(self, item) -> bool:
        """Проверить на дубликаты"""
        recent_news = db.get_recent_news(minutes=60)  # Проверяем последний час
        for news in recent_news:
            if self._calculate_similarity(item.title, news.title) > 0.8:  # Порог схожести 80%
                self.duplicate_stats["duplicates"] += 1
                return True
        return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Рассчитать схожесть двух текстов (простая реализация)"""
        # TODO: Заменить на более продвинутый алгоритм (например, cosine similarity)
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0
    
    async def process_source(self, source: Source):
        """Обработать один источник"""
        print(f"process_source called for {source.id}")
        try:
            fetcher_cls = FETCHER_MAP.get(source.type)
            if not fetcher_cls:
                logger.error(f"Unknown fetcher type: {source.type}", source_id=source.id)
                return
            fetcher = fetcher_cls(source)
            items = await fetcher.fetch()
            print(f"Fetched {len(items)} items from {source.id}")  # DEBUG
            if not items:
                return
            processed_items = await self.summarizer.process_batch(items)
            for item in processed_items:
                if self._is_duplicate(item):
                    logger.info("duplicate_skipped", title=item.title)
                    continue
                    
                score = self.ranker.calculate_score(item)
                item.score = score
                item.impact = self.ranker.calculate_impact(score, item.impact)
                
                if db.add_news_item(item):
                    if item.impact >= 2:
                        print(f"TRY SEND: {item.title} | {item.source_id}")
                        print(f"Send breaking news: {item.title}")  # DEBUG
                        try:
                            from app.bot import send_breaking_news
                            await send_breaking_news(item)
                            self.delivery_stats["success"] += 1
                            logger.info("breaking_news_sent", title=item.title, impact=item.impact)
                        except Exception as e:
                            logger.error("breaking_news_delivery_failed", error=str(e), title=item.title)
                        self.delivery_stats["total"] += 1
            await fetcher.close()
        except Exception as e:
            logger.error("error_processing_source", error=str(e), source_id=source.id)
    
    async def send_daily_digest(self):
        """Отправить ежедневный дайджест"""
        try:
            news = db.get_unsent_news()
            if not news:
                logger.info("no_news_for_digest")
                return
            text = "<b>📰 Дайджест найцікавіших новин за день</b>\n\n"
            for item in news:
                text += (
                    f"<b>• {item.title}</b>\n"
                    f"<i>{item.summary}</i>\n"
                    f"<b>Чому це важливо:</b> {item.why_matters}\n"
                    f"<b>Джерело:</b> <code>{item.source_id}</code> | <b>Impact:</b> {item.impact}\n"
                    f"<a href='{item.url}'>Читати повністю</a>\n\n"
                )
            try:
                from app.bot import send_breaking_news
                await send_breaking_news(news[0])  # TODO: можна зробити окрему функцію для красивого дайджесту
                self.delivery_stats["success"] += 1
                logger.info("digest_sent", items_count=len(news))
            except Exception as e:
                logger.error("digest_delivery_failed", error=str(e))
            self.delivery_stats["total"] += 1
            
            for item in news:
                db.mark_as_sent(item.url)
                
            # Логируем статистику
            delivery_rate = (self.delivery_stats["success"] / self.delivery_stats["total"] * 100) if self.delivery_stats["total"] > 0 else 0
            duplicate_rate = (self.duplicate_stats["duplicates"] / self.duplicate_stats["total"] * 100) if self.duplicate_stats["total"] > 0 else 0
            logger.info("delivery_stats", 
                       delivery_rate=f"{delivery_rate:.2f}%",
                       duplicate_rate=f"{duplicate_rate:.2f}%")
        except Exception as e:
            logger.error("error_sending_digest", error=str(e))

    def start(self):
        """Запустить планировщик"""
        for source in self.sources:
            if source.active:
                self.scheduler.add_job(
                    self.process_source,
                    'interval',
                    minutes=source.interval,
                    args=[source],
                    id=f"source_{source.id}"
                )
        self.scheduler.add_job(
            self.send_daily_digest,
            CronTrigger(hour=12, minute=30, timezone='Europe/Kiev'),
            id="daily_digest"
        )
        print("Scheduler jobs:", self.scheduler.get_jobs())  # DEBUG
        self.scheduler.start()
        logger.info("scheduler_started") 
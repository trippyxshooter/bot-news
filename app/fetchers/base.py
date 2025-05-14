from abc import ABC, abstractmethod
from typing import List
from datetime import datetime
import httpx
import structlog
from app.models import NewsItem, Source

logger = structlog.get_logger()

class BaseFetcher(ABC):
    """Базовый класс для всех фетчеров новостей"""
    
    def __init__(self, source: Source):
        self.source = source
        self.client = httpx.AsyncClient(timeout=30.0)
        self.logger = logger.bind(source_id=source.id)
    
    @abstractmethod
    async def fetch(self) -> List[NewsItem]:
        """Получить новости из источника"""
        pass
    
    async def close(self):
        """Закрыть HTTP клиент"""
        await self.client.aclose()
    
    def _create_news_item(
        self,
        url: str,
        title: str,
        content: str,
        published: datetime,
        lang: str
    ) -> NewsItem:
        """Создать объект новости"""
        return NewsItem(
            url=url,
            title=title,
            source_id=self.source.id,
            published=published,
            content=content,
            lang=lang,
            impact=1
        ) 
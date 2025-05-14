import feedparser
from datetime import datetime
from typing import List
from bs4 import BeautifulSoup
import structlog
from app.fetchers.base import BaseFetcher
from app.models import NewsItem
from app.db import db

logger = structlog.get_logger()

class RSSFetcher(BaseFetcher):
    """Фетчер для RSS-лент"""
    
    async def fetch(self) -> List[NewsItem]:
        """Получить новости из RSS-ленты"""
        try:
            etag, last_modified = db.get_source_headers(self.source.id)
            headers = {}
            if etag:
                headers['If-None-Match'] = etag
            if last_modified:
                headers['If-Modified-Since'] = last_modified
            response = await self.client.get(self.source.url, headers=headers)
            if response.status_code == 304:
                return []
            response.raise_for_status()
            # Зберігаємо нові etag/last_modified, якщо вони є
            new_etag = response.headers.get('ETag')
            new_last_modified = response.headers.get('Last-Modified')
            if new_etag or new_last_modified:
                db.update_source_headers(self.source.id, etag=new_etag, last_modified=new_last_modified)
            feed = feedparser.parse(response.text)
            items = []
            
            for entry in feed.entries:
                try:
                    # Получаем дату публикации
                    published = datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now()
                    
                    # Очищаем контент от HTML
                    content = self._clean_html(entry.summary if hasattr(entry, 'summary') else entry.description)
                    
                    # Создаем объект новости
                    news_item = self._create_news_item(
                        url=entry.link,
                        title=entry.title,
                        content=content,
                        published=published,
                        lang=self.source.lang
                    )
                    items.append(news_item)
                    
                except Exception as e:
                    self.logger.error("error_processing_entry", error=str(e), entry=entry)
                    continue
                    
            return items
            
        except Exception as e:
            self.logger.error("error_fetching_rss", error=str(e))
            return []
    
    def _clean_html(self, html: str) -> str:
        """Очистить HTML от тегов"""
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text(separator=" ", strip=True) 
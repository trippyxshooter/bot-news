from typing import List
from datetime import datetime
import structlog
from app.fetchers.base import BaseFetcher
from app.models import NewsItem
from app.utils import clean_text, detect_language

logger = structlog.get_logger()

class APIFetcher(BaseFetcher):
    """Фетчер для API-джерел (наприклад, taaft)"""
    
    async def fetch(self) -> List[NewsItem]:
        try:
            response = await self.client.get(self.source.url)
            response.raise_for_status()
            data = response.json()
            items = []
            for entry in data.get('tools', []):
                try:
                    published = datetime.fromisoformat(entry.get('createdAt', datetime.now().isoformat()))
                    content = clean_text(entry.get('description', ''))
                    lang, prob = detect_language(content)
                    news_item = self._create_news_item(
                        url=entry.get('url', ''),
                        title=entry.get('name', ''),
                        content=content,
                        published=published,
                        lang=lang
                    )
                    items.append(news_item)
                except Exception as e:
                    self.logger.error("error_processing_api_entry", error=str(e), entry=entry)
                    continue
            return items
        except Exception as e:
            self.logger.error("error_fetching_api", error=str(e))
            return [] 
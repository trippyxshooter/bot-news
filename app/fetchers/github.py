from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
import structlog
from app.fetchers.base import BaseFetcher
from app.models import NewsItem
from app.utils import clean_text, detect_language

logger = structlog.get_logger()

class GitHubTrendingFetcher(BaseFetcher):
    """Фетчер для GitHub Trending AI"""
    
    async def fetch(self) -> List[NewsItem]:
        try:
            response = await self.client.get(self.source.url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            items = []
            for repo in soup.select('article.Box-row'):
                try:
                    title_tag = repo.select_one('h2 a')
                    url = 'https://github.com' + title_tag['href'] if title_tag else ''
                    title = title_tag.get_text(strip=True) if title_tag else ''
                    desc_tag = repo.select_one('p')
                    content = clean_text(desc_tag.get_text(strip=True) if desc_tag else '')
                    lang, prob = detect_language(content)
                    published = datetime.now()  # GitHub не дає точну дату, ставимо зараз
                    news_item = self._create_news_item(
                        url=url,
                        title=title,
                        content=content,
                        published=published,
                        lang=lang
                    )
                    items.append(news_item)
                except Exception as e:
                    self.logger.error("error_processing_github_entry", error=str(e))
                    continue
            return items
        except Exception as e:
            self.logger.error("error_fetching_github", error=str(e))
            return [] 
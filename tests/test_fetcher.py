import pytest
from datetime import datetime
from app.fetchers.rss import RSSFetcher
from app.models import Source

@pytest.fixture
def source():
    """Фикстура для тестового источника"""
    return Source(
        id="test",
        name="Test Source",
        type="rss",
        url="https://example.com/feed.xml",
        interval=15,
        lang="en"
    )

@pytest.mark.asyncio
async def test_fetch_empty(source):
    """Тест получения пустого фида"""
    fetcher = RSSFetcher(source)
    items = await fetcher.fetch()
    
    assert isinstance(items, list)
    assert len(items) == 0

@pytest.mark.asyncio
async def test_clean_html():
    """Тест очистки HTML"""
    fetcher = RSSFetcher(Source(
        id="test",
        name="Test",
        type="rss",
        url="https://example.com",
        interval=15,
        lang="en"
    ))
    
    html = "<p>Test <b>content</b> with <a href='#'>link</a></p>"
    cleaned = fetcher._clean_html(html)
    
    assert cleaned == "Test content with link"
    assert "<" not in cleaned
    assert ">" not in cleaned

@pytest.mark.asyncio
async def test_create_news_item(source):
    """Тест создания объекта новости"""
    fetcher = RSSFetcher(source)
    
    item = fetcher._create_news_item(
        url="https://example.com/news/1",
        title="Test News",
        content="Test content",
        published=datetime.now(),
        lang="en"
    )
    item.impact = 1
    
    assert item.url == "https://example.com/news/1"
    assert item.title == "Test News"
    assert item.source_id == source.id
    assert item.lang == "en" 
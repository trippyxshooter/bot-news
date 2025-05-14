import pytest
from datetime import datetime, timedelta
from app.models import NewsItem
from app.ranker import Ranker

@pytest.fixture
def news_item():
    """Фикстура для тестовой новости"""
    return NewsItem(
        url="https://example.com/news/1",
        title="Test News",
        source_id="test",
        published=datetime.now(),
        content="Test content",
        lang="en",
        impact=1
    )

@pytest.fixture
def ranker():
    return Ranker()

@pytest.fixture
def sample_news():
    return NewsItem(
        url="https://example.com/news/1",
        title="Test News",
        source_id="test",
        published=datetime.now(),
        content="Test content",
        lang="en",
        score=0,
        impact=1
    )

def test_calculate_score(ranker, sample_news):
    # Тест з високим рейтингом
    score = ranker.calculate_score(sample_news)
    assert score > 0
    assert score <= 100.0

def test_calculate_impact(ranker, sample_news):
    # Тест з високим impact
    score = 50
    impact = ranker.calculate_impact(score, 0)
    assert 1 <= impact <= 5
    assert isinstance(impact, int)

def test_fresh_news_bonus(ranker, sample_news):
    # Тест бонусу за свіжість
    sample_news.published = datetime.now() - timedelta(hours=1)
    score1 = ranker.calculate_score(sample_news)
    
    sample_news.published = datetime.now() - timedelta(hours=48)
    score2 = ranker.calculate_score(sample_news)
    
    assert score1 > score2  # Свіжа новина має вищий рейтинг

def test_old_news_score(news_item):
    """Тест score для старых новостей"""
    ranker = Ranker()
    
    # Делаем новость старой
    news_item.published = datetime.now() - timedelta(days=3)
    score = ranker.calculate_score(news_item)
    
    assert score <= 1.0  # Должен быть низкий score 

def test_score_zero_for_empty_content(ranker):
    item = NewsItem(
        url="https://example.com/news/2",
        title="",
        source_id="test",
        published=datetime.now(),
        content="",
        lang="en",
        impact=1
    )
    score = ranker.calculate_score(item)
    assert score == 0

def test_impact_min_max(ranker, sample_news):
    assert ranker.calculate_impact(0, 0) == 1
    assert ranker.calculate_impact(1000, 0) == 5 
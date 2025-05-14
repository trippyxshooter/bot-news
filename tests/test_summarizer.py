import pytest
from app.summarizer import Summarizer
from app.models import NewsItem
from datetime import datetime

@pytest.fixture
def summarizer():
    return Summarizer()

@pytest.fixture
def sample_news():
    return NewsItem(
        url="https://example.com/news/1",
        title="OpenAI Announces GPT-5",
        source_id="test",
        published=datetime.now(),
        content="OpenAI has announced the development of GPT-5, their next-generation language model. The new model promises significant improvements in understanding and generating human-like text.",
        lang="en",
        score=0,
        impact=1
    )

@pytest.mark.asyncio
async def test_process_batch(summarizer, sample_news):
    # Тест обробки пакету новин
    items = [sample_news] * 3
    results = await summarizer.process_batch(items)
    assert len(results) == 3
    for item in results:
        assert item.summary
        assert item.why_matters
        assert 1 <= item.impact <= 5

@pytest.mark.asyncio
async def test_impact_range(summarizer, sample_news):
    # Тест діапазону impact
    results = await summarizer.process_batch([sample_news])
    assert 1 <= results[0].impact <= 5

@pytest.mark.asyncio
async def test_summary_length(summarizer, sample_news):
    # Тест довжини summary
    results = await summarizer.process_batch([sample_news])
    assert len(results[0].summary.split()) <= 50  # Не більше 50 слів 
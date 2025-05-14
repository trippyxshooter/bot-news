import pytest
from unittest.mock import AsyncMock, patch
from app.summarizer import Summarizer
from app.models import NewsItem, SummarySchema

@pytest.fixture
def news_item():
    return NewsItem(
        url="https://example.com/news/1",
        title="Test News",
        content="This is a test news content",
        source_id="test_source",
        published="2024-03-20T12:00:00Z",
        lang="en"
    )

@pytest.fixture
def summarizer():
    return Summarizer()

@pytest.mark.asyncio
async def test_process_batch_with_gemini(summarizer, news_item):
    """Тест обработки новости через Gemini"""
    with patch.object(summarizer.gemini_model, 'generate_content_async') as mock_generate:
        mock_generate.return_value = AsyncMock(
            text='{"summary": "Test summary", "why": "Test why", "impact": 3}'
        )
        
        results = await summarizer.process_batch([news_item])
        
        assert len(results) == 1
        assert results[0].summary == "Test summary"
        assert results[0].why_matters == "Test why"
        assert results[0].impact == 3
        assert results[0].llm_model == "gemini-1.5-flash"

@pytest.mark.asyncio
async def test_process_batch_with_openai_fallback(summarizer, news_item):
    """Тест fallback на OpenAI при ошибке Gemini"""
    with patch.object(summarizer.gemini_model, 'generate_content_async', side_effect=Exception("Gemini error")), \
         patch.object(summarizer.openai_client.chat.completions, 'create') as mock_create:
        
        mock_create.return_value = AsyncMock(
            choices=[AsyncMock(message=AsyncMock(content='{"summary": "OpenAI summary", "why": "OpenAI why", "impact": 4}'))]
        )
        
        results = await summarizer.process_batch([news_item])
        
        assert len(results) == 1
        assert results[0].summary == "OpenAI summary"
        assert results[0].why_matters == "OpenAI why"
        assert results[0].impact == 4
        assert results[0].llm_model == "openai"

@pytest.mark.asyncio
async def test_process_batch_error_handling(summarizer, news_item):
    """Тест обработки ошибок при обработке новости"""
    with patch.object(summarizer.gemini_model, 'generate_content_async', side_effect=Exception("Test error")), \
         patch.object(summarizer.openai_client.chat.completions, 'create', side_effect=Exception("OpenAI error")):
        
        results = await summarizer.process_batch([news_item])
        assert len(results) == 0

def test_prompt_creation(summarizer, news_item):
    """Тест создания промпта"""
    prompt = summarizer._create_prompt(news_item)
    assert "Title: Test News" in prompt
    assert "Content: This is a test news content" in prompt
    assert "Return ONLY valid JSON" in prompt

def test_parse_llm_response_valid_json(summarizer):
    """Тест парсинга валидного JSON ответа"""
    response = '{"summary": "Test", "why": "Test", "impact": 3}'
    result = summarizer._parse_llm_response(response)
    assert isinstance(result, SummarySchema)
    assert result.summary == "Test"
    assert result.why == "Test"
    assert result.impact == 3

def test_parse_llm_response_invalid_json(summarizer):
    """Тест парсинга невалидного JSON ответа"""
    with pytest.raises(Exception):
        summarizer._parse_llm_response("invalid json") 
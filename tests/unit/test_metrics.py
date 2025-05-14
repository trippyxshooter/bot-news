import pytest
from unittest.mock import AsyncMock, patch
from app.metrics import (
    NEWS_PROCESSED,
    NEWS_IMPACT,
    NEWS_PROCESSING_TIME,
    LLM_REQUESTS,
    LLM_COST,
    DUPLICATE_RATE,
    SCHEDULER_JOBS,
    MetricsMiddleware
)

@pytest.fixture
def metrics_middleware():
    return MetricsMiddleware(AsyncMock())

@pytest.mark.asyncio
async def test_metrics_middleware(metrics_middleware):
    """Тест middleware для метрик"""
    scope = {"type": "http"}
    receive = AsyncMock()
    send = AsyncMock()
    
    # Симулируем успешный ответ
    async def mock_send(message):
        if message["type"] == "http.response.start":
            message["status"] = 200
    
    await metrics_middleware(scope, receive, mock_send)
    
    # Проверяем, что метрики были обновлены
    assert NEWS_PROCESSED._value.get() > 0
    assert NEWS_PROCESSING_TIME._sum.get() > 0

def test_news_metrics():
    """Тест метрик новостей"""
    # Тестируем счетчик обработанных новостей
    NEWS_PROCESSED.labels(source="test", status="success").inc()
    assert NEWS_PROCESSED._value.get() == 1
    
    # Тестируем гистограмму impact
    NEWS_IMPACT.observe(3)
    assert NEWS_IMPACT._sum.get() == 3
    
    # Тестируем гистограмму времени обработки
    NEWS_PROCESSING_TIME.observe(0.5)
    assert NEWS_PROCESSING_TIME._sum.get() == 0.5

def test_llm_metrics():
    """Тест метрик LLM"""
    # Тестируем счетчик запросов
    LLM_REQUESTS.labels(model="gemini", status="success").inc()
    assert LLM_REQUESTS._value.get() == 1
    
    # Тестируем счетчик стоимости
    LLM_COST.labels(model="gemini").inc(0.001)
    assert LLM_COST._value.get() == 0.001

def test_duplicate_rate():
    """Тест метрики дубликатов"""
    DUPLICATE_RATE.set(0.1)
    assert DUPLICATE_RATE._value.get() == 0.1

def test_scheduler_jobs():
    """Тест метрики планировщика"""
    SCHEDULER_JOBS.set(5)
    assert SCHEDULER_JOBS._value.get() == 5 
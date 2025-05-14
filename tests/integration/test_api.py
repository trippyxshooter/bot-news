import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import NewsItem
from app.db import Database
import json

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db():
    return Database()

@pytest.fixture
def sample_news():
    return {
        "url": "https://example.com/news/1",
        "title": "Test News",
        "content": "This is a test news content",
        "source_id": "test_source",
        "published": "2024-03-20T12:00:00Z",
        "lang": "en"
    }

def test_healthz_endpoint(client):
    """Тест healthz endpoint"""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "scheduler_jobs" in data
    assert "version" in data

def test_metrics_endpoint(client):
    """Тест metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "news_processed_total" in response.text
    assert "news_impact" in response.text

def test_news_processing(client, sample_news):
    """Тест обработки новости"""
    response = client.post(
        "/api/news",
        json=sample_news,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "why_matters" in data
    assert "impact" in data

def test_duplicate_handling(client, sample_news):
    """Тест обработки дубликатов"""
    # Отправляем первую новость
    response1 = client.post(
        "/api/news",
        json=sample_news,
        headers={"Content-Type": "application/json"}
    )
    assert response1.status_code == 200
    
    # Отправляем ту же новость снова
    response2 = client.post(
        "/api/news",
        json=sample_news,
        headers={"Content-Type": "application/json"}
    )
    assert response2.status_code == 409  # Conflict

def test_invalid_news_format(client):
    """Тест обработки невалидного формата новости"""
    invalid_news = {
        "url": "invalid-url",
        "title": "Test News"
        # Отсутствуют обязательные поля
    }
    response = client.post(
        "/api/news",
        json=invalid_news,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422  # Unprocessable Entity

@pytest.mark.asyncio
async def test_scheduler_integration(db):
    """Тест интеграции с планировщиком"""
    # Проверяем, что планировщик создает задачи
    scheduler = NewsScheduler()
    jobs = scheduler.scheduler.get_jobs()
    assert len(jobs) > 0
    
    # Проверяем, что задачи выполняются
    for job in jobs:
        assert job.next_run_time is not None 
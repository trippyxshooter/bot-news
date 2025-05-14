from locust import HttpUser, task, between
import random

class NewsBotUser(HttpUser):
    wait_time = between(1, 5)
    
    @task(3)
    def check_health(self):
        """Проверка healthz endpoint"""
        self.client.get("/healthz")
    
    @task(1)
    def check_metrics(self):
        """Проверка метрик"""
        self.client.get("/metrics")
    
    @task(2)
    def simulate_news_processing(self):
        """Симуляция обработки новостей"""
        # Генерируем тестовую новость
        news = {
            "url": f"https://example.com/news/{random.randint(1, 1000)}",
            "title": f"Test News {random.randint(1, 1000)}",
            "content": "This is a test news content for load testing.",
            "source_id": "test_source",
            "published": "2024-03-20T12:00:00Z",
            "lang": "en"
        }
        
        # Отправляем POST запрос
        self.client.post(
            "/api/news",
            json=news,
            headers={"Content-Type": "application/json"}
        ) 
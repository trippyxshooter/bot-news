from prometheus_client import Counter, Histogram, Gauge
import time

# Метрики для новостей
NEWS_PROCESSED = Counter(
    'news_processed_total',
    'Total number of processed news items',
    ['source', 'status']
)

NEWS_IMPACT = Histogram(
    'news_impact',
    'Impact score distribution',
    buckets=[1, 2, 3, 4, 5]
)

NEWS_PROCESSING_TIME = Histogram(
    'news_processing_seconds',
    'Time spent processing news items',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

# Метрики для LLM
LLM_REQUESTS = Counter(
    'llm_requests_total',
    'Total number of LLM requests',
    ['model', 'status']
)

LLM_COST = Counter(
    'llm_cost_usd',
    'Total cost of LLM requests in USD',
    ['model']
)

# Метрики для дубликатов
DUPLICATE_RATE = Gauge(
    'duplicate_rate',
    'Rate of duplicate news items'
)

# Метрики для планировщика
SCHEDULER_JOBS = Gauge(
    'scheduler_jobs',
    'Number of active scheduler jobs'
)

class MetricsMiddleware:
    """Middleware для сбора метрик"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
            
        start_time = time.time()
        
        async def wrapped_send(message):
            if message["type"] == "http.response.start":
                NEWS_PROCESSED.labels(
                    source="api",
                    status=message["status"]
                ).inc()
            await send(message)
            
        await self.app(scope, receive, wrapped_send)
        
        NEWS_PROCESSING_TIME.observe(time.time() - start_time) 
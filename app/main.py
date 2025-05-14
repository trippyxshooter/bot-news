import asyncio
import structlog
import sentry_sdk
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from app.bot import start_bot
from app.scheduler import NewsScheduler
from app.config import settings

logger = structlog.get_logger()

# Инициализация FastAPI
app = FastAPI(title="AI News Bot API")

# Инициализация Sentry
sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

@app.get("/healthz")
async def healthz():
    """Health check endpoint"""
    try:
        # Проверяем подключение к БД
        from app.db import db
        db.conn.execute("SELECT 1")
        
        # Проверяем статус планировщика
        scheduler = NewsScheduler()
        jobs = scheduler.scheduler.get_jobs()
        
        return JSONResponse({
            "status": "healthy",
            "scheduler_jobs": len(jobs),
            "version": settings.VERSION
        })
    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        return Response(status_code=500)

async def main():
    """Основная функция запуска приложения"""
    try:
        # Инициализируем планировщик
        scheduler = NewsScheduler()
        scheduler.start()
        
        # Запускаем бота
        await start_bot()
        
    except Exception as e:
        logger.error("error_starting_app", error=str(e))
        raise

if __name__ == "__main__":
    # Настраиваем логирование
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ]
    )
    
    # Запускаем приложение
    asyncio.run(main()) 
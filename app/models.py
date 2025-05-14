from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class NewsItem(BaseModel):
    """Модель для хранения новостей"""
    url: str
    title: str
    source_id: str
    published: datetime
    content: str
    lang: str
    score: float = 0.0
    impact: int = Field(ge=1, le=5)
    summary: Optional[str] = None
    why_matters: Optional[str] = None
    processed_at: Optional[datetime] = None
    sent: bool = False
    llm_model: Optional[str] = None
    cost_usd: Optional[float] = None

class Source(BaseModel):
    """Модель для источников новостей"""
    id: str
    name: str
    type: str
    url: str
    interval: int  # в минутах
    lang: str
    weight: int = 1
    active: bool = True
    etag: Optional[str] = None
    last_modified: Optional[str] = None

class SummarySchema(BaseModel):
    """Схема для ответа LLM"""
    summary: str
    why: str
    impact: int = Field(ge=1, le=5) 
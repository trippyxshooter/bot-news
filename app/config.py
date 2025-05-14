from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import json

class Settings(BaseSettings):
    # Telegram settings
    TELEGRAM_TOKEN: str
    TELEGRAM_CHANNEL_ID: str
    ADMIN_IDS: str  # Зберігаємо як рядок
    
    # LLM API keys
    OPENAI_API_KEY: str
    GOOGLE_API_KEY: str
    
    # Database
    DB_URL: str = Field(default="sqlite:///data.db")
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    SOURCES_FILE: Path = BASE_DIR / "config" / "sources.yml"
    
    # LLM settings
    GEMINI_TEMPERATURE: float = 0.2
    GPT4_TEMPERATURE: float = 0.1
    
    # Processing settings
    MAX_CONTENT_LENGTH: int = 4000
    BATCH_SIZE: int = 10
    PROCESSING_TIMEOUT: int = 12
    
    # Monitoring
    SENTRY_DSN: str = ""
    VERSION: str = "1.0.0"
    
    # Metrics
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    def get_admin_ids(self) -> List[str]:
        """Повертає список ID адмінів."""
        try:
            return json.loads(self.ADMIN_IDS.strip("'"))
        except (json.JSONDecodeError, AttributeError):
            return []
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings() 
import sqlite3
from typing import List, Optional
import structlog
from app.models import NewsItem
from app.config import settings
from datetime import datetime, timedelta

logger = structlog.get_logger()

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(settings.DB_URL.replace('sqlite:///', ''))
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        """Создать необходимые таблицы"""
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS sources (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    weight INTEGER DEFAULT 1,
                    active BOOLEAN DEFAULT 1,
                    etag TEXT,
                    last_modified TEXT
                )
            """)
            
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS news_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE,
                    title TEXT,
                    source_id TEXT REFERENCES sources(id),
                    published TIMESTAMP,
                    content TEXT,
                    lang TEXT,
                    score REAL,
                    impact INTEGER,
                    summary TEXT,
                    why_matters TEXT,
                    processed_at TIMESTAMP,
                    sent BOOLEAN DEFAULT 0,
                    llm_model TEXT,
                    cost_usd REAL
                )
            """)
    
    def add_news_item(self, item: NewsItem) -> bool:
        """Добавить новую новость в БД"""
        try:
            with self.conn:
                self.conn.execute("""
                    INSERT OR IGNORE INTO news_items (
                        url, title, source_id, published, content, lang,
                        score, impact, summary, why_matters, processed_at,
                        sent, llm_model, cost_usd
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item.url, item.title, item.source_id, item.published,
                    item.content, item.lang, item.score, item.impact,
                    item.summary, item.why_matters, item.processed_at,
                    item.sent, item.llm_model, item.cost_usd
                ))
            return True
        except Exception as e:
            logger.error("error_adding_news", error=str(e), url=item.url)
            return False
    
    def get_unsent_news(self, limit: int = 10) -> List[NewsItem]:
        """Получить неотправленные новости"""
        cursor = self.conn.execute("""
            SELECT * FROM news_items 
            WHERE sent = 0 
            ORDER BY impact DESC, published DESC 
            LIMIT ?
        """, (limit,))
        
        return [NewsItem(**dict(row)) for row in cursor.fetchall()]
    
    def mark_as_sent(self, url: str):
        """Отметить новость как отправленную"""
        with self.conn:
            self.conn.execute(
                "UPDATE news_items SET sent = 1 WHERE url = ?",
                (url,)
            )
    
    def get_last_news(self) -> Optional[NewsItem]:
        """Получить последнюю новость (по дате публикации)"""
        cursor = self.conn.execute(
            "SELECT * FROM news_items ORDER BY published DESC LIMIT 1"
        )
        row = cursor.fetchone()
        return NewsItem(**dict(row)) if row else None
    
    def get_recent_news(self, minutes: int = 60) -> list[NewsItem]:
        """Получить новости за последние N минут"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        cursor = self.conn.execute("""
            SELECT * FROM news_items 
            WHERE published >= ?
        """, (cutoff_time,))
        
        return [NewsItem(**dict(row)) for row in cursor.fetchall()]
    
    def get_stats_since(self, since: datetime) -> dict:
        """Отримати статистику з певного моменту"""
        cursor = self.conn.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN impact >= 4 THEN 1 ELSE 0 END) as breaking,
                AVG(impact) as avg_impact
            FROM news_items 
            WHERE published >= ?
        """, (since,))
        
        row = cursor.fetchone()
        return {
            'total': row['total'] or 0,
            'breaking': row['breaking'] or 0,
            'avg_impact': row['avg_impact'] or 0
        }
    
    def toggle_source(self, source_id: str) -> bool:
        """Увімкнути/вимкнути джерело"""
        try:
            with self.conn:
                cursor = self.conn.execute(
                    "SELECT active FROM sources WHERE id = ?",
                    (source_id,)
                )
                row = cursor.fetchone()
                if not row:
                    return False
                
                new_status = 0 if row['active'] else 1
                self.conn.execute(
                    "UPDATE sources SET active = ? WHERE id = ?",
                    (new_status, source_id)
                )
                return True
        except Exception as e:
            logger.error("error_toggling_source", error=str(e), source_id=source_id)
            return False
    
    def update_source_headers(self, source_id: str, etag: str = None, last_modified: str = None):
        """Оновити etag/last_modified для джерела"""
        with self.conn:
            if etag is not None and last_modified is not None:
                self.conn.execute(
                    "UPDATE sources SET etag = ?, last_modified = ? WHERE id = ?",
                    (etag, last_modified, source_id)
                )
            elif etag is not None:
                self.conn.execute(
                    "UPDATE sources SET etag = ? WHERE id = ?",
                    (etag, source_id)
                )
            elif last_modified is not None:
                self.conn.execute(
                    "UPDATE sources SET last_modified = ? WHERE id = ?",
                    (last_modified, source_id)
                )

    def get_source_headers(self, source_id: str):
        """Отримати etag/last_modified для джерела"""
        cursor = self.conn.execute(
            "SELECT etag, last_modified FROM sources WHERE id = ?",
            (source_id,)
        )
        row = cursor.fetchone()
        return (row['etag'], row['last_modified']) if row else (None, None)
    
    def close(self):
        """Закрыть соединение с БД"""
        self.conn.close()

db = Database() 
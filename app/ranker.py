from datetime import datetime
import structlog
from app.models import NewsItem

logger = structlog.get_logger()

class Ranker:
    """Класс для ранжирования новостей"""
    
    @staticmethod
    def calculate_score(item: NewsItem) -> float:
        """Рассчитать оценку важности новости"""
        try:
            # Базовый вес источника
            source_weight = 1.0  # TODO: брать из конфига
            
            # Время с публикации в часах
            hours_old = (datetime.now() - item.published).total_seconds() / 3600
            
            # Формула оценки
            score = source_weight + max(0, 48 - hours_old)
            
            return round(score, 2)
            
        except Exception as e:
            logger.error("error_calculating_score", error=str(e), url=item.url)
            return 0.0
    
    @staticmethod
    def calculate_impact(score: float, llm_impact: int) -> int:
        """Рассчитать итоговый impact"""
        try:
            # Округляем score/10 до ближайшего целого
            score_impact = round(score / 10)
            
            # Берем максимальное значение
            impact = max(llm_impact, score_impact)
            
            # Ограничиваем диапазоном 1-5
            return max(1, min(5, impact))
            
        except Exception as e:
            logger.error("error_calculating_impact", error=str(e), score=score)
            return 1 
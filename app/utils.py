import re
import hashlib
from langdetect import detect_langs
import logging

EMOJI_PATTERN = re.compile('[\\U00010000-\\U0010ffff]', flags=re.UNICODE)
MARKDOWN_PATTERN = re.compile(r'([*_~`\[\](){}<>#=|])')

STOP_WORDS = ["about", "tags", "sponsor"]

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """Очищення тексту: видалення HTML, emoji, markdown, обрізання по стоп-словах і довжині."""
    # Видалити emoji
    text = EMOJI_PATTERN.sub('', text)
    # Видалити markdown-артефакти
    text = MARKDOWN_PATTERN.sub('', text)
    # Обрізати по стоп-словах
    for word in STOP_WORDS:
        idx = text.lower().find(word)
        if idx != -1:
            text = text[:idx]
    # Обрізати до 4000 символів
    text = text[:4000]
    # Видалити зайві пробіли
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def detect_language(text: str) -> tuple[str, float]:
    """Detect language of text using langdetect."""
    try:
        langs = detect_langs(text)
        if langs:
            lang = langs[0].lang
            prob = langs[0].prob
            return lang, prob
    except Exception as e:
        logger.error(f"Language detection failed: {e}")
    return 'unknown', 0.0


def url_hash(url: str) -> str:
    """Повертає sha256-хеш для url."""
    return hashlib.sha256(url.encode('utf-8')).hexdigest() 
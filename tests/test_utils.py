import pytest
from app.utils import clean_text, detect_language, url_hash


def test_clean_text_removes_emoji():
    text = "Hello 😃 world!"
    assert clean_text(text) == "Hello world!"

def test_clean_text_removes_markdown():
    text = "*bold* _italic_ ~strike~"
    assert clean_text(text) == "bold italic strike"

def test_clean_text_stops_on_stopword():
    text = "This is about AI and future."
    assert clean_text(text) == "This is "

def test_detect_language_en():
    lang, prob = detect_language("Hello world!")
    assert lang == "en"
    assert prob > 0.5

def test_detect_language_unknown():
    lang, prob = detect_language("")
    assert lang == "unknown"
    assert prob == 0.0

def test_url_hash():
    h1 = url_hash("https://example.com")
    h2 = url_hash("https://example.com")
    h3 = url_hash("https://other.com")
    assert h1 == h2
    assert h1 != h3 
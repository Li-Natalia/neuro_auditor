"""Unit tests for the NLP pipeline intent detection."""
from app.ai.nlp_pipeline import detect_intent, preprocess, tokenize


def test_detect_intent_revenue():
    assert "revenue" in detect_intent("Как изменилась выручка?")


def test_detect_intent_risk():
    assert "risk" in detect_intent("Какие риски выявлены?")


def test_detect_intent_liquidity():
    intents = detect_intent("Сравни ликвидность с нормативами")
    assert "liquidity" in intents


def test_detect_intent_defaults_general():
    assert detect_intent("Привет") == ["general"]


def test_preprocess_structure():
    res = preprocess("Как изменилась прибыль за год?")
    assert "profit" in res["intents"]
    assert isinstance(res["tokens"], list)
    assert res["normalized"].startswith("как")


def test_tokenize_fallback():
    tokens = tokenize("Выручка 1 000 000 рублей")
    assert "выручка" in tokens

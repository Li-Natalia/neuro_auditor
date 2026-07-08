"""Lightweight NLP pipeline for user questions (tokenization + intent).

Gracefully degrades when spaCy/NLTK are not installed by using simple regex
tokenization. The intent classifier is keyword-based so the app is fully
functional without the heavy ML stack.
"""
from __future__ import annotations

import re
from typing import Any

_NLTK_OK = False
try:  # optional
    import nltk  # type: ignore

    _NLTK_OK = True
except Exception:  # pragma: no cover
    pass

INTENT_KEYWORDS: dict[str, list[str]] = {
    "revenue": ["выручк", "доход", "продаж"],
    "profit": ["прибыл", "убыток", "рентабель"],
    "liquidity": ["ликвидн", "оборотн", "платежеспособ"],
    "debt": ["долг", "задолжен", "кредит", "заем"],
    "risk": ["риск", "банкрот", "мошеннич"],
    "assets": ["актив", "баланс", "капитал"],
    "cashflow": ["денежн", "поток", "каш"],
}

TOKEN_RE = re.compile(r"[A-Za-zА-Яа-яёЁ0-9]+")


def tokenize(text: str) -> list[str]:
    if _NLTK_OK:
        try:
            return nltk.word_tokenize(text, language="russian")  # type: ignore
        except Exception:
            pass
    return TOKEN_RE.findall(text.lower())


def detect_intent(question: str) -> list[str]:
    """Return the list of detected financial intents in the question."""
    q = question.lower()
    found = []
    for intent, kws in INTENT_KEYWORDS.items():
        if any(kw in q for kw in kws):
            found.append(intent)
    return found or ["general"]


def preprocess(question: str) -> dict[str, Any]:
    return {
        "tokens": tokenize(question),
        "intents": detect_intent(question),
        "normalized": re.sub(r"\s+", " ", question.strip()).lower(),
    }

"""Chatbot model: answers via a configured LLM provider (YandexGPT or OpenAI).

There is no offline fallback: if no provider is configured — or a request to the
model fails — the chat returns a short message stating the neural model is
unavailable. Provider selection is controlled by ``AI_PROVIDER`` (auto|yandex|openai).
"""
from __future__ import annotations

import logging

from app.ai.prompts import build_system_prompt
from app.ai.yandex_client import get_yandex_client, yandex_configured
from app.core.config import settings

logger = logging.getLogger("fin-auditor")

_OPENAI_OK = False
try:  # optional
    import openai  # type: ignore

    _OPENAI_OK = True
except Exception:  # pragma: no cover
    pass

# Returned to the chat when the neural model can't be used (no offline fallback).
NOT_CONFIGURED_MESSAGE = (
    "AI-чат-бот сейчас недоступен: не настроено подключение к нейросети. "
    "Обратитесь к администратору, чтобы указать ключи языковой модели (YandexGPT)."
)
ERROR_MESSAGE = (
    "Не удалось получить ответ от нейросети. Проверьте подключение к языковой "
    "модели и повторите попытку позже."
)


def _resolve_provider() -> str | None:
    """Return the LLM provider to use, or None if none is available."""
    provider = (settings.AI_PROVIDER or "auto").lower()
    if provider == "yandex":
        return "yandex" if yandex_configured() else None
    if provider == "openai":
        return "openai" if (_OPENAI_OK and settings.OPENAI_API_KEY) else None
    # auto
    if yandex_configured():
        return "yandex"
    if _OPENAI_OK and settings.OPENAI_API_KEY:
        return "openai"
    return None


def _messages(question: str, context: dict | None) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": build_system_prompt(context)},
        {"role": "user", "content": question},
    ]


def _answer_with_yandex(question: str, context: dict | None) -> str:
    return get_yandex_client().chat(_messages(question, context))


def _answer_with_openai(question: str, context: dict | None) -> str:
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=_messages(question, context),
        temperature=settings.AI_TEMPERATURE,
    )
    return (resp.choices[0].message.content or "").strip()


def generate_answer(question: str, context: dict | None = None) -> str:
    """Answer via the configured LLM, or report that the neural model is unavailable."""
    provider = _resolve_provider()
    if provider is None:
        return NOT_CONFIGURED_MESSAGE

    try:
        if provider == "yandex":
            answer = _answer_with_yandex(question, context)
        else:
            answer = _answer_with_openai(question, context)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Провайдер '%s' недоступен: %s", provider, exc)
        return ERROR_MESSAGE

    return answer or ERROR_MESSAGE

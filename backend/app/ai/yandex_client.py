"""YandexGPT client via the OpenAI-compatible Foundation Models API.

Uses the OpenAI SDK pointed at Yandex Cloud (with an ``x-folder-id`` header) and
talks to the ``chat.completions`` endpoint: the Нейроаудитор chatbot builds its own system
prompt from the document's financial context, so it needs a plain completion model
rather than a pre-configured AI Studio agent with an attached knowledge base.

Docs: https://yandex.cloud/docs/ai-studio/concepts/openai-compatibility
"""
from __future__ import annotations

import logging
from functools import lru_cache

from app.core.config import settings

logger = logging.getLogger("fin-auditor")

_OPENAI_OK = False
try:  # openai is a light dependency shipped in requirements.txt
    import openai  # type: ignore

    _OPENAI_OK = True
except Exception:  # pragma: no cover
    pass


def yandex_configured() -> bool:
    """True when the SDK is present and Yandex credentials are set."""
    return bool(_OPENAI_OK and settings.AI_YC_API_KEY and settings.AI_YC_FOLDER_ID)


class YandexGPTClient:
    """Thin wrapper around the OpenAI SDK configured for Yandex Cloud."""

    def __init__(self, api_key: str, folder_id: str, base_url: str, model: str) -> None:
        if not _OPENAI_OK:
            raise RuntimeError("Пакет 'openai' не установлен. Установите: pip install openai")

        self._folder_id = folder_id
        # The OpenAI-compatible endpoint expects the folder inside the model URI.
        self._model_uri = model if model.startswith("gpt://") else f"gpt://{folder_id}/{model}"
        self._client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url,
            # Keep parity with the reference integration; harmless for chat.completions.
            default_headers={"x-folder-id": folder_id},
        )

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Send a chat completion request and return the assistant's text."""
        logger.debug("Запрос к YandexGPT (%s), сообщений: %d", self._model_uri, len(messages))
        response = self._client.chat.completions.create(
            model=self._model_uri,
            messages=messages,
            temperature=settings.AI_TEMPERATURE if temperature is None else temperature,
            max_tokens=settings.AI_MAX_TOKENS if max_tokens is None else max_tokens,
        )
        return (response.choices[0].message.content or "").strip()


def _resolve_yandex_client() -> YandexGPTClient:
    if not settings.AI_YC_API_KEY:
        raise RuntimeError("AI_YC_API_KEY не задан.")
    if not settings.AI_YC_FOLDER_ID:
        raise RuntimeError("AI_YC_FOLDER_ID не задан.")
    return YandexGPTClient(
        api_key=settings.AI_YC_API_KEY,
        folder_id=settings.AI_YC_FOLDER_ID,
        base_url=settings.AI_BASE_URL,
        model=settings.AI_MODEL,
    )


@lru_cache(maxsize=1)
def get_yandex_client() -> YandexGPTClient:
    """Return a cached YandexGPT client built from settings."""
    return _resolve_yandex_client()

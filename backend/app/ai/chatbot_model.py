"""Chatbot model: answers via YandexGPT (Yandex AI Studio Responses API).

There is no offline fallback: if Yandex is not configured — or a request fails — the
chat returns a short message saying the neural model is unavailable. Dialog context is
threaded through ``previous_response_id`` (the caller stores it per chat session).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from app.ai.prompts import build_code_interpreter_prompt, build_system_prompt
from app.ai.yandex_client import (
    Artifact,
    code_interpreter_enabled,
    get_yandex_client,
    yandex_configured,
)

logger = logging.getLogger("fin-auditor")

_OPENAI_OK = False
try:  # only needed to recognise SDK error classes
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
CI_DISABLED_MESSAGE = (
    "Режим Code Interpreter выключен на сервере (AI_CODE_INTERPRETER_ENABLED). "
    "Задайте вопрос в обычном режиме."
)


class FileUnavailableError(RuntimeError):
    """The Yandex Files API no longer has the document's file — the caller should re-upload."""


@dataclass
class ChatReply:
    answer: str
    response_id: str | None = None
    # True when the stored previous_response_id was rejected and the chain restarted.
    context_reset: bool = False
    artifacts: tuple[Artifact, ...] = ()


def generate_answer(
    question: str,
    context: dict | None = None,
    *,
    previous_response_id: str | None = None,
    mode: str = "context",
    file_id: str | None = None,
    filename: str | None = None,
) -> ChatReply:
    """Answer via YandexGPT, or report that the neural model is unavailable.

    ``mode="code_interpreter"`` attaches the document's Yandex file (``file_id``) and lets
    the model analyse it; a missing file raises :class:`FileUnavailableError` so the
    caller can re-upload and retry.
    """
    if not yandex_configured():
        return ChatReply(NOT_CONFIGURED_MESSAGE)
    if mode == "code_interpreter" and not code_interpreter_enabled():
        return ChatReply(CI_DISABLED_MESSAGE)

    client = get_yandex_client()
    try:
        if mode == "code_interpreter":
            if not file_id:
                raise ValueError("file_id is required for code_interpreter mode")
            reply = client.respond_with_code_interpreter(
                question,
                build_code_interpreter_prompt(context, filename or "отчёт"),
                previous_response_id,
                file_ids=[file_id],
            )
        else:
            reply = client.respond(question, build_system_prompt(context), previous_response_id)
    except Exception as exc:  # noqa: BLE001
        if mode == "code_interpreter" and _OPENAI_OK and isinstance(exc, openai.NotFoundError):
            # stale previous_response_id is already retried inside the client, so a 404
            # here means the attached file is gone on the Yandex side
            raise FileUnavailableError(str(exc)) from exc
        logger.warning("YandexGPT недоступен: %s", exc)
        return ChatReply(ERROR_MESSAGE)

    if not reply.text:
        return ChatReply(ERROR_MESSAGE)
    return ChatReply(reply.text, reply.response_id, reply.context_reset, reply.artifacts)

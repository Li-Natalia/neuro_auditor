"""YandexGPT client — Yandex AI Studio Responses API via the OpenAI SDK.

Client: ``openai.OpenAI(api_key=..., project=<folder_id>, base_url=".../v1")`` (the folder
goes into ``project``; no custom headers). Dialog context is kept with
``previous_response_id`` — the app stores ``response.id`` per chat session and sends it on
the next turn. Code Interpreter mode uploads the workbook via the Files API and attaches it
to an auto-created container.

Docs: https://aistudio.yandex.ru/docs/ru/ai-studio/concepts/openai-compatibility
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, NamedTuple

from app.core.config import settings

logger = logging.getLogger("fin-auditor")

_OPENAI_OK = False
try:  # the OpenAI SDK is the client library for Yandex AI Studio (shipped in requirements.txt)
    import openai  # type: ignore

    _OPENAI_OK = True
except Exception:  # pragma: no cover
    pass


@dataclass(frozen=True)
class Artifact:
    """A file produced by the model in Code Interpreter mode."""

    file_id: str
    filename: str


class YandexReply(NamedTuple):
    text: str
    response_id: str | None
    # True when the stored previous_response_id was rejected and the dialog chain restarted.
    context_reset: bool = False
    artifacts: tuple[Artifact, ...] = ()


def yandex_configured() -> bool:
    """True when the SDK is present and Yandex credentials are set."""
    return bool(_OPENAI_OK and settings.AI_YC_API_KEY and settings.AI_YC_FOLDER_ID)


def code_interpreter_enabled() -> bool:
    return bool(settings.AI_CODE_INTERPRETER_ENABLED and yandex_configured())


def _model_uri(folder_id: str, model: str) -> str:
    return model if model.startswith("gpt://") else f"gpt://{folder_id}/{model}"


class YandexGPTClient:
    """Thin wrapper around the OpenAI SDK configured for Yandex AI Studio."""

    def __init__(
        self,
        api_key: str,
        folder_id: str,
        base_url: str,
        model: str,
        *,
        ci_model: str | None = None,
        timeout: float | None = None,
    ) -> None:
        if not _OPENAI_OK:
            raise RuntimeError("Пакет 'openai' не установлен. Установите: pip install openai")

        self._folder_id = folder_id
        self._model_uri = _model_uri(folder_id, model)
        self._ci_model_uri = _model_uri(folder_id, ci_model or model)
        self._client = openai.OpenAI(
            api_key=api_key,
            project=folder_id,
            base_url=base_url,
            timeout=timeout,
        )

    # ------------------------------------------------------------------ core
    def _create(self, previous_response_id: str | None, **params: Any):
        """Call responses.create; if Yandex rejects a stale previous_response_id, retry once
        without it and report that the dialog chain was restarted."""
        if previous_response_id:
            try:
                response = self._client.responses.create(
                    previous_response_id=previous_response_id, **params
                )
                return response, False
            except (openai.BadRequestError, openai.NotFoundError) as exc:
                logger.warning(
                    "Yandex отклонил previous_response_id (%s: %s) — перезапуск цепочки диалога",
                    type(exc).__name__, exc,
                )
                return self._client.responses.create(**params), True
        return self._client.responses.create(**params), False

    def respond(
        self,
        question: str,
        instructions: str,
        previous_response_id: str | None = None,
        *,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> YandexReply:
        """Answer a question with the document context in ``instructions``."""
        logger.debug("Запрос к YandexGPT (%s), контекст: %s", self._model_uri, bool(previous_response_id))
        response, reset = self._create(
            previous_response_id,
            model=self._model_uri,
            instructions=instructions,
            input=question,
            temperature=settings.AI_TEMPERATURE if temperature is None else temperature,
            max_output_tokens=settings.AI_MAX_TOKENS if max_output_tokens is None else max_output_tokens,
            store=True,
        )
        return YandexReply((response.output_text or "").strip(), response.id, reset)

    # ----------------------------------------------------------------- files
    def upload_file(self, path: str, *, purpose: str, filename: str | None = None) -> str:
        """Upload a local file to the Yandex Files API and return its id.

        ``filename`` is the name the model sees inside the Code Interpreter container; it
        defaults to the on-disk name (usually a storage name with a timestamp prefix).
        """
        with open(path, "rb") as fh:
            return self._client.files.create(
                file=(filename or os.path.basename(path), fh), purpose=purpose
            ).id

    def download_file(self, file_id: str) -> bytes:
        return self._client.files.content(file_id).read()

    def delete_file(self, file_id: str) -> None:
        """Best-effort removal of a file from the Files API."""
        try:
            self._client.files.delete(file_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Не удалось удалить файл %s из Files API: %s", file_id, exc)

    # ------------------------------------------------------- code interpreter
    def respond_with_code_interpreter(
        self,
        question: str,
        instructions: str,
        previous_response_id: str | None = None,
        *,
        file_ids: list[str],
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> YandexReply:
        """Let the model analyse the attached files in an auto-created container."""
        tools = [{"type": "code_interpreter", "container": {"type": "auto", "file_ids": list(file_ids)}}]
        logger.debug(
            "Запрос к YandexGPT Code Interpreter (%s), файлов: %d, контекст: %s",
            self._ci_model_uri, len(file_ids), bool(previous_response_id),
        )
        response, reset = self._create(
            previous_response_id,
            model=self._ci_model_uri,
            instructions=instructions,
            input=question,
            tools=tools,
            tool_choice="auto",
            include=["code_interpreter_call.outputs"],
            temperature=settings.AI_TEMPERATURE if temperature is None else temperature,
            max_output_tokens=settings.AI_MAX_TOKENS if max_output_tokens is None else max_output_tokens,
            store=True,
            timeout=settings.AI_CI_TIMEOUT_SECONDS,
        )
        return YandexReply(
            (response.output_text or "").strip(), response.id, reset, _collect_artifacts(response)
        )


def _collect_artifacts(response: Any) -> tuple[Artifact, ...]:
    """Pull generated-file annotations (container_file_citation) out of a response."""
    found: dict[str, Artifact] = {}
    for item in getattr(response, "output", None) or []:
        if getattr(item, "type", None) == "code_interpreter_call":
            code = getattr(item, "code", None)
            if code:
                logger.debug("code_interpreter выполнил код:\n%s", code)
            continue
        for part in getattr(item, "content", None) or []:
            for ann in getattr(part, "annotations", None) or []:
                if getattr(ann, "type", None) != "container_file_citation":
                    continue
                file_id = getattr(ann, "file_id", None)
                if file_id and file_id not in found:
                    found[file_id] = Artifact(file_id, getattr(ann, "filename", None) or file_id)
    return tuple(found.values())


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
        ci_model=settings.AI_CI_MODEL or None,
        timeout=settings.AI_TIMEOUT_SECONDS,
    )


@lru_cache(maxsize=1)
def get_yandex_client() -> YandexGPTClient:
    """Return a cached YandexGPT client built from settings."""
    return _resolve_yandex_client()

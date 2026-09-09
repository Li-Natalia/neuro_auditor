"""Unit tests for the YandexGPT chatbot routing (no offline fallback)."""
import pytest

from app.ai import chatbot_model
from app.ai.chatbot_model import (
    CI_DISABLED_MESSAGE,
    ERROR_MESSAGE,
    NOT_CONFIGURED_MESSAGE,
    ChatReply,
    FileUnavailableError,
    generate_answer,
)
from app.ai.yandex_client import Artifact, YandexReply


class _FakeClient:
    def __init__(self, reply=None, error=None):
        self._reply = reply
        self._error = error
        self.calls = []

    def respond(self, question, instructions, previous_response_id=None, **kwargs):
        self.calls.append(("respond", question, instructions, previous_response_id))
        if self._error:
            raise self._error
        return self._reply

    def respond_with_code_interpreter(
        self, question, instructions, previous_response_id=None, *, file_ids, **kwargs
    ):
        self.calls.append(("ci", question, instructions, previous_response_id, tuple(file_ids)))
        if self._error:
            raise self._error
        return self._reply


def _use(monkeypatch, client, configured=True, ci=True):
    monkeypatch.setattr(chatbot_model, "yandex_configured", lambda: configured)
    monkeypatch.setattr(chatbot_model, "code_interpreter_enabled", lambda: ci)
    monkeypatch.setattr(chatbot_model, "get_yandex_client", lambda: client)


def test_not_configured_returns_message(monkeypatch):
    _use(monkeypatch, _FakeClient(), configured=False)
    assert generate_answer("Какие риски?", {}) == ChatReply(NOT_CONFIGURED_MESSAGE)


def test_answer_response_id_and_previous_id_passed(monkeypatch):
    fake = _FakeClient(YandexReply("Ликвидность в пределах нормы.", "resp_2"))
    _use(monkeypatch, fake)

    reply = generate_answer(
        "Оцени ликвидность", {"ratios": {"currentRatio": 1.6}}, previous_response_id="resp_1"
    )

    assert reply.answer == "Ликвидность в пределах нормы."
    assert reply.response_id == "resp_2" and reply.context_reset is False
    kind, question, instructions, prev = fake.calls[0]
    assert kind == "respond" and question == "Оцени ликвидность" and prev == "resp_1"
    assert "1.6" in instructions  # document context reached the system prompt


def test_error_returns_error_message(monkeypatch):
    _use(monkeypatch, _FakeClient(error=RuntimeError("boom")))
    assert generate_answer("Вопрос", {}) == ChatReply(ERROR_MESSAGE)


def test_empty_text_becomes_error_message(monkeypatch):
    _use(monkeypatch, _FakeClient(YandexReply("", "resp_x")))
    assert generate_answer("Вопрос", {}).answer == ERROR_MESSAGE


def test_context_reset_propagates(monkeypatch):
    _use(monkeypatch, _FakeClient(YandexReply("ок", "resp_new", context_reset=True)))
    reply = generate_answer("Вопрос", {}, previous_response_id="stale")
    assert reply.context_reset is True and reply.response_id == "resp_new"


def test_code_interpreter_mode_passes_file_and_returns_artifacts(monkeypatch):
    artifact = Artifact("file_1", "chart.png")
    fake = _FakeClient(YandexReply("12 строк", "resp_ci", artifacts=(artifact,)))
    _use(monkeypatch, fake)

    reply = generate_answer(
        "Сколько строк?", {}, mode="code_interpreter", file_id="file_0", filename="report.xlsx"
    )

    assert reply.answer == "12 строк" and reply.artifacts == (artifact,)
    kind, _, instructions, _, file_ids = fake.calls[0]
    assert kind == "ci" and file_ids == ("file_0",)
    assert "report.xlsx" in instructions and "code_interpreter" in instructions


def test_code_interpreter_disabled(monkeypatch):
    _use(monkeypatch, _FakeClient(), ci=False)
    reply = generate_answer("Вопрос", {}, mode="code_interpreter", file_id="f")
    assert reply.answer == CI_DISABLED_MESSAGE


def test_code_interpreter_missing_file_raises(monkeypatch):
    openai = pytest.importorskip("openai")
    httpx = pytest.importorskip("httpx")
    err = openai.NotFoundError(
        "no such file",
        response=httpx.Response(404, request=httpx.Request("POST", "https://example")),
        body=None,
    )
    _use(monkeypatch, _FakeClient(error=err))
    with pytest.raises(FileUnavailableError):
        generate_answer("Вопрос", {}, mode="code_interpreter", file_id="gone")

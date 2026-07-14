"""Unit tests for the LLM chatbot provider routing (no offline fallback)."""
from app.ai import chatbot_model
from app.ai.chatbot_model import ERROR_MESSAGE, NOT_CONFIGURED_MESSAGE, generate_answer
from app.core.config import settings


class _FakeYandexClient:
    def __init__(self, reply=None, error=None):
        self._reply = reply
        self._error = error
        self.calls = []

    def chat(self, messages, **kwargs):
        self.calls.append(messages)
        if self._error:
            raise self._error
        return self._reply


def test_no_provider_returns_unavailable_message(monkeypatch):
    monkeypatch.setattr(settings, "AI_PROVIDER", "auto")
    monkeypatch.setattr(chatbot_model, "yandex_configured", lambda: False)
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    answer = generate_answer("Какие риски?", {"balance": {}, "income": {}, "ratios": {}})
    assert answer == NOT_CONFIGURED_MESSAGE


def test_yandex_provider_answers(monkeypatch):
    fake = _FakeYandexClient(reply="Ликвидность в пределах нормы.")
    monkeypatch.setattr(settings, "AI_PROVIDER", "yandex")
    monkeypatch.setattr(chatbot_model, "yandex_configured", lambda: True)
    monkeypatch.setattr(chatbot_model, "get_yandex_client", lambda: fake)

    answer = generate_answer("Оцени ликвидность", {"ratios": {"currentRatio": 1.6}})

    assert answer == "Ликвидность в пределах нормы."
    # system prompt + user question were passed to the client
    assert fake.calls and fake.calls[0][-1]["role"] == "user"


def test_yandex_error_returns_error_message(monkeypatch):
    fake = _FakeYandexClient(error=RuntimeError("boom"))
    monkeypatch.setattr(settings, "AI_PROVIDER", "yandex")
    monkeypatch.setattr(chatbot_model, "yandex_configured", lambda: True)
    monkeypatch.setattr(chatbot_model, "get_yandex_client", lambda: fake)

    answer = generate_answer("Оцени ликвидность", {})

    assert answer == ERROR_MESSAGE


def test_empty_answer_becomes_error_message(monkeypatch):
    fake = _FakeYandexClient(reply="")
    monkeypatch.setattr(settings, "AI_PROVIDER", "yandex")
    monkeypatch.setattr(chatbot_model, "yandex_configured", lambda: True)
    monkeypatch.setattr(chatbot_model, "get_yandex_client", lambda: fake)

    assert generate_answer("Вопрос", {}) == ERROR_MESSAGE


def test_resolve_provider(monkeypatch):
    monkeypatch.setattr(settings, "AI_PROVIDER", "auto")
    monkeypatch.setattr(chatbot_model, "yandex_configured", lambda: True)
    assert chatbot_model._resolve_provider() == "yandex"

    monkeypatch.setattr(chatbot_model, "yandex_configured", lambda: False)
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    assert chatbot_model._resolve_provider() is None

    # forcing an unconfigured provider yields no provider (→ unavailable message)
    monkeypatch.setattr(settings, "AI_PROVIDER", "yandex")
    assert chatbot_model._resolve_provider() is None

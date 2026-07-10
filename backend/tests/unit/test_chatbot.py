"""Unit tests for the chatbot rule-based fallback and LLM provider routing."""
from app.ai import chatbot_model
from app.ai.chatbot_model import _rule_based_answer, generate_answer
from app.core.config import settings


def test_rule_based_answer_without_context():
    answer = _rule_based_answer("Какая выручка?", None)
    assert "данных анализа" in answer.lower() or "выручк" in answer.lower()


def test_rule_based_answer_with_context():
    context = {
        "balance": {"totalAssets": 1000, "equity": 500, "accountsReceivable": 100},
        "income": {"revenue": 2000, "netProfit": 200},
        "ratios": {"currentRatio": 2.0, "quickRatio": 1.5, "roa": 20, "roe": 40, "ros": 10, "debtToEquity": 0.2},
        "risks": [],
    }
    answer = _rule_based_answer("Какая выручка и прибыль?", context)
    assert "2,000" in answer


def test_generate_answer_falls_back_gracefully():
    # Without any provider configured the rule-based path is used
    answer = generate_answer("Какие риски?", {"balance": {}, "income": {}, "ratios": {}, "risks": []})
    assert isinstance(answer, str)
    assert len(answer) > 0


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


def test_yandex_provider_is_used_when_selected(monkeypatch):
    fake = _FakeYandexClient(reply="Чистая прибыль составила 200.")
    monkeypatch.setattr(settings, "AI_PROVIDER", "yandex")
    monkeypatch.setattr(chatbot_model, "get_yandex_client", lambda: fake)

    answer = generate_answer("Какая прибыль?", {"income": {"netProfit": 200}})

    assert answer == "Чистая прибыль составила 200."
    # System prompt + user question were passed to the client
    assert fake.calls and fake.calls[0][-1]["role"] == "user"


def test_yandex_error_falls_back_to_rule_based(monkeypatch):
    fake = _FakeYandexClient(error=RuntimeError("boom"))
    monkeypatch.setattr(settings, "AI_PROVIDER", "yandex")
    monkeypatch.setattr(chatbot_model, "get_yandex_client", lambda: fake)

    context = {"income": {"revenue": 2000, "netProfit": 200}}
    answer = generate_answer("Какая выручка?", context)

    # Rule-based responder kicks in and formats the revenue
    assert "2,000" in answer


def test_auto_provider_prefers_yandex_when_configured(monkeypatch):
    monkeypatch.setattr(settings, "AI_PROVIDER", "auto")
    monkeypatch.setattr(chatbot_model, "yandex_configured", lambda: True)
    assert chatbot_model._resolve_provider() == "yandex"

    monkeypatch.setattr(chatbot_model, "yandex_configured", lambda: False)
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    assert chatbot_model._resolve_provider() == "rule"

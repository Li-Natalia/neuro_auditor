"""Unit tests for the chatbot rule-based fallback."""
from app.ai.chatbot_model import _rule_based_answer, generate_answer


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
    # Without OPENAI_API_KEY the rule-based path is used
    answer = generate_answer("Какие риски?", {"balance": {}, "income": {}, "ratios": {}, "risks": []})
    assert isinstance(answer, str)
    assert len(answer) > 0

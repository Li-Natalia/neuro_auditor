"""Chatbot model: LLM-backed when a provider is configured, otherwise a robust
rule-based responder built from the document's financial data.

Provider resolution (``AI_PROVIDER`` setting):
- ``auto``  — YandexGPT if configured, else OpenAI if configured, else rule-based
- ``yandex`` / ``openai`` / ``rule`` — force a specific backend
"""
from __future__ import annotations

import logging
from typing import Any

from app.ai.nlp_pipeline import detect_intent
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


def _fmt(v: Any) -> str:
    try:
        return f"{float(v):,.0f}"
    except (TypeError, ValueError):
        return str(v)


def _rule_based_answer(question: str, context: dict | None) -> str:
    context = context or {}
    balance = context.get("balance", {})
    income = context.get("income", {})
    ratios = context.get("ratios", {})
    risks = context.get("risks", [])

    if not (balance or income or ratios):
        return (
            "К сожалению, по выбранному документу нет данных анализа. "
            "Загрузите отчёт и дождитесь завершения анализа, либо задайте вопрос без контекста."
        )

    intents = detect_intent(question)

    lines: list[str] = []
    if "revenue" in intents:
        lines.append(f"Выручка: {_fmt(income.get('revenue'))}; чистая прибыль: {_fmt(income.get('netProfit'))}.")
    if "profit" in intents:
        lines.append(
            f"Рентабельность: ROA {ratios.get('roa', 0)}%, ROE {ratios.get('roe', 0)}%, "
            f"ROS {ratios.get('ros', 0)}%."
        )
    if "liquidity" in intents:
        lines.append(
            f"Ликвидность: текущая {ratios.get('currentRatio', 0)} (норма ≥1.5), "
            f"быстрая {ratios.get('quickRatio', 0)} (норма ≥1.0)."
        )
    if "debt" in intents:
        lines.append(
            f"Долговая нагрузка: долг/капитал = {ratios.get('debtToEquity', 0)} (норма ≤1.0). "
            f"Дебиторская задолженность: {_fmt(balance.get('accountsReceivable'))}."
        )
    if "assets" in intents:
        lines.append(
            f"Активы: всего {_fmt(balance.get('totalAssets'))} "
            f"(оборотные {_fmt(balance.get('currentAssets'))}, внеоборотные {_fmt(balance.get('nonCurrentAssets'))}). "
            f"Капитал: {_fmt(balance.get('equity'))}."
        )
    if "cashflow" in intents:
        lines.append(
            "Денежные потоки: операционный, инвестиционный, финансовый — "
            f"см. раздел анализа."
        )
    if "risk" in intents or "general" in intents:
        if risks:
            counts = {"critical": 0, "medium": 0, "low": 0}
            for r in risks:
                lvl = r.get("level") if isinstance(r, dict) else r.level
                if isinstance(lvl, str):
                    pass
                else:
                    lvl = lvl.value
                counts[lvl] = counts.get(lvl, 0) + 1
            lines.append(
                f"Риски: 🔴 критических {counts.get('critical', 0)}, "
                f"🟡 средних {counts.get('medium', 0)}, 🟢 низких {counts.get('low', 0)}."
            )
        else:
            lines.append("Существенных рисков по документу не выявлено.")

    if not lines:
        lines.append(
            "Я могу ответить на вопросы о выручке, прибыли, ликвидности, долговой "
            "нагрузке, активах и рисках по загруженному документу."
        )

    return " ".join(lines)


def _resolve_provider() -> str:
    """Decide which backend to use for this request."""
    provider = (settings.AI_PROVIDER or "auto").lower()
    if provider in {"yandex", "openai", "rule"}:
        return provider
    # auto
    if yandex_configured():
        return "yandex"
    if _OPENAI_OK and settings.OPENAI_API_KEY:
        return "openai"
    return "rule"


def _messages(question: str, context: dict | None) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": build_system_prompt(context)},
        {"role": "user", "content": question},
    ]


def _answer_with_yandex(question: str, context: dict | None) -> str:
    client = get_yandex_client()
    answer = client.chat(_messages(question, context))
    return answer or _rule_based_answer(question, context)


def _answer_with_openai(question: str, context: dict | None) -> str:
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=_messages(question, context),
        temperature=settings.AI_TEMPERATURE,
    )
    return (resp.choices[0].message.content or "").strip() or _rule_based_answer(question, context)


def generate_answer(question: str, context: dict | None = None) -> str:
    """Generate an answer, preferring the configured LLM provider.

    Any provider error degrades gracefully to the rule-based responder so the
    chat endpoint always returns something useful.
    """
    provider = _resolve_provider()

    if provider == "yandex":
        try:
            return _answer_with_yandex(question, context)
        except Exception as exc:  # noqa: BLE001
            logger.warning("YandexGPT недоступен, использую резервный ответ: %s", exc)
            return _rule_based_answer(question, context)

    if provider == "openai":
        try:
            return _answer_with_openai(question, context)
        except Exception as exc:  # noqa: BLE001
            logger.warning("OpenAI недоступен, использую резервный ответ: %s", exc)
            return _rule_based_answer(question, context)

    return _rule_based_answer(question, context)

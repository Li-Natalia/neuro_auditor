"""Chatbot model: LLM-backed when OPENAI_API_KEY is set, otherwise a robust
rule-based responder built from the document's financial data.
"""
from __future__ import annotations

import json
from typing import Any

from app.ai.nlp_pipeline import detect_intent
from app.ai.prompts import build_prompt
from app.core.config import settings

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


def generate_answer(question: str, context: dict | None = None) -> str:
    """Generate an answer, preferring the LLM when configured."""
    if _OPENAI_OK and settings.OPENAI_API_KEY:
        try:
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            prompt = build_prompt(question, context or {})
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": question},
                ],
                temperature=0.2,
            )
            return resp.choices[0].message.content or _rule_based_answer(question, context)
        except Exception:
            # Fallback to rule-based on any API error
            return _rule_based_answer(question, context)
    return _rule_based_answer(question, context)

"""Prompt templates for the LLM chatbot (Yandex GPT / OpenAI)."""
from __future__ import annotations

SYSTEM_PROMPT = """Ты — финансовый аудитор-ассистент Нейроаудитор.
Отвечай на вопросы пользователя на русском языке, опираясь на предоставленные
финансовые показатели загруженного документа. Будь кратким, точным и по делу.
Если данных недостаточно — честно сообщи об этом и предложи нужные показатели."""

CONTEXT_TEMPLATE = """
Контекст документа:
- Баланс: {balance}
- ОПУ: {income}
- Коэффициенты: {ratios}
- Риски: {risks}
"""


def build_system_prompt(context: dict | None) -> str:
    """Compose the system prompt with the document context.

    Missing context keys are tolerated (an empty document yields an empty
    context block) so the LLM path never raises on incomplete data.
    """
    context = context or {}
    context_block = CONTEXT_TEMPLATE.format(
        balance=context.get("balance") or {},
        income=context.get("income") or {},
        ratios=context.get("ratios") or {},
        risks=context.get("risks") or [],
    )
    return f"{SYSTEM_PROMPT}\n{context_block}"

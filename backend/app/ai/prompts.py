"""Prompt templates for the YandexGPT chatbot (Yandex AI Studio)."""
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


CODE_INTERPRETER_ADDENDUM = """
К запросу приложен файл финансовой отчётности «{filename}» — он доступен в рабочей
директории контейнера под этим именем. Все расчёты выполняй через инструмент
code_interpreter (pandas / openpyxl) по данным из файла, а не по памяти.
Отвечай на русском языке и кратко: не пересказывай план и промежуточные шаги, приведи
исходные значения, формулу и результат. Если создаёшь файлы (таблицы, графики) — дай
в ответе ссылку на каждый созданный файл."""


def build_code_interpreter_prompt(context: dict | None, filename: str) -> str:
    """System prompt for Code Interpreter mode: document context + file-analysis instructions."""
    return build_system_prompt(context) + CODE_INTERPRETER_ADDENDUM.format(filename=filename)

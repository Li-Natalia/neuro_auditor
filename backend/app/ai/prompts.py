"""Prompt templates for the LLM chatbot (used when OPENAI_API_KEY is set)."""

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


def build_prompt(question: str, context: dict) -> str:
    return f"{SYSTEM_PROMPT}\n\n{CONTEXT_TEMPLATE.format(**context)}\n\nВопрос: {question}"

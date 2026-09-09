"""Picks the chat mode for ``mode="auto"`` — without an extra model call.

The fast path (an answer from the document's precomputed figures and risks) is the
default: it responds in a second and costs one short YandexGPT request. Code Interpreter
takes 1–3 minutes and runs a large model plus code execution, so "auto" routes to it only
when the question clearly needs the workbook itself: a file, a table, a chart, an export,
or a recalculation / check "по файлу".
"""
from __future__ import annotations

import re

_CI_INTENT = re.compile(
    r"(?:"
    # an output artifact or an explicit file format
    r"\bcsv\b|\bxlsx?\b|\bexcel\b|\bjson\b"
    r"|график|диаграмм|гистограмм|визуализ"
    r"|(?:сдела|сформир|состав|постро|созда|выгруз|сохран|подготов)\w*(?:\s+\S+){0,3}\s+таблиц"
    r"|сохрани|выгруз|экспорт|скача"
    # the source file itself
    r"|по файлу|из файла|в файле|файл\w*"
    # recomputation / verification against the source
    r"|пересчита|перепровер|провер(?:ь|ить|ка)\s+расч|исходн\w+\s+(?:данн|цифр|значен)"
    r")",
    re.IGNORECASE,
)


def wants_code_interpreter(message: str) -> bool:
    """True when the question asks for something only the workbook can provide."""
    return bool(_CI_INTENT.search(message or ""))

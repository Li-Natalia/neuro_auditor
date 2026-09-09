"""Data cleaning helpers for parsed financial data."""
from __future__ import annotations

import re
from typing import Any


_NON_NUMERIC = re.compile(r"[^\d,.]")


def _normalize_separators(core: str) -> str:
    """Normalize thousands/decimal separators to a Python-parseable string.

    - If both ',' and '.' are present, the right-most one is the decimal
      separator and the other groups thousands.
    - If only ',' is present, it is the decimal separator unless it looks like
      a thousands grouping (1-3 digits, then exactly 3 digits), or repeats.
    - If only '.' is present, a lone dot is decimal; repeated dots group
      thousands.
    """
    has_comma = "," in core
    has_dot = "." in core
    if has_comma and has_dot:
        if core.rfind(",") > core.rfind("."):
            return core.replace(".", "").replace(",", ".")  # comma is decimal
        return core.replace(",", "")  # dot is decimal
    if has_comma:
        if core.count(",") > 1:
            return core.replace(",", "")  # thousands grouping
        int_part, dec_part = core.split(",")
        if len(dec_part) == 3 and 1 <= len(int_part) <= 3:
            return int_part + dec_part  # thousands separator
        return int_part + "." + dec_part  # decimal separator
    if has_dot and core.count(".") > 1:
        return core.replace(".", "")  # thousands grouping
    return core


def to_float(value: Any) -> float:
    """Best-effort conversion of Excel cell values to float."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        s = value.strip().replace("\xa0", "").replace(" ", "")
        if not s or s in {"-", "—", "н/д", "Н/Д"}:
            return 0.0
        # Handle parentheses / leading minus as negatives, e.g. (1 234) -> -1234
        negative = (s.startswith("(") and s.endswith(")")) or s.startswith("-")
        # Sign is captured above; keep only digits and separators.
        core = _normalize_separators(_NON_NUMERIC.sub("", s))
        try:
            val = float(core) if core else 0.0
        except ValueError:
            return 0.0
        return -val if negative else val
    return 0.0


def clean_numeric_dict(data: dict[str, Any], keys: list[str]) -> dict[str, float]:
    return {k: to_float(data.get(k)) for k in keys}

"""Data cleaning helpers for parsed financial data."""
from __future__ import annotations

import re
from typing import Any


_NON_NUMERIC = re.compile(r"[^\d,.\-]")


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
        # Handle parentheses as negatives, e.g. (1 234) -> -1234
        negative = s.startswith("(") and s.endswith(")")
        s = _NON_NUMERIC.sub("", s.replace(",", "."))
        try:
            val = float(s) if s else 0.0
            return -val if negative else val
        except ValueError:
            return 0.0
    return 0.0


def clean_numeric_dict(data: dict[str, Any], keys: list[str]) -> dict[str, float]:
    return {k: to_float(data.get(k)) for k in keys}


def find_row(df, keywords: list[str]):
    """Return the first row Series whose index label contains any keyword."""
    if df is None or df.empty:
        return None
    labels = [str(idx).lower() for idx in df.index]
    for kw in keywords:
        for i, label in enumerate(labels):
            if kw.lower() in label:
                return df.iloc[i]
    return None

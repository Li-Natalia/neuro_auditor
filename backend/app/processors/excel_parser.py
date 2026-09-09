"""Excel parsing for financial statements (IFRS / RSBU).

The parser is heuristic: it scans an Excel workbook for sheets that look like the
balance sheet, income statement and cash flow statement, then locates rows by
label to extract headline figures. Robust enough for well-structured reporting
templates; gracefully returns zeros when a figure is not found.

Design notes
------------
* Line items are described by :class:`LineItem` specs: an ordered tuple of
  ``include`` regexes (most specific first) plus ``exclude`` regexes. A row is
  a candidate only if some include pattern matches its normalised label and no
  exclude pattern does. The first include pattern (in order) with at least one
  candidate row wins, and the first such row in sheet order is taken. This is
  what keeps "Оборотные активы" from matching "Внеоборотные активы", "Капитал"
  from matching "Уставный капитал", etc.
* The reporting period is chosen deterministically: the header row is
  detected, every header cell is turned into a sortable period key and the
  column with the latest period wins (ties -> right-most). Values are read from
  that single column and a legitimate ``0`` is kept as ``0.0``.
* ``.xls`` files are read with ``xlrd`` (which only supports the legacy
  format), everything else with ``openpyxl``.
"""
from __future__ import annotations

import datetime as _dt
import logging
import math
import numbers
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from app.utils.data_cleaners import to_float

logger = logging.getLogger("fin-auditor")


# ---------------------------------------------------------------------------
# Label matching
# ---------------------------------------------------------------------------
_WHITESPACE_RE = re.compile(r"\s+")


def normalise_label(label: Any) -> str:
    """Lower-case, fold ``ё``→``е`` and collapse whitespace (incl. NBSP)."""
    text = str(label).lower().replace("ё", "е")
    return _WHITESPACE_RE.sub(" ", text).strip()


@dataclass(frozen=True)
class LineItem:
    """Collision-proof spec for locating one line item by its row label.

    ``include`` patterns are ordered most-specific-first; ``exclude`` patterns
    veto a row regardless of which include pattern matched. Both are searched
    (``re.search``) against the *normalised* label, so patterns are written in
    lower case with ``е`` instead of ``ё``.
    """

    include: tuple[str, ...]
    exclude: tuple[str, ...] = ()
    _include_re: tuple[re.Pattern[str], ...] = field(
        init=False, repr=False, compare=False, default=()
    )
    _exclude_re: tuple[re.Pattern[str], ...] = field(
        init=False, repr=False, compare=False, default=()
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "_include_re", tuple(re.compile(p) for p in self.include))
        object.__setattr__(self, "_exclude_re", tuple(re.compile(p) for p in self.exclude))

    def match_rank(self, label: Any) -> int | None:
        """Index of the first include pattern matching ``label`` or ``None``.

        ``None`` is also returned when any exclude pattern matches. Lower rank
        means a more specific match.
        """
        text = normalise_label(label)
        if any(p.search(text) for p in self._exclude_re):
            return None
        for rank, pattern in enumerate(self._include_re):
            if pattern.search(text):
                return rank
        return None


BALANCE_ITEMS: dict[str, LineItem] = {
    "totalAssets": LineItem(
        include=(
            r"\bитого актив",
            r"\bвалюта баланса",
            r"\bактивы всего",
            r"\btotal assets",
            r"\bбаланс\b",
        ),
    ),
    "currentAssets": LineItem(
        include=(
            r"\bитого оборотн\w* актив",
            r"\bоборотн\w* актив",
            r"\bитого по разделу ii\b",
            r"\bтекущ\w* актив",
            r"\bcurrent assets",
        ),
        exclude=(r"внеоборотн", r"non-current"),
    ),
    "nonCurrentAssets": LineItem(
        include=(
            r"\bитого внеоборотн\w* актив",
            r"\bвнеоборотн\w* актив",
            r"\bитого по разделу i\b",
            r"\bnon-current assets",
            r"\bдолгосрочн\w* актив",
        ),
    ),
    "totalLiabilities": LineItem(
        include=(
            r"\bобязательства? всего",
            r"\bитого обязательств",
            r"\bвсего обязательств",
            r"\btotal liabilities",
        ),
        exclude=(r"капитал", r"equity"),
    ),
    "currentLiabilities": LineItem(
        include=(
            r"\bкраткосрочн\w* обязательств",
            r"\bтекущ\w* обязательств",
            r"\bcurrent liabilities",
        ),
        exclude=(r"прочие", r"долгосрочн"),
    ),
    "equity": LineItem(
        include=(
            r"\bитого капитал",
            r"\bкапитал и резервы",
            r"\bитого по разделу iii\b",
            r"\bсобственн\w* капитал",
            r"\btotal equity",
            r"\bequity\b",
            r"\bкапитал\b",
        ),
        exclude=(
            r"уставн",
            r"добавочн",
            r"резервн",
            r"оборотн",
            r"заемн",
            r"обязательств",
            r"liabilities",
            r"share capital",
            r"working capital",
        ),
    ),
    "inventory": LineItem(include=(r"\bзапасы", r"\binventor")),
    "accountsReceivable": LineItem(
        include=(r"\bдебиторск", r"\baccounts receivable", r"\bдебиторка"),
    ),
    "cash": LineItem(
        include=(r"\bденежные средства", r"\bденьги", r"\bcash\b"),
        exclude=(r"поток", r"движени", r"изменени"),
    ),
}

INCOME_ITEMS: dict[str, LineItem] = {
    "revenue": LineItem(include=(r"\bвыручка", r"\brevenue", r"\bдоходы от реализации")),
    "costOfSales": LineItem(
        include=(r"\bсебестоимость", r"\bcost of sales", r"\bcost of revenue"),
    ),
    "grossProfit": LineItem(include=(r"\bваловая прибыль", r"\bgross profit")),
    "operatingExpenses": LineItem(
        include=(
            r"\bкоммерческие и управленческие",
            r"\bоперационные расходы",
            r"\boperating expenses",
        ),
    ),
    "operatingProfit": LineItem(
        include=(
            r"\bприбыль (\(убыток\) )?от продаж",
            r"\boperating profit",
            r"\bприбыль от операций",
        ),
    ),
    "netProfit": LineItem(include=(r"\bчистая прибыль", r"\bnet profit", r"\bnet income")),
    "interestExpense": LineItem(include=(r"\bпроценты к уплате", r"\binterest expense")),
}

CASHFLOW_ITEMS: dict[str, LineItem] = {
    "operatingCashFlow": LineItem(
        include=(
            r"\bоперационн\w* деятельност",
            r"\bсальдо денежных потоков от текущих операций",
            r"\bденежный поток от операционной",
            r"\boperating activities",
        ),
    ),
    "investingCashFlow": LineItem(
        include=(r"\bинвестиционн\w* деятельност", r"\binvesting activities"),
    ),
    "financingCashFlow": LineItem(
        include=(r"\bфинансов\w* деятельност", r"\bfinancing activities"),
    ),
    "netCashFlow": LineItem(
        include=(
            r"\bчист\w* денежн\w* поток",
            r"\bизменение денежных средств",
            r"\bnet change in cash",
        ),
    ),
}

SHEET_HINTS = {
    "balance": ["баланс", "balance", "активы", "balance sheet"],
    "income": ["прибыль", "убыток", "income", "p&l", "финансовые результаты"],
    "cashflow": ["денежн", "cash flow", "движение денежных"],
}


# ---------------------------------------------------------------------------
# Cell helpers
# ---------------------------------------------------------------------------
_NUMERIC_TEXT_RE = re.compile(r"[(\-−–—]?\d[\d.,]*\)?")


def _is_blank(cell: Any) -> bool:
    """True for ``None``, NaN/NaT and empty/whitespace-only strings."""
    if cell is None:
        return True
    if isinstance(cell, str):
        return not cell.strip()
    try:
        return bool(pd.isna(cell))
    except (TypeError, ValueError):
        return False


def _is_number(cell: Any) -> bool:
    return isinstance(cell, numbers.Real) and not isinstance(cell, bool)


def _is_numeric_cell(cell: Any) -> bool:
    """A real number or a string that looks like one (``1 234,56``, ``(500)``)."""
    if _is_number(cell):
        return not math.isnan(float(cell))
    if isinstance(cell, str):
        compact = cell.strip().replace("\xa0", "").replace(" ", "")
        return bool(compact) and _NUMERIC_TEXT_RE.fullmatch(compact) is not None
    return False


def _cell_to_float(cell: Any) -> float:
    """``to_float`` that is also safe for NaN and numpy scalars."""
    if _is_blank(cell):
        return 0.0
    if _is_number(cell):
        return float(cell)
    return to_float(cell)


# ---------------------------------------------------------------------------
# Reporting period / header detection
# ---------------------------------------------------------------------------
_HEADER_SCAN_ROWS = 10
_DATE_RE = re.compile(r"(\d{2})\.(\d{2})\.(\d{4})")
_BARE_YEAR_RE = re.compile(r"(?<!\d)((?:19|20)\d{2})(?!\d)")
_YEAR_MIN, _YEAR_MAX = 1990, 2100


@dataclass(frozen=True)
class HeaderInfo:
    """Where the header row is and which column holds the reporting period."""

    row_index: int
    value_col: int
    period_label: str | None
    #: Columns whose header cell carries a period key (used as the fallback
    #: pool when the chosen cell is blank); empty when no header cell had one.
    period_cols: tuple[int, ...] = ()


def _period_key(cell: Any) -> tuple[int, int, int] | None:
    """Sortable ``(year, month, day)`` for a header cell, or ``None``.

    * datetime / ``pd.Timestamp`` → ``(y, m, d)``
    * integral number in 1990..2100 → ``(y, 12, 31)``
    * string with ``dd.mm.yyyy`` → ``(y, m, d)``
    * string containing a bare four-digit year → ``(y, 12, 31)``
    """
    if _is_blank(cell):
        return None
    if isinstance(cell, _dt.date):  # datetime.datetime / pd.Timestamp subclass date
        return (cell.year, cell.month, cell.day)
    if _is_number(cell):
        value = float(cell)
        if value.is_integer() and _YEAR_MIN <= int(value) <= _YEAR_MAX:
            return (int(value), 12, 31)
        return None
    if isinstance(cell, str):
        m = _DATE_RE.search(cell)
        if m:
            day, month, year = (int(g) for g in m.groups())
            if 1 <= month <= 12 and 1 <= day <= 31 and _YEAR_MIN <= year <= _YEAR_MAX:
                return (year, month, day)
        m = _BARE_YEAR_RE.search(cell)
        if m:
            return (int(m.group(1)), 12, 31)
    return None


def _period_label(cell: Any) -> str:
    if isinstance(cell, _dt.date):
        return cell.strftime("%d.%m.%Y")
    if _is_number(cell) and float(cell).is_integer():
        return str(int(cell))
    return str(cell).strip()


def _is_header_cell(cell: Any) -> bool:
    """Blank, period-like (date / year) or non-numeric text."""
    if _is_blank(cell):
        return True
    if _period_key(cell) is not None:
        return True
    if isinstance(cell, str):
        return not _is_numeric_cell(cell)
    return False


def _detect_header(df: pd.DataFrame) -> HeaderInfo | None:
    """Locate the header row within the first rows of a statement sheet.

    The header row is the first row where every value-column cell is blank or
    non-numeric (text, date or a year) and at least one is non-blank. The value
    column is the one with the latest period key (ties → right-most); when no
    header cell carries a period key, the right-most non-blank header cell.
    """
    n_cols = df.shape[1]
    if n_cols < 2:
        return None
    for row_index in range(min(_HEADER_SCAN_ROWS, len(df))):
        cells = [df.iat[row_index, col] for col in range(1, n_cols)]
        if not all(_is_header_cell(c) for c in cells):
            continue
        if all(_is_blank(c) for c in cells):
            continue
        keyed = [(key, offset) for offset, c in enumerate(cells) if (key := _period_key(c))]
        if keyed:
            _, best = max(keyed)  # latest period; on ties the larger offset wins
            period_cols = tuple(offset + 1 for _, offset in keyed)
        else:
            best = max(offset for offset, c in enumerate(cells) if not _is_blank(c))
            period_cols = ()
        return HeaderInfo(
            row_index=row_index,
            value_col=best + 1,
            period_label=_period_label(cells[best]),
            period_cols=period_cols,
        )
    return None


def _rightmost_numeric_col(df: pd.DataFrame) -> int:
    """Right-most column (after the label column) containing any numeric cell."""
    for col in range(df.shape[1] - 1, 0, -1):
        if any(_is_numeric_cell(c) for c in df.iloc[:, col]):
            return col
    return df.shape[1] - 1


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------
def _prepare(df: pd.DataFrame) -> pd.DataFrame:
    """Drop fully blank rows/columns, renumber and use plain Python scalars."""
    df = df.dropna(axis=0, how="all").dropna(axis=1, how="all").reset_index(drop=True)
    df.columns = range(df.shape[1])
    return df.astype(object)


def _row_value(row: pd.Series, value_col: int, fallback_cols: tuple[int, ...]) -> float:
    """Value of the period column (``0`` is kept); blank → right-most numeric."""
    cell = row[value_col]
    if not _is_blank(cell):
        return _cell_to_float(cell)
    for col in reversed(fallback_cols):
        if col == value_col:
            continue
        candidate = row[col]
        if _is_numeric_cell(candidate):
            return _cell_to_float(candidate)
    return 0.0


def _extract(
    df: pd.DataFrame | None, items: dict[str, LineItem]
) -> tuple[dict[str, float], HeaderInfo | None]:
    """Extract every line item from a statement sheet (0.0 when not found)."""
    result = {key: 0.0 for key in items}
    if df is None or df.empty:
        return result, None
    df = _prepare(df)
    if df.shape[1] < 2 or df.empty:
        return result, None

    header = _detect_header(df)
    if header is not None:
        first_data_row = header.row_index + 1
        value_col = header.value_col
        fallback_cols = header.period_cols or tuple(range(1, df.shape[1]))
    else:
        first_data_row = 0
        value_col = _rightmost_numeric_col(df)
        fallback_cols = tuple(range(1, df.shape[1]))

    labels = [normalise_label(v) for v in df.iloc[:, 0].tolist()]
    for key, item in items.items():
        best: tuple[int, int] | None = None  # (rank, row position)
        for pos in range(first_data_row, len(labels)):
            rank = item.match_rank(labels[pos])
            if rank is None:
                continue
            if best is None or rank < best[0]:
                best = (rank, pos)
            if rank == 0:
                break  # most specific pattern, earliest row: cannot improve
        if best is not None:
            result[key] = _row_value(df.iloc[best[1]], value_col, fallback_cols)
    return result, header


def _reconcile_balance(balance: dict[str, float]) -> list[str]:
    """Fill gaps / fix inconsistencies between the balance-sheet totals.

    Mutates ``balance`` in place and returns human-readable warnings.
    """
    warnings: list[str] = []
    total = float(balance.get("totalAssets") or 0.0)
    current = float(balance.get("currentAssets") or 0.0)
    non_current = float(balance.get("nonCurrentAssets") or 0.0)
    equity = float(balance.get("equity") or 0.0)

    if not non_current and total > 0:
        non_current = max(total - current, 0.0)
        balance["nonCurrentAssets"] = non_current
        warnings.append(
            "Внеоборотные активы не найдены — рассчитаны как итого активов минус "
            f"оборотные активы ({non_current:,.0f})."
        )

    if total > 0 and (not current or abs(current + non_current - total) > 0.01 * total):
        fixed = max(total - non_current, 0.0)
        if not current:
            warnings.append(
                "Оборотные активы не найдены — рассчитаны как итого активов минус "
                f"внеоборотные активы ({fixed:,.0f})."
            )
        else:
            warnings.append(
                f"Оборотные ({current:,.0f}) + внеоборотные ({non_current:,.0f}) активы "
                f"не сходятся с итогом активов ({total:,.0f}); оборотные активы "
                f"заменены на {fixed:,.0f}."
            )
        current = fixed
        balance["currentAssets"] = current

    if not total:
        total = current + non_current
        balance["totalAssets"] = total
        if total:
            warnings.append(
                "Итого активов не найдено — рассчитано как сумма оборотных и "
                f"внеоборотных активов ({total:,.0f})."
            )

    total_liabilities = float(balance.get("totalLiabilities") or 0.0)
    if not total_liabilities or total_liabilities == total:
        fixed = max(total - equity, 0.0)
        if total_liabilities and total_liabilities == total:
            warnings.append(
                f"Обязательства ({total_liabilities:,.0f}) совпадают с итогом баланса — "
                "вероятно, взят итог пассива; заменены на итого активов минус капитал "
                f"({fixed:,.0f})."
            )
        elif fixed:
            warnings.append(
                "Обязательства не найдены — рассчитаны как итого активов минус "
                f"капитал ({fixed:,.0f})."
            )
        balance["totalLiabilities"] = fixed

    for message in warnings:
        logger.info("Balance reconciliation: %s", message)
    return warnings


# ---------------------------------------------------------------------------
# Workbook level
# ---------------------------------------------------------------------------
def _engine_for(file_path: str | Path) -> str:
    """``xlrd`` for legacy ``.xls`` workbooks, ``openpyxl`` for everything else."""
    return "xlrd" if Path(file_path).suffix.lower() == ".xls" else "openpyxl"


def _find_sheets(xls: pd.ExcelFile) -> dict[str, pd.DataFrame | None]:
    found: dict[str, pd.DataFrame | None] = {"balance": None, "income": None, "cashflow": None}
    for sheet in xls.sheet_names:
        name = sheet.lower()
        for key, hints in SHEET_HINTS.items():
            if found[key] is None and any(h in name for h in hints):
                found[key] = xls.parse(sheet_name=sheet, header=None)
    # Fallback: assume first 3 sheets
    sheets = xls.sheet_names
    for key, idx in zip(["balance", "income", "cashflow"], range(3)):
        if found[key] is None and len(sheets) > idx:
            found[key] = xls.parse(sheet_name=sheets[idx], header=None)
    return found


def parse_workbook(file_path: str) -> dict:
    """Parse an Excel workbook into balance / income / cashflow dicts.

    Returns ``{"balance": {...}, "income": {...}, "cashflow": {...},
    "meta": {"period": <label or None>, "warnings": [...]}}``. The three
    statement dicts always contain every key (``0.0`` when not found).
    """
    with pd.ExcelFile(file_path, engine=_engine_for(file_path)) as xls:
        sheets = _find_sheets(xls)

    balance, balance_header = _extract(sheets["balance"], BALANCE_ITEMS)
    income, income_header = _extract(sheets["income"], INCOME_ITEMS)
    cashflow, cashflow_header = _extract(sheets["cashflow"], CASHFLOW_ITEMS)

    warnings = _reconcile_balance(balance)

    # Derived: _extract always inserts every key (0.0 when the line item was
    # not found), so derive from the other fields whenever the value is absent.
    if not income.get("grossProfit"):
        income["grossProfit"] = max(
            income.get("revenue", 0) - income.get("costOfSales", 0), 0
        )
    if not income.get("operatingProfit"):
        income["operatingProfit"] = max(
            income.get("grossProfit", 0) - income.get("operatingExpenses", 0), 0
        )
    if not cashflow.get("netCashFlow"):
        cashflow["netCashFlow"] = (
            cashflow.get("operatingCashFlow", 0)
            + cashflow.get("investingCashFlow", 0)
            + cashflow.get("financingCashFlow", 0)
        )

    headers = (balance_header, income_header, cashflow_header)
    period = next((h.period_label for h in headers if h and h.period_label), None)
    return {
        "balance": balance,
        "income": income,
        "cashflow": cashflow,
        "meta": {"period": period, "warnings": warnings},
    }

"""Excel parsing for financial statements (IFRS / RSBU).

The parser is heuristic: it scans an Excel workbook for sheets that look like the
balance sheet, income statement and cash flow statement, then locates rows by
keyword to extract headline figures. Robust enough for well-structured
reporting templates; gracefully returns zeros when a figure is not found.
"""
from __future__ import annotations

import pandas as pd

from app.utils.data_cleaners import find_row, to_float

BALANCE_KEYWORDS = {
    "totalAssets": ["итого актив", "валюта баланса", "total assets", "активы всего"],
    "currentAssets": ["оборотные активы", "текущие активы", "current assets"],
    "nonCurrentAssets": ["внеоборотные активы", "non-current assets", "долгосрочные активы"],
    "totalLiabilities": ["итого пассив", "обязательства всего", "total liabilities"],
    "currentLiabilities": ["краткосрочные обязательства", "текущие обязательства", "current liabilities"],
    "equity": ["капитал", "собственный капитал", "equity", "итого капитал"],
    "inventory": ["запасы", "inventory"],
    "accountsReceivable": ["дебиторская задолженность", "accounts receivable", "дебиторка"],
    "cash": ["денежные средства", "деньги", "cash"],
}

INCOME_KEYWORDS = {
    "revenue": ["выручка", "выручка от продаж", "revenue", "доходы от реализации"],
    "costOfSales": ["себестоимость", "cost of sales", "cost of revenue"],
    "grossProfit": ["валовая прибыль", "gross profit"],
    "operatingExpenses": ["коммерческие и управленческие", "операционные расходы", "operating expenses"],
    "operatingProfit": ["прибыль от продаж", "operating profit", "прибыль от операций"],
    "netProfit": ["чистая прибыль", "net profit", "net income"],
    "interestExpense": ["проценты к уплате", "interest expense"],
}

CASHFLOW_KEYWORDS = {
    "operatingCashFlow": ["операционная деятельность", "operating activities", "денежный поток от операционной"],
    "investingCashFlow": ["инвестиционная деятельность", "investing activities"],
    "financingCashFlow": ["финансовая деятельность", "financing activities"],
    "netCashFlow": ["чистый денежный поток", "net change in cash", "изменение денежных средств"],
}

SHEET_HINTS = {
    "balance": ["баланс", "balance", "активы", "balance sheet"],
    "income": ["прибыль", "убыток", "income", "p&l", "финансовые результаты"],
    "cashflow": ["денежн", "cash flow", "движение денежных"],
}


def _pick_value_column(row) -> float:
    """Pick the most likely numeric value column from a row (last numeric-like cell)."""
    if row is None:
        return 0.0
    values = list(row.values) if hasattr(row, "values") else list(row)
    numeric = [to_float(v) for v in values]
    numeric = [v for v in numeric if v != 0.0]
    return numeric[-1] if numeric else to_float(values[-1]) if values else 0.0


def _find_sheets(xls: pd.ExcelFile) -> dict[str, pd.DataFrame | None]:
    found = {"balance": None, "income": None, "cashflow": None}
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
    """Parse an Excel workbook into balance / income / cashflow dicts."""
    xls = pd.ExcelFile(file_path, engine="openpyxl")
    sheets = _find_sheets(xls)

    def _extract(df, keywords):
        # Promote first non-null column as the index for keyword lookup
        result = {}
        if df is None:
            return {k: 0.0 for k in keywords}
        df = df.dropna(how="all")
        label_col = df.columns[0]
        value_cols = df.columns[1:]
        for key, kws in keywords.items():
            mask = df[label_col].astype(str).str.lower()
            match = None
            for kw in kws:
                m = mask[mask.str.contains(kw, na=False)]
                if not m.empty:
                    match = df.loc[m.index].iloc[0]
                    break
            if match is not None:
                # take last non-null numeric value
                vals = [to_float(match[c]) for c in value_cols]
                vals = [v for v in vals if v != 0.0]
                result[key] = vals[-1] if vals else 0.0
            else:
                result[key] = 0.0
        return result

    balance = _extract(sheets["balance"], BALANCE_KEYWORDS)
    income = _extract(sheets["income"], INCOME_KEYWORDS)
    cashflow = _extract(sheets["cashflow"], CASHFLOW_KEYWORDS)

    # Derived
    balance.setdefault("nonCurrentAssets", max(balance.get("totalAssets", 0) - balance.get("currentAssets", 0), 0))
    income.setdefault("grossProfit", max(income.get("revenue", 0) - income.get("costOfSales", 0), 0))
    income.setdefault("operatingProfit", max(income.get("grossProfit", 0) - income.get("operatingExpenses", 0), 0))
    cashflow.setdefault(
        "netCashFlow",
        cashflow.get("operatingCashFlow", 0)
        + cashflow.get("investingCashFlow", 0)
        + cashflow.get("financingCashFlow", 0),
    )

    return {"balance": balance, "income": income, "cashflow": cashflow}

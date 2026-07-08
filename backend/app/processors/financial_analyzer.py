"""Financial ratio calculations from parsed statements."""
from __future__ import annotations

from typing import Any


def safe_div(a: float, b: float) -> float:
    return float(a) / float(b) if b not in (0, None) else 0.0


def compute_ratios(balance: dict[str, Any], income: dict[str, Any]) -> dict[str, float]:
    """Compute the headline financial ratios."""
    current_assets = float(balance.get("currentAssets", 0))
    inventory = float(balance.get("inventory", 0) or 0)
    current_liab = float(balance.get("currentLiabilities", 0))
    total_assets = float(balance.get("totalAssets", 0))
    equity = float(balance.get("equity", 0))
    total_liab = float(balance.get("totalLiabilities", 0))
    revenue = float(income.get("revenue", 0))
    net_profit = float(income.get("netProfit", 0))
    operating_profit = float(income.get("operatingProfit", 0))

    current_ratio = safe_div(current_assets, current_liab)
    quick_ratio = safe_div(current_assets - inventory, current_liab)
    roa = safe_div(net_profit, total_assets) * 100
    roe = safe_div(net_profit, equity) * 100 if equity else 0.0
    ros = safe_div(operating_profit, revenue) * 100
    debt_to_equity = safe_div(total_liab, equity)
    asset_turnover = safe_div(revenue, total_assets)

    return {
        "currentRatio": round(current_ratio, 3),
        "quickRatio": round(quick_ratio, 3),
        "roa": round(roa, 2),
        "roe": round(roe, 2),
        "ros": round(ros, 2),
        "debtToEquity": round(debt_to_equity, 3),
        "assetTurnover": round(asset_turnover, 3),
    }


def build_summary(balance: dict, income: dict, ratios: dict) -> str:
    """Compose a short textual summary of the financial state."""
    parts: list[str] = []
    parts.append(
        f"Выручка составила {income.get('revenue', 0):,.0f}, чистая прибыль — "
        f"{income.get('netProfit', 0):,.0f}."
    )
    parts.append(
        f"Текущая ликвидность — {ratios.get('currentRatio', 0):.2f}, "
        f"быстрая — {ratios.get('quickRatio', 0):.2f}."
    )
    parts.append(
        f"Рентабельность: ROA {ratios.get('roa', 0):.1f}%, ROE {ratios.get('roe', 0):.1f}%, "
        f"ROS {ratios.get('ros', 0):.1f}%."
    )
    return " ".join(parts)

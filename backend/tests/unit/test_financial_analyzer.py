"""Unit tests for the financial analyzer (ratios + summary)."""
from app.processors.financial_analyzer import build_summary, compute_ratios


def test_compute_ratios_zero_division_safe():
    balance = {"currentAssets": 0, "currentLiabilities": 0, "totalAssets": 0, "equity": 0, "totalLiabilities": 0}
    income = {"revenue": 0, "netProfit": 0, "operatingProfit": 0}
    ratios = compute_ratios(balance, income)
    assert ratios["currentRatio"] == 0.0
    assert ratios["roa"] == 0.0


def test_compute_ratios_normal():
    balance = {
        "currentAssets": 300,
        "inventory": 100,
        "currentLiabilities": 200,
        "totalAssets": 1000,
        "equity": 400,
        "totalLiabilities": 600,
    }
    income = {"revenue": 2000, "netProfit": 200, "operatingProfit": 300}
    ratios = compute_ratios(balance, income)
    assert ratios["currentRatio"] == 1.5
    assert ratios["quickRatio"] == 1.0
    assert ratios["roa"] == 20.0
    assert ratios["ros"] == 15.0


def test_build_summary_contains_key_figures():
    balance = {"currentAssets": 0, "currentLiabilities": 0, "totalAssets": 0, "equity": 0, "totalLiabilities": 0}
    income = {"revenue": 1000, "netProfit": 100, "operatingProfit": 150}
    ratios = {"currentRatio": 1.5, "quickRatio": 1.0, "roa": 10, "roe": 20, "ros": 15}
    summary = build_summary(balance, income, ratios)
    assert "1,000" in summary
    assert "ROA" in summary

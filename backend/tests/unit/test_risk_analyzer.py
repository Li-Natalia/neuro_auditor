"""Unit tests for the risk analyzer."""
from app.processors.risk_analyzer import detect_risks


def test_critical_liquidity_detected():
    balance = {"currentAssets": 50, "currentLiabilities": 100, "equity": 100, "totalLiabilities": 100, "totalAssets": 200, "accountsReceivable": 10}
    income = {"revenue": 500, "netProfit": 50, "operatingProfit": 80}
    ratios = {"currentRatio": 0.5, "quickRatio": 0.4, "debtToEquity": 1.0, "roa": 25, "roe": 50, "ros": 16}
    risks = detect_risks(balance, income, ratios)
    titles = [r["title"] for r in risks]
    assert any("ликвидн" in t.lower() for t in titles)
    assert any(r["level"] == "critical" for r in risks)


def test_no_risks_when_healthy():
    balance = {"currentAssets": 300, "currentLiabilities": 150, "equity": 500, "totalLiabilities": 100, "totalAssets": 600, "accountsReceivable": 50}
    income = {"revenue": 1000, "netProfit": 150, "operatingProfit": 200}
    ratios = {"currentRatio": 2.0, "quickRatio": 1.5, "debtToEquity": 0.2, "roa": 25, "roe": 30, "ros": 20}
    risks = detect_risks(balance, income, ratios)
    # The healthy case yields a single low "no risks" entry
    assert all(r["level"] == "low" for r in risks)


def test_loss_detected():
    balance = {"currentAssets": 300, "currentLiabilities": 150, "equity": 500, "totalLiabilities": 100, "totalAssets": 600, "accountsReceivable": 50}
    income = {"revenue": 1000, "netProfit": -50, "operatingProfit": -20}
    ratios = {"currentRatio": 2.0, "quickRatio": 1.5, "debtToEquity": 0.2, "roa": -5, "roe": -6, "ros": -2}
    risks = detect_risks(balance, income, ratios)
    assert any("Убыток" in r["title"] for r in risks)

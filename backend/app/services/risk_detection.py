"""Risk-detection service: thin orchestration over the risk analyzer processors.

Provides higher-level helpers (risk score, heat map data) used by the dashboard
and reports.
"""
from __future__ import annotations

from typing import Any

from app.models.risk import RiskLevel
from app.processors.risk_analyzer import detect_risks

SCORE_BY_LEVEL = {
    RiskLevel.critical: 3,
    RiskLevel.medium: 2,
    RiskLevel.low: 1,
}


def _level_value(level: Any) -> str:
    if isinstance(level, str):
        return level
    return level.value


def compute_risk_score(risks: list[Any]) -> float:
    """Aggregate weighted risk score for a set of risks."""
    if not risks:
        return 0.0
    score = 0
    for r in risks:
        lvl = _level_value(r.level) if hasattr(r, "level") else r.get("level")
        score += {"critical": 3, "medium": 2, "low": 1}.get(lvl, 0)
    return float(score)


def risk_heatmap(analyses: list[Any]) -> dict[str, int]:
    """Return counts per risk level across analyses (for the dashboard heat map)."""
    counts = {"critical": 0, "medium": 0, "low": 0}
    for a in analyses:
        for r in (a.risks or []):
            lvl = _level_value(r.level)
            if lvl in counts:
                counts[lvl] += 1
    return counts


def detect(balance: dict, income: dict, ratios: dict) -> list[dict]:
    """Convenience wrapper around the processors risk analyzer."""
    return detect_risks(balance, income, ratios)

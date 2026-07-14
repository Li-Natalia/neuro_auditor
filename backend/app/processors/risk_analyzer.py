"""Risk detection rules over parsed financial data and ratios."""
from __future__ import annotations

from typing import Any


def _risk(level: str, title: str, description: str, recommendation: str, metric: str | None = None,
           value: float | None = None, threshold: float | None = None) -> dict:
    return {
        "level": level,
        "title": title,
        "description": description,
        "recommendation": recommendation,
        "metric": metric,
        "value": value,
        "threshold": threshold,
    }


def detect_risks(balance: dict[str, Any], income: dict[str, Any], ratios: dict[str, float]) -> list[dict]:
    risks: list[dict] = []

    current_ratio = ratios.get("currentRatio", 0)
    quick_ratio = ratios.get("quickRatio", 0)
    debt_to_equity = ratios.get("debtToEquity", 0)
    roa = ratios.get("roa", 0)
    roe = ratios.get("roe", 0)
    net_profit = float(income.get("netProfit", 0))

    current_liab = float(balance.get("currentLiabilities", 0) or 0)

    # Liquidity — the ratios are only meaningful when there ARE current
    # liabilities to cover. When there are, a ratio of 0 means zero current
    # assets (the worst case), so it must NOT be skipped by a falsy check.
    if current_liab > 0:
        if current_ratio < 1.0:
            risks.append(
                _risk(
                    "critical",
                    "Критическая ликвидность",
                    f"Текущая ликвидность {current_ratio:.2f} ниже 1.0 — оборотные активы не покрывают краткосрочные обязательства.",
                    "Срочно увеличьте оборотный капитал: ускорьте дебиторку, оптимизируйте запасы, реструктурируйте краткосрочный долг.",
                    "currentRatio", current_ratio, 1.0,
                )
            )
        elif current_ratio < 1.5:
            risks.append(
                _risk(
                    "medium",
                    "Сниженная ликвидность",
                    f"Текущая ликвидность {current_ratio:.2f} ниже рекомендуемой нормы 1.5.",
                    "Проконтролируйте структуру оборотных активов и краткосрочных обязательств.",
                    "currentRatio", current_ratio, 1.5,
                )
            )

        # Quick liquidity
        if quick_ratio < 0.8:
            risks.append(
                _risk(
                    "medium",
                    "Низкая быстрая ликвидность",
                    f"Быстрая ликвидность {quick_ratio:.2f} ниже 0.8 — зависимость от запасов для покрытия обязательств.",
                    "Сократите долю низколиквидных запасов в оборотных активах.",
                    "quickRatio", quick_ratio, 0.8,
                )
            )

    # Debt burden
    if debt_to_equity and debt_to_equity > 3.0:
        risks.append(
            _risk(
                "critical",
                "Высокая долговая нагрузка",
                f"Долг/капитал = {debt_to_equity:.2f}, что значительно превышает 1.0 — риск неплатёжеспособности.",
                "Разработайте план снижения долговой нагрузки, пересмотрите структуру финансирования.",
                "debtToEquity", debt_to_equity, 3.0,
            )
        )
    elif debt_to_equity and debt_to_equity > 1.0:
        risks.append(
            _risk(
                "medium",
                "Повышенная долговая нагрузка",
                f"Долг/капитал = {debt_to_equity:.2f} превышает норматив 1.0.",
                "Контролируйте привлечение новых займов и график погашения.",
                "debtToEquity", debt_to_equity, 1.0,
            )
        )

    # Profitability
    if net_profit < 0:
        risks.append(
            _risk(
                "critical",
                "Убыток",
                f"Чистый убыток составил {net_profit:,.0f}.",
                "Проведите анализ причин убыточности, пересмотрите структуру затрат и ценообразование.",
                "netProfit", net_profit, 0,
            )
        )

    if roa and roa < 0:
        risks.append(
            _risk(
                "medium",
                "Отрицательная рентабельность активов",
                f"ROA = {roa:.1f}% — активы генерируют убыток.",
                "Оптимизируйте использование активов и операционные расходы.",
                "roa", roa, 0,
            )
        )

    if equity := float(balance.get("equity", 0)):
        if equity < 0:
            risks.append(
                _risk(
                    "critical",
                    "Отрицательный собственный капитал",
                    "Собственный капитал отрицателен — признаки банкротства.",
                    "Необходима срочная финансовая реструктуризация и докапитализация.",
                    "equity", equity, 0,
                )
            )

    # Accounts receivable growth hint
    receivable = float(balance.get("accountsReceivable", 0) or 0)
    revenue = float(income.get("revenue", 0))
    if revenue and receivable / revenue > 0.4:
        risks.append(
            _risk(
                "low",
                "Высокая доля дебиторской задолженности",
                f"Дебиторка составляет {receivable / revenue * 100:.1f}% от выручки.",
                "Усильте контроль кредитной политики и работу по взысканию.",
                "receivableToRevenue", round(receivable / revenue, 2), 0.4,
            )
        )

    if not risks:
        risks.append(
            _risk(
                "low",
                "Существенных рисков не выявлено",
                "Ключевые показатели находятся в пределах норм.",
                "Продолжайте регулярный мониторинг показателей.",
            )
        )

    return risks

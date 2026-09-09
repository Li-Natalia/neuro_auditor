"""PDF report generation using reportlab."""
from __future__ import annotations

from io import BytesIO
from typing import Any, Callable
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from app.utils.pdf_fonts import register_cyrillic_fonts

RISK_COLORS = {
    "critical": colors.HexColor("#EF4444"),
    "medium": colors.HexColor("#F59E0B"),
    "low": colors.HexColor("#10B981"),
}

# Russian labels for the camelCase keys produced by the analyzers.
# Unknown keys are shown as-is.
BALANCE_LABELS = {
    "totalAssets": "Итого активов",
    "currentAssets": "Оборотные активы",
    "nonCurrentAssets": "Внеоборотные активы",
    "totalLiabilities": "Обязательства всего",
    "currentLiabilities": "Краткосрочные обязательства",
    "equity": "Собственный капитал",
    "inventory": "Запасы",
    "accountsReceivable": "Дебиторская задолженность",
    "cash": "Денежные средства",
}
INCOME_LABELS = {
    "revenue": "Выручка",
    "costOfSales": "Себестоимость",
    "grossProfit": "Валовая прибыль",
    "operatingExpenses": "Коммерческие и управленческие расходы",
    "operatingProfit": "Прибыль от продаж",
    "netProfit": "Чистая прибыль",
    "interestExpense": "Проценты к уплате",
}
RATIO_LABELS = {
    "currentRatio": "Текущая ликвидность",
    "quickRatio": "Быстрая ликвидность",
    "roa": "ROA, %",
    "roe": "ROE, %",
    "ros": "ROS, %",
    "debtToEquity": "Долг / капитал",
    "assetTurnover": "Оборачиваемость активов",
}
RISK_LEVEL_LABELS = {
    "critical": "Критический",
    "medium": "Средний",
    "low": "Низкий",
}


def _fmt_amount(value: Any) -> str:
    """Money amounts: no decimals, space as thousands separator (1 234 567)."""
    if value is None:
        return "—"
    if isinstance(value, (int, float)):
        return f"{value:,.0f}".replace(",", " ")
    return str(value)


def _fmt_ratio(value: Any) -> str:
    """Ratios: two decimals (roa/roe/ros are already percentages)."""
    if value is None:
        return "—"
    if isinstance(value, (int, float)):
        return f"{value:.2f}"
    return str(value)


def generate_analysis_pdf(analysis: Any) -> bytes:
    """Generate a PDF report for an Analysis object/dict."""
    regular, bold = register_cyrillic_fonts()

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title2", parent=styles["Title"], fontName=bold, textColor=colors.HexColor("#2563EB")
    )
    normal = ParagraphStyle("Body", parent=styles["Normal"], fontName=regular)
    cell = ParagraphStyle("Cell", parent=normal, fontSize=8, leading=10)

    elements: list = []
    elements.append(Paragraph("Нейроаудитор | Отчёт об анализе", title_style))
    elements.append(Spacer(1, 8 * mm))

    elements.append(Paragraph(f"<b>Документ:</b> #{getattr(analysis, 'document_id', '-')}", normal))
    elements.append(Spacer(1, 4 * mm))

    balance = getattr(analysis, "balance_sheet", None) or {}
    income = getattr(analysis, "income_statement", None) or {}
    ratios = getattr(analysis, "ratios", None) or {}
    summary = getattr(analysis, "summary", "") or ""

    elements.append(Paragraph("<b>Сводка</b>", normal))
    elements.append(Paragraph(escape(summary) or "—", normal))
    elements.append(Spacer(1, 4 * mm))

    def _table(
        title: str, data: dict[str, Any], labels: dict[str, str], fmt: Callable[[Any], str]
    ) -> None:
        elements.append(Paragraph(f"<b>{title}</b>", normal))
        rows = [["Показатель", "Значение"]]
        for key, value in data.items():
            rows.append([labels.get(key, key), fmt(value)])
        t = Table(rows, colWidths=[90 * mm, 60 * mm])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563EB")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), bold),
                    ("FONTNAME", (0, 1), (-1, -1), regular),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ]
            )
        )
        elements.append(t)
        elements.append(Spacer(1, 4 * mm))

    _table("Баланс", balance, BALANCE_LABELS, _fmt_amount)
    _table("ОПУ", income, INCOME_LABELS, _fmt_amount)
    _table("Коэффициенты", ratios, RATIO_LABELS, _fmt_ratio)

    risks = getattr(analysis, "risks", []) or []
    if risks:
        elements.append(Paragraph("<b>Риски</b>", normal))
        rows: list[list[Any]] = [["Уровень", "Название", "Рекомендация"]]
        style = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7C3AED")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), bold),
            ("FONTNAME", (0, 1), (-1, -1), regular),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]
        for row_idx, r in enumerate(risks, start=1):
            level = getattr(r, "level", "low")
            level = level.value if hasattr(level, "value") else str(level)
            rows.append(
                [
                    RISK_LEVEL_LABELS.get(level, level),
                    # Paragraphs wrap long text inside the cell (plain strings don't).
                    Paragraph(escape(str(getattr(r, "title", "") or "")), cell),
                    Paragraph(escape(str(getattr(r, "recommendation", "") or "")), cell),
                ]
            )
            if level in RISK_COLORS:
                style.append(("BACKGROUND", (0, row_idx), (0, row_idx), RISK_COLORS[level]))
                style.append(("TEXTCOLOR", (0, row_idx), (0, row_idx), colors.white))
        t = Table(rows, colWidths=[25 * mm, 45 * mm, 100 * mm])
        t.setStyle(TableStyle(style))
        elements.append(t)

    doc.build(elements)
    return buffer.getvalue()

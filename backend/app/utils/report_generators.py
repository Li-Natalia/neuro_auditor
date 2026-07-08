"""PDF report generation using reportlab."""
from __future__ import annotations

from io import BytesIO
from typing import Any

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

from app.core.config import settings

RISK_COLORS = {
    "critical": colors.HexColor("#EF4444"),
    "medium": colors.HexColor("#F59E0B"),
    "low": colors.HexColor("#10B981"),
}


def generate_analysis_pdf(analysis: Any) -> bytes:
    """Generate a PDF report for an Analysis object/dict."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, margins=15 * mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title2", parent=styles["Title"], textColor=colors.HexColor("#2563EB"))
    normal = styles["Normal"]

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
    elements.append(Paragraph(summary or "—", normal))
    elements.append(Spacer(1, 4 * mm))

    def _table(title: str, data: dict[str, Any]):
        elements.append(Paragraph(f"<b>{title}</b>", normal))
        rows = [["Показатель", "Значение"]]
        for k, v in data.items():
            rows.append([k, f"{v:,.2f}" if isinstance(v, (int, float)) else str(v)])
        t = Table(rows, colWidths=[90 * mm, 60 * mm])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563EB")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ]
            )
        )
        elements.append(t)
        elements.append(Spacer(1, 4 * mm))

    _table("Баланс", balance)
    _table("ОПУ", income)
    _table("Коэффициенты", ratios)

    risks = getattr(analysis, "risks", []) or []
    if risks:
        elements.append(Paragraph("<b>Риски</b>", normal))
        rows = [["Уровень", "Название", "Рекомендация"]]
        for r in risks:
            level = getattr(r, "level", "low")
            level = level.value if hasattr(level, "value") else str(level)
            rows.append([level, getattr(r, "title", ""), getattr(r, "recommendation", "")])
        t = Table(rows, colWidths=[25 * mm, 45 * mm, 100 * mm])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7C3AED")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        elements.append(t)

    doc.build(elements)
    return buffer.getvalue()

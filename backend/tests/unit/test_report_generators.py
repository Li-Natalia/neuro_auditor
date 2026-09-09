"""Unit tests for PDF report generation (Cyrillic-capable fonts, labels, formatting)."""
from datetime import datetime
from types import SimpleNamespace

import pytest
from reportlab.pdfbase import pdfmetrics

from app.utils import pdf_fonts
from app.utils.pdf_fonts import register_cyrillic_fonts
from app.utils.report_generators import _fmt_amount, _fmt_ratio, generate_analysis_pdf


def _analysis(**overrides):
    base = dict(
        document_id=1,
        created_at=datetime.now(),
        summary="Выручка составила 320 000 000, чистая прибыль — 12 000 000.",
        balance_sheet={"totalAssets": 250_000_000, "currentAssets": 100_000_000},
        income_statement={"revenue": 320_000_000, "netProfit": 12_000_000},
        ratios={"currentRatio": 1.25, "roa": 4.8},
        risks=[
            SimpleNamespace(
                level="medium",
                title="Сниженная ликвидность",
                recommendation=(
                    "Проконтролируйте структуру оборотных активов и краткосрочных обязательств."
                ),
            )
        ],
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def test_generate_analysis_pdf_embeds_cyrillic_font():
    pdf = generate_analysis_pdf(_analysis())

    assert pdf[:4] == b"%PDF"
    assert "DejaVuSans" in pdfmetrics.getRegisteredFontNames()
    # reportlab embeds the TrueType subset under its face name (/XXXXXX+DejaVuSans).
    assert b"DejaVuSans" in pdf


def test_generate_analysis_pdf_survives_empty_sections_and_markup_chars():
    a = _analysis(
        summary="",
        balance_sheet={},
        income_statement={"unknownKey": None},
        ratios={},
        risks=[SimpleNamespace(level="critical", title="Долг & капитал <3", recommendation="")],
    )

    pdf = generate_analysis_pdf(a)

    assert pdf[:4] == b"%PDF"


def test_register_cyrillic_fonts_falls_back_to_helvetica(monkeypatch):
    monkeypatch.setattr(pdf_fonts, "_FONT_DIRS", [])
    register_cyrillic_fonts.cache_clear()
    try:
        assert register_cyrillic_fonts() == ("Helvetica", "Helvetica-Bold")
    finally:
        # Don't leak the cached fallback into other tests.
        register_cyrillic_fonts.cache_clear()


@pytest.mark.parametrize(
    "value, expected",
    [
        (320_000_000, "320 000 000"),
        (1234.56, "1 235"),
        (-1500, "-1 500"),
        (None, "—"),
        ("n/a", "n/a"),
    ],
)
def test_fmt_amount(value, expected):
    assert _fmt_amount(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [(1.256, "1.26"), (4.8, "4.80"), (2, "2.00"), (None, "—")],
)
def test_fmt_ratio(value, expected):
    assert _fmt_ratio(value) == expected

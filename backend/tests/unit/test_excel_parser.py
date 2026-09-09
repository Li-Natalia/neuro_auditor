"""Unit tests for the Excel statement parser.

Covers collision-proof label matching, deterministic reporting-period choice,
balance reconciliation and the engine selection for legacy ``.xls`` files.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import openpyxl
import pandas as pd
import pytest

from app.processors.excel_parser import (
    BALANCE_ITEMS,
    HeaderInfo,
    _detect_header,
    _engine_for,
    _period_key,
    _reconcile_balance,
    parse_workbook,
)
from app.processors.financial_analyzer import compute_ratios

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"

# Figures of the "На конец" column in sample_rsbu.xlsx / .xls
EXPECTED_RSBU_BALANCE = {
    "totalAssets": 1_500_000,
    "currentAssets": 300_000,
    "nonCurrentAssets": 1_200_000,
    "totalLiabilities": 900_000,
    "currentLiabilities": 800_000,
    "equity": 600_000,
    "inventory": 100_000,
    "accountsReceivable": 280_000,
    "cash": 20_000,
}


def _write_workbook(path: Path, sheets: dict[str, list[list]]) -> Path:
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for title, rows in sheets.items():
        ws = wb.create_sheet(title)
        for row in rows:
            ws.append(row)
    wb.save(path)
    return path


# ---------------------------------------------------------------------------
# Fixture workbooks
# ---------------------------------------------------------------------------
def test_parse_sample_rsbu_xlsx():
    parsed = parse_workbook(str(FIXTURES / "sample_rsbu.xlsx"))

    assert parsed["balance"] == EXPECTED_RSBU_BALANCE
    assert parsed["income"]["revenue"] == 2_000_000
    assert parsed["income"]["netProfit"] == 50_000
    assert parsed["cashflow"]["operatingCashFlow"] == 100_000
    assert parsed["cashflow"]["investingCashFlow"] == -200_000
    assert parsed["cashflow"]["financingCashFlow"] == 50_000
    assert parsed["cashflow"]["netCashFlow"] == -50_000
    assert parsed["meta"]["period"] == "На конец"
    assert parsed["meta"]["warnings"] == []


def test_parse_sample_report_large_uses_latest_period():
    parsed = parse_workbook(str(FIXTURES / "sample_report_large.xlsx"))
    balance, income, cashflow = parsed["balance"], parsed["income"], parsed["cashflow"]

    assert balance["currentAssets"] == 100_000_000
    assert balance["nonCurrentAssets"] == 150_000_000
    assert balance["totalAssets"] == 250_000_000
    assert balance["totalLiabilities"] == 130_000_000
    assert balance["equity"] == 120_000_000
    assert balance["currentLiabilities"] == 80_000_000
    assert income["revenue"] == 320_000_000
    assert income["netProfit"] == 12_000_000
    assert cashflow["operatingCashFlow"] == 30_000_000
    assert cashflow["investingCashFlow"] == -22_000_000
    assert parsed["meta"]["period"] == "на 31.12.2025"
    assert parsed["meta"]["warnings"] == []

    ratios = compute_ratios(balance, income)
    assert ratios["currentRatio"] == 1.25
    assert ratios["debtToEquity"] == pytest.approx(1.083, abs=1e-3)


def test_parse_sample_rsbu_xls_matches_xlsx():
    pytest.importorskip("xlrd")
    parsed = parse_workbook(str(FIXTURES / "sample_rsbu.xls"))

    assert parsed["balance"] == EXPECTED_RSBU_BALANCE
    assert parsed["income"]["revenue"] == 2_000_000
    assert parsed["income"]["netProfit"] == 50_000
    assert parsed["cashflow"]["netCashFlow"] == -50_000
    assert parsed["meta"]["period"] == "На конец"


# ---------------------------------------------------------------------------
# Reporting period selection
# ---------------------------------------------------------------------------
_PERIOD_ROWS = [
    ["Внеоборотные активы", 700, 400],
    ["Оборотные активы", 300, 500],
    ["Итого актив", 1000, 900],
    ["Капитал", 600, 500],
    ["Обязательства всего", 400, 400],
]


def test_latest_period_column_wins_even_when_it_is_first(tmp_path):
    header = ["Показатель", "на 31.12.2025", "на 31.12.2024"]
    path = _write_workbook(tmp_path / "latest_first.xlsx", {"Баланс": [header, *_PERIOD_ROWS]})

    parsed = parse_workbook(str(path))

    assert parsed["balance"]["currentAssets"] == 300  # column 1, not the right-most
    assert parsed["balance"]["nonCurrentAssets"] == 700
    assert parsed["balance"]["totalAssets"] == 1000
    assert parsed["meta"]["period"] == "на 31.12.2025"


def test_latest_period_column_wins_when_it_is_last(tmp_path):
    header = ["Показатель", "на 31.12.2024", "на 31.12.2025"]
    rows = [[label, older, latest] for label, latest, older in _PERIOD_ROWS]
    path = _write_workbook(tmp_path / "latest_last.xlsx", {"Баланс": [header, *rows]})

    parsed = parse_workbook(str(path))

    assert parsed["balance"]["currentAssets"] == 300
    assert parsed["balance"]["nonCurrentAssets"] == 700
    assert parsed["meta"]["period"] == "на 31.12.2025"


def test_zero_in_latest_period_is_kept_and_blank_falls_back(tmp_path):
    rows = [
        ["Показатель", "на 31.12.2025", "на 31.12.2024"],
        ["Запасы", 0, 500],
        ["Денежные средства", None, 250],
    ]
    path = _write_workbook(tmp_path / "zero.xlsx", {"Баланс": rows})

    balance = parse_workbook(str(path))["balance"]

    assert balance["inventory"] == 0.0  # a legitimate zero is not skipped
    assert balance["cash"] == 250  # blank cell -> right-most numeric cell


def test_headerless_sheet_uses_rightmost_numeric_column(tmp_path):
    rows = [["Запасы", 5, 7], ["Итого актив", 100, 120]]
    path = _write_workbook(tmp_path / "noheader.xlsx", {"Баланс": rows})

    parsed = parse_workbook(str(path))

    assert parsed["balance"]["inventory"] == 7
    assert parsed["balance"]["totalAssets"] == 120
    assert parsed["meta"]["period"] is None


@pytest.mark.parametrize(
    "cell, expected",
    [
        (dt.datetime(2025, 12, 31), (2025, 12, 31)),
        (pd.Timestamp("2024-06-30"), (2024, 6, 30)),
        (2025, (2025, 12, 31)),
        (2025.0, (2025, 12, 31)),
        ("на 31.12.2025", (2025, 12, 31)),
        ("2025", (2025, 12, 31)),
        ("За 2024 год", (2024, 12, 31)),
        ("На конец", None),
        ("12025", None),  # not a bare year
        (1_500_000, None),
        (None, None),
        (float("nan"), None),
    ],
)
def test_period_key(cell, expected):
    assert _period_key(cell) == expected


def test_detect_header_skips_title_row_and_picks_latest_period():
    df = pd.DataFrame(
        [
            ["Бухгалтерский баланс, тыс. руб.", None, None, None],
            ["Показатель", "на 31.12.2023", "на 31.12.2025", "на 31.12.2024"],
            ["Запасы", 1, 2, 3],
        ]
    )
    assert _detect_header(df) == HeaderInfo(
        row_index=1, value_col=2, period_label="на 31.12.2025", period_cols=(1, 2, 3)
    )


def test_detect_header_without_period_keys_uses_rightmost_column():
    df = pd.DataFrame([["Статья", "На начало", "На конец"], ["Запасы", 1, 2]])
    assert _detect_header(df) == HeaderInfo(row_index=0, value_col=2, period_label="На конец")


def test_detect_header_returns_none_without_header_row():
    df = pd.DataFrame([["Запасы", 1, 2], ["Итого актив", 3, 4]])
    assert _detect_header(df) is None


# ---------------------------------------------------------------------------
# Label matching (collision regressions)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "key, label",
    [
        ("currentAssets", "Внеоборотные активы"),
        ("currentAssets", "Итого внеоборотных активов"),
        ("currentAssets", "Итого по разделу III"),
        ("nonCurrentAssets", "Итого по разделу III"),
        ("equity", "Уставный капитал"),
        ("equity", "Добавочный капитал"),
        ("equity", "Итого капитал и обязательства"),
        ("totalLiabilities", "Итого пассив"),
        ("totalLiabilities", "Итого капитал и обязательства"),
        ("totalAssets", "Итого капитал и обязательства"),
        ("currentLiabilities", "Прочие краткосрочные обязательства"),
        ("currentLiabilities", "Заёмные средства (краткосрочные)"),
        ("cash", "Чистое изменение денежных средств"),
    ],
)
def test_label_must_not_match(key, label):
    assert BALANCE_ITEMS[key].match_rank(label) is None


@pytest.mark.parametrize(
    "key, label, rank",
    [
        ("currentAssets", "Оборотные активы", 1),
        ("currentAssets", "  ИТОГО   оборотные активы", 0),
        ("currentAssets", "Итого по разделу II", 2),
        ("nonCurrentAssets", "Внеоборотные активы", 1),
        ("nonCurrentAssets", "Итого внеоборотных активов", 0),
        ("totalAssets", "Итого активов", 0),
        ("totalAssets", "БАЛАНС", 4),
        ("totalLiabilities", "Обязательства всего", 0),
        ("currentLiabilities", "Краткосрочные обязательства", 0),
        ("equity", "Капитал", 6),
        ("equity", "Капитал и резервы", 1),
        ("equity", "Итого по разделу III", 2),
        ("equity", "Собственный капитал", 3),
        ("cash", "Денежные средства и денежные эквиваленты", 0),
    ],
)
def test_label_matches_with_rank(key, label, rank):
    assert BALANCE_ITEMS[key].match_rank(label) == rank


def test_yo_is_folded_before_matching():
    # "Заёмные" must hit the "заемн" exclusion once ё is normalised to е.
    assert BALANCE_ITEMS["equity"].match_rank("Заёмный капитал") is None


# ---------------------------------------------------------------------------
# Balance reconciliation
# ---------------------------------------------------------------------------
def test_reconcile_balance_fixes_current_assets_when_totals_disagree():
    balance = {
        "totalAssets": 1_500_000.0,
        "currentAssets": 1_200_000.0,  # the old collision result
        "nonCurrentAssets": 1_200_000.0,
        "equity": 600_000.0,
        "totalLiabilities": 900_000.0,
    }
    warnings = _reconcile_balance(balance)

    assert balance["currentAssets"] == 300_000.0
    assert balance["nonCurrentAssets"] == 1_200_000.0
    assert balance["totalLiabilities"] == 900_000.0
    assert len(warnings) == 1


def test_reconcile_balance_replaces_liabilities_equal_to_balance_total():
    balance = {
        "totalAssets": 1_500.0,
        "currentAssets": 300.0,
        "nonCurrentAssets": 1_200.0,
        "equity": 600.0,
        "totalLiabilities": 1_500.0,  # "Итого пассив" mistaken for liabilities
    }
    warnings = _reconcile_balance(balance)

    assert balance["totalLiabilities"] == 900.0
    assert len(warnings) == 1


def test_reconcile_balance_leaves_consistent_figures_alone():
    balance = {
        "totalAssets": 1_500.0,
        "currentAssets": 300.0,
        "nonCurrentAssets": 1_200.0,
        "equity": 600.0,
        "totalLiabilities": 900.0,
    }
    assert _reconcile_balance(balance) == []
    assert balance["currentAssets"] == 300.0
    assert balance["totalLiabilities"] == 900.0


def test_reconcile_balance_derives_missing_totals():
    balance = {
        "totalAssets": 0.0,
        "currentAssets": 300.0,
        "nonCurrentAssets": 1_200.0,
        "equity": 600.0,
        "totalLiabilities": 0.0,
    }
    _reconcile_balance(balance)

    assert balance["totalAssets"] == 1_500.0
    assert balance["totalLiabilities"] == 900.0


# ---------------------------------------------------------------------------
# Engine selection
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "name, engine",
    [
        ("report.xls", "xlrd"),
        ("REPORT.XLS", "xlrd"),
        ("report.xlsx", "openpyxl"),
        ("report.xlsm", "openpyxl"),
    ],
)
def test_engine_for(name, engine):
    assert _engine_for(name) == engine
    assert _engine_for(Path("/uploads") / name) == engine

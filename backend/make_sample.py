"""Generate the sample RSBU-style Excel fixtures used by the parser tests.

Writes ``tests/fixtures/sample_rsbu.xlsx`` (via openpyxl) and, when ``xlwt``
is installed, the same three sheets as the legacy ``tests/fixtures/sample_rsbu.xls``
so the ``xlrd`` engine path is covered too. Existing files are left untouched
unless ``--force`` is given (the tests pin the exact figures below).

Usage (from ``backend/``):  python make_sample.py [--force]
"""
from __future__ import annotations

import sys
from pathlib import Path

import openpyxl

FIXTURES_DIR = Path(__file__).resolve().parent / "tests" / "fixtures"

# Sheet 1: Balance. Note the deliberate ordering: "Внеоборотные активы" comes
# before "Оборотные активы" and "Итого пассив" after "Обязательства всего" —
# the parser tests guard against substring collisions on these rows.
BALANCE_ROWS = [
    ["Статья", "На начало", "На конец"],
    ["Внеоборотные активы", 1000000, 1200000],
    ["Оборотные активы", 500000, 300000],
    ["Запасы", 100000, 100000],
    ["Дебиторская задолженность", 300000, 280000],
    ["Денежные средства", 100000, 20000],
    ["Итого актив", 1500000, 1500000],
    ["Капитал", 700000, 600000],
    ["Краткосрочные обязательства", 600000, 800000],
    ["Обязательства всего", 800000, 900000],
    ["Итого пассив", 1500000, 1500000],
]

# Sheet 2: Income statement
INCOME_ROWS = [
    ["Статья", "За период"],
    ["Выручка", 2000000],
    ["Себестоимость", 1500000],
    ["Валовая прибыль", 500000],
    ["Операционные расходы", 300000],
    ["Прибыль от продаж", 200000],
    ["Чистая прибыль", 50000],
]

# Sheet 3: Cash flow
CASHFLOW_ROWS = [
    ["Статья", "Сумма"],
    ["Операционная деятельность", 100000],
    ["Инвестиционная деятельность", -200000],
    ["Финансовая деятельность", 50000],
    ["Чистый денежный поток", -50000],
]

SHEETS = [("Баланс", BALANCE_ROWS), ("ОПУ", INCOME_ROWS), ("ОДДС", CASHFLOW_ROWS)]


def write_xlsx(path: Path) -> None:
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for title, rows in SHEETS:
        ws = wb.create_sheet(title)
        for row in rows:
            ws.append(row)
    wb.save(path)


def write_xls(path: Path) -> bool:
    """Write the legacy ``.xls`` twin via xlwt; returns False when xlwt is missing."""
    try:
        import xlwt
    except ImportError:
        return False
    wb = xlwt.Workbook()
    for title, rows in SHEETS:
        ws = wb.add_sheet(title)
        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                ws.write(r, c, value)
    wb.save(str(path))
    return True


def main(argv: list[str]) -> int:
    force = "--force" in argv
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    xlsx = FIXTURES_DIR / "sample_rsbu.xlsx"
    if xlsx.exists() and not force:
        print(f"{xlsx.name}: already exists, skipped (use --force to regenerate)")
    else:
        write_xlsx(xlsx)
        print(f"{xlsx.name} created")

    xls = FIXTURES_DIR / "sample_rsbu.xls"
    if xls.exists() and not force:
        print(f"{xls.name}: already exists, skipped (use --force to regenerate)")
    elif write_xls(xls):
        print(f"{xls.name} created")
    else:
        print(f"{xls.name}: skipped — xlwt is not installed (pip install xlwt==1.3.0)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

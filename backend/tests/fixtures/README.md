# Test fixtures

Sample workbooks exercised by `tests/unit/test_excel_parser.py`.

| File | Origin | What it covers |
|------|--------|----------------|
| `sample_rsbu.xlsx` | `python make_sample.py` (run from `backend/`) | Minimal RSBU-style workbook with three sheets (`Баланс`, `ОПУ`, `ОДДС`) and text-only headers without dates (`На начало` / `На конец`) |
| `sample_rsbu.xls` | `python make_sample.py` (needs `xlwt`, see `requirements-dev.txt`) | The same three sheets in the legacy BIFF format — exercises the `xlrd` engine path and asserts parity with the `.xlsx` |
| `sample_report_large.xlsx` | Copy of `example/sample_report_large.xlsx` (kept here because the Docker build context is `./backend` only) | Realistic multi-period statements: a title row above the header, three dated columns (`на 31.12.2023` … `на 31.12.2025`, year-only headers on the other sheets) and sub-items such as `Уставный капитал`, `Прочие краткосрочные обязательства`, `Итого капитал и обязательства` |

## Regression: label collisions

`sample_rsbu.xlsx` deliberately lists `Внеоборотные активы` (1 200 000) *before*
`Оборотные активы` (300 000) and ends with `Итого пассив` (1 500 000) right after
`Обязательства всего` (900 000). The old substring matcher took the first row that
merely *contained* the keyword, so `currentAssets` was read from the
`Внеоборотные активы` row and `totalLiabilities` from `Итого пассив`. The tests pin
the correct figures (300 000 / 900 000) — keep the row order when regenerating.

`sample_report_large.xlsx` additionally guards the reporting-period choice: the
latest column (`на 31.12.2025`) must be used even though older figures are also
non-zero, and `Итого капитал и обязательства` must not be mistaken for equity or
total assets.

Do not edit the fixtures by hand: regenerate with `python make_sample.py --force`
and update the expectations in the tests if the data changes.

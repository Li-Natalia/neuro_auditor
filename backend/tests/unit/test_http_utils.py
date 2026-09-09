from urllib.parse import quote

from app.utils.http import content_disposition


def test_ascii_name_is_sanitised_and_encoded():
    assert content_disposition("report 2025.csv") == (
        "attachment; filename=\"report_2025.csv\"; filename*=UTF-8''report%202025.csv"
    )


def test_cyrillic_name_keeps_extension_in_ascii_fallback():
    name = "основные_показатели_баланса.csv"
    header = content_disposition(name)
    assert header.startswith('attachment; filename="file.csv"; ')
    assert header.endswith("filename*=UTF-8''" + quote(name, safe=""))


def test_paths_and_line_breaks_are_stripped():
    header = content_disposition("../evil\r\nX-Injected: 1.txt")
    assert "\n" not in header and "\r" not in header and "../" not in header
    assert 'filename="evilX-Injected_1.txt"' in header


def test_empty_name_falls_back_to_file():
    assert content_disposition("").startswith('attachment; filename="file"; ')

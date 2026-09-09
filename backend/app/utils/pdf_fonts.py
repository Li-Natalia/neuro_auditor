"""Cyrillic-capable TrueType fonts for reportlab.

reportlab's built-in Type 1 fonts (Helvetica & co.) only cover Latin-1, so any
Cyrillic text drawn with them renders as black squares. We register DejaVu Sans
(vendored in ``app/assets/fonts``; see ``LICENSE-DejaVu.txt`` there) once per
process and use it for every text style in generated PDFs.
"""
from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)

REGULAR_FONT = "DejaVuSans"
BOLD_FONT = "DejaVuSans-Bold"
FALLBACK_FONTS = ("Helvetica", "Helvetica-Bold")

_REGULAR_FILE = "DejaVuSans.ttf"
_BOLD_FILE = "DejaVuSans-Bold.ttf"


def _default_font_dirs() -> list[Path]:
    dirs = [
        # Vendored copy — the one expected to be used in Docker and locally.
        Path(__file__).resolve().parents[1] / "assets" / "fonts",
        # Debian/Ubuntu (fonts-dejavu-core), Fedora/Alpine (dejavu-fonts / font-dejavu).
        Path("/usr/share/fonts/truetype/dejavu"),
        Path("/usr/share/fonts/dejavu"),
        # macOS system + user fonts.
        Path("/Library/Fonts"),
    ]
    try:
        dirs.append(Path.home() / "Library" / "Fonts")
    except RuntimeError:  # home directory cannot be resolved (bare containers)
        pass
    dirs.append(Path("C:/Windows/Fonts"))
    return dirs


# Searched in order; module-level so tests can monkeypatch it.
_FONT_DIRS: list[Path] = _default_font_dirs()


def _find_font_dir() -> Path | None:
    """Return the first directory containing both DejaVu Sans files, if any."""
    for directory in _FONT_DIRS:
        if (directory / _REGULAR_FILE).is_file() and (directory / _BOLD_FILE).is_file():
            return directory
    return None


@lru_cache(maxsize=1)
def register_cyrillic_fonts() -> tuple[str, str]:
    """Register DejaVu Sans (regular + bold) with reportlab.

    Returns ``(regular, bold)`` font names to use in paragraph/table styles.
    Falls back to Helvetica (Latin-1 only — Cyrillic renders as boxes) with a
    warning when the font files cannot be found. Cached because registration
    is process-wide and only needs to happen once.
    """
    font_dir = _find_font_dir()
    if font_dir is None:
        logger.warning(
            "DejaVu Sans not found (searched: %s); falling back to %s — Cyrillic text "
            "in PDF reports will render as boxes",
            ", ".join(str(d) for d in _FONT_DIRS),
            FALLBACK_FONTS[0],
        )
        return FALLBACK_FONTS

    pdfmetrics.registerFont(TTFont(REGULAR_FONT, str(font_dir / _REGULAR_FILE)))
    pdfmetrics.registerFont(TTFont(BOLD_FONT, str(font_dir / _BOLD_FILE)))
    # Makes <b>…</b> inside Paragraph markup switch to the bold face
    # (without a family mapping reportlab would fall back to Helvetica-Bold).
    pdfmetrics.registerFontFamily(
        REGULAR_FONT,
        normal=REGULAR_FONT,
        bold=BOLD_FONT,
        italic=REGULAR_FONT,
        boldItalic=BOLD_FONT,
    )
    logger.info("Registered PDF fonts %s / %s from %s", REGULAR_FONT, BOLD_FONT, font_dir)
    return REGULAR_FONT, BOLD_FONT

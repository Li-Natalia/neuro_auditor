"""Small HTTP helpers."""
from __future__ import annotations

import os
import re
from urllib.parse import quote

_ASCII_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")


def content_disposition(filename: str, disposition: str = "attachment") -> str:
    """Build a Content-Disposition header that keeps non-ASCII file names (RFC 6266/5987).

    Old clients read the ASCII ``filename=`` fallback, modern ones ``filename*=UTF-8''``.
    Path components and line breaks are stripped so a name coming from an external
    service cannot inject headers or paths.
    """
    name = os.path.basename((filename or "").replace("\r", "").replace("\n", "")).strip()
    name = name or "file"
    stem, ext = os.path.splitext(name)
    ascii_stem = _ASCII_UNSAFE.sub("_", stem).strip("_") or "file"
    ascii_name = ascii_stem + _ASCII_UNSAFE.sub("", ext)
    return f"{disposition}; filename=\"{ascii_name}\"; filename*=UTF-8''{quote(name, safe='')}"

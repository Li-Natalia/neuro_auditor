"""Vector embeddings for document context (optional).

Uses sentence-transformers if available, otherwise a lightweight hash-based
fallback so the rest of the app keeps working without heavy ML deps.
"""
from __future__ import annotations

import hashlib
import math
from typing import Any

_MODEL = None
_USE_MODEL = False

try:  # optional heavy dependency
    from sentence_transformers import SentenceTransformer  # type: ignore

    _USE_MODEL = True
except Exception:  # pragma: no cover
    pass


def _get_model():
    global _MODEL
    if _USE_MODEL and _MODEL is None:
        try:
            _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            pass
    return _MODEL


def embed(text: str, dim: int = 128) -> list[float]:
    """Return an embedding vector for a text chunk."""
    model = _get_model()
    if model is not None:
        return model.encode(text).tolist()
    # Deterministic hash-based fallback (not semantic, but keeps API working)
    h = hashlib.sha512(text.encode("utf-8")).digest()
    vec = [(b - 128) / 128.0 for b in (h * (dim // 64 + 1))[:dim]]
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0

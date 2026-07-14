"""Simple in-memory rate limiting middleware (per-IP).

For production use Redis-backed limits (e.g. slowapi). This provides a basic
guard that keeps the app self-contained without extra dependencies.
"""
import time
from collections import defaultdict, deque

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

WINDOW_SECONDS = 60
MAX_REQUESTS = 120

_requests: dict[str, deque[float]] = defaultdict(deque)
_last_cleanup: float = 0.0


def _client_ip(request: Request) -> str:
    """Resolve the client IP, honouring X-Forwarded-For behind a proxy.

    The first entry in X-Forwarded-For is the original client, so clients
    behind a shared proxy are not all bucketed under the proxy's address.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _prune(now: float) -> None:
    """Drop timestamps older than the window and remove drained buckets.

    Without this the module-global ``_requests`` grows unbounded as new
    client keys are added and never released.
    """
    cutoff = now - WINDOW_SECONDS
    for key in list(_requests.keys()):
        bucket = _requests[key]
        while bucket and bucket[0] < cutoff:
            bucket.popleft()
        if not bucket:
            del _requests[key]


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client = _client_ip(request)
        now = time.monotonic()

        global _last_cleanup
        if now - _last_cleanup >= WINDOW_SECONDS:
            _prune(now)
            _last_cleanup = now

        bucket = _requests[client]
        while bucket and bucket[0] < now - WINDOW_SECONDS:
            bucket.popleft()
        if len(bucket) >= MAX_REQUESTS:
            return JSONResponse(
                status_code=429,
                content={"detail": "Слишком много запросов. Попробуйте позже."},
            )
        bucket.append(now)
        return await call_next(request)

# backend/rate_limit.py
"""
From-scratch sliding-window-log rate limiter.

GLOBAL bucket: every request against a given scope shares ONE counter,
regardless of client. One caller hitting the limit throttles everyone.

Single-process only. Do NOT run uvicorn with --workers > 1.
"""
import asyncio
import os
import time
from collections import deque
from dataclasses import dataclass

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware


@dataclass
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    reset_at: float
    retry_after: float


class MemoryStore:
    """Per-process store. One deque per scope (not per client)."""

    def __init__(self) -> None:
        self._data: dict[str, deque[float]] = {}
        self._lock = asyncio.Lock()

    async def check(self, key: str, limit: int, window: float) -> RateLimitResult:
        now = time.time()
        cutoff = now - window
        async with self._lock:
            dq = self._data.setdefault(key, deque())
            while dq and dq[0] <= cutoff:
                dq.popleft()
            if len(dq) < limit:
                dq.append(now)
                return RateLimitResult(
                    allowed=True,
                    limit=limit,
                    remaining=limit - len(dq),
                    reset_at=dq[0] + window,
                    retry_after=0.0,
                )
            oldest = dq[0]
            return RateLimitResult(
                allowed=False,
                limit=limit,
                remaining=0,
                reset_at=oldest + window,
                retry_after=oldest + window - now,
            )


_store: MemoryStore | None = None


def get_store() -> MemoryStore:
    global _store
    if _store is None:
        _store = MemoryStore()
    return _store


def rate_limit(limit: int, window: float, scope: str = "default"):
    """FastAPI dependency: allow `limit` requests per `window` seconds,
    GLOBALLY across all clients, tracked per `scope`."""
    async def _dep(request: Request) -> None:
        if os.getenv("RATE_LIMIT_DISABLED") == "1":
            return
        key = f"rl:{scope}:__global__"
        result = await get_store().check(key, limit, window)
        request.state.rate_limit = result
        if not result.allowed:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={
                    "Retry-After": str(int(result.retry_after) + 1),
                    "X-RateLimit-Limit": str(result.limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(result.reset_at)),
                },
            )

    return _dep


class RateLimitHeadersMiddleware(BaseHTTPMiddleware):
    """Adds X-RateLimit-* headers to successful responses too."""

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        rl = getattr(request.state, "rate_limit", None)
        if rl is not None:
            response.headers["X-RateLimit-Limit"] = str(rl.limit)
            response.headers["X-RateLimit-Remaining"] = str(rl.remaining)
            response.headers["X-RateLimit-Reset"] = str(int(rl.reset_at))
        return response
import time
import logging
from collections import defaultdict, deque
from threading import Lock
from typing import Optional, Tuple
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger("lumiq.rate_limiter")

class SlidingWindowRateLimiter:
    """
    Thread-safe, in-memory sliding-window rate limiter.
    Maintains timestamp deques per client key and endpoint group.
    """
    def __init__(self, window_seconds: int = 60):
        self.window_seconds = window_seconds
        self._lock = Lock()
        self._clients = defaultdict(lambda: defaultdict(deque))
        self._last_cleanup = time.time()

    def _cleanup_old_entries(self, now: float):
        # Run cleanup at most once every 60 seconds
        if now - self._last_cleanup < 60.0:
            return
        self._last_cleanup = now
        stale_threshold = now - self.window_seconds
        keys_to_remove = []

        for client_key, buckets in self._clients.items():
            bucket_keys_to_remove = []
            for bucket_name, timestamps in buckets.items():
                while timestamps and timestamps[0] < stale_threshold:
                    timestamps.popleft()
                if not timestamps:
                    bucket_keys_to_remove.append(bucket_name)
            for b in bucket_keys_to_remove:
                del buckets[b]
            if not buckets:
                keys_to_remove.append(client_key)

        for k in keys_to_remove:
            del self._clients[k]

    def acquire(self, client_key: str, bucket_name: str, max_limit: int) -> Tuple[bool, int, int]:
        """
        Attempts to acquire a slot for the given client and bucket.
        Returns:
            allowed (bool): True if allowed, False if rate limited.
            remaining (int): Remaining requests allowed in this window.
            retry_after (int): Seconds until the oldest request expires (if rate limited).
        """
        now = time.time()
        window_start = now - self.window_seconds

        with self._lock:
            self._cleanup_old_entries(now)
            dq = self._clients[client_key][bucket_name]

            # Pop expired timestamps
            while dq and dq[0] < window_start:
                dq.popleft()

            current_count = len(dq)
            if current_count >= max_limit:
                oldest = dq[0]
                retry_after = max(1, int(oldest + self.window_seconds - now))
                return False, 0, retry_after

            # Record this hit
            dq.append(now)
            remaining = max(0, max_limit - len(dq))
            return True, remaining, 0

class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    FastAPI / Starlette middleware enforcing tiered rate limits:
    - AI Stream: 30 requests / min
    - Auth endpoints: 20 requests / min
    - General API: 120 requests / min
    """
    def __init__(self, app, window_seconds: int = 60):
        super().__init__(app)
        self.limiter = SlidingWindowRateLimiter(window_seconds=window_seconds)

    def _get_client_identifier(self, request: Request) -> str:
        # Check Authorization header first for authenticated users
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer ") and len(auth_header) > 15:
            # Hash or take suffix of bearer token to identify user
            return f"token:{auth_header[-16:]}"

        # Otherwise fallback to client IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "127.0.0.1"

        return f"ip:{client_ip}"

    def _get_route_limit(self, path: str) -> Tuple[str, int]:
        """
        Returns (bucket_name, max_requests_per_window).
        """
        if "/ai/chat/stream" in path:
            return "ai_stream", 30
        elif "/auth/login" in path or "/auth/signup" in path or "/auth/register" in path:
            return "auth", 20
        else:
            return "general", 120

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path

        # Whitelist non-API routes, health check, static files, and CORS preflight
        if (
            request.method == "OPTIONS"
            or not path.startswith("/api/")
            or path == "/api/health"
            or path.startswith("/uploads")
        ):
            return await call_next(request)

        client_key = self._get_client_identifier(request)
        bucket_name, max_limit = self._get_route_limit(path)

        allowed, remaining, retry_after = self.limiter.acquire(client_key, bucket_name, max_limit)

        if not allowed:
            logger.warning(
                f"Rate limit exceeded for client {client_key} on {path} (bucket: {bucket_name}, limit: {max_limit}/min)"
            )
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Too many requests. Please wait before trying again.",
                    "retry_after_seconds": retry_after
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(max_limit),
                    "X-RateLimit-Remaining": "0"
                }
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(max_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response

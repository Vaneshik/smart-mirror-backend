from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent API abuse"""

    def __init__(self, app, requests_per_minute: int = 60, llm_requests_per_minute: int = 10):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.llm_requests_per_minute = llm_requests_per_minute

        # Storage: {ip: [(timestamp, endpoint), ...]}
        self.request_history = defaultdict(list)
        self.cleanup_interval = timedelta(minutes=5)
        self.last_cleanup = datetime.now()

    def _cleanup_old_requests(self):
        """Remove old request records to prevent memory leak"""
        now = datetime.now()
        if now - self.last_cleanup > self.cleanup_interval:
            cutoff_time = now - timedelta(minutes=2)
            for ip in list(self.request_history.keys()):
                self.request_history[ip] = [
                    (ts, endpoint) for ts, endpoint in self.request_history[ip] if ts > cutoff_time
                ]
                if not self.request_history[ip]:
                    del self.request_history[ip]
            self.last_cleanup = now

    def _is_rate_limited(self, ip: str, path: str) -> tuple[bool, str]:
        """
        Check if request should be rate limited

        Returns:
            (is_limited, error_message)
        """
        now = datetime.now()
        cutoff_time = now - timedelta(minutes=1)

        # Get requests from last minute
        recent_requests = [
            (ts, endpoint) for ts, endpoint in self.request_history[ip] if ts > cutoff_time
        ]

        # Check LLM endpoint (more expensive, stricter limit)
        if "/api/llm/" in path:
            llm_requests = [r for r in recent_requests if "/api/llm/" in r[1]]
            if len(llm_requests) >= self.llm_requests_per_minute:
                logger.warning(
                    f"Rate limit exceeded for LLM by IP {ip}: {len(llm_requests)} requests"
                )
                return (
                    True,
                    f"LLM rate limit exceeded: {self.llm_requests_per_minute} requests per minute",
                )

        # Check overall rate limit
        if len(recent_requests) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded by IP {ip}: {len(recent_requests)} requests")
            return True, f"Rate limit exceeded: {self.requests_per_minute} requests per minute"

        return False, ""

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host
        if forwarded_for := request.headers.get("X-Forwarded-For"):
            client_ip = forwarded_for.split(",")[0].strip()

        # Cleanup old records periodically
        self._cleanup_old_requests()

        # Check rate limit
        is_limited, error_msg = self._is_rate_limited(client_ip, request.url.path)
        if is_limited:
            return JSONResponse(
                status_code=429,
                content={"detail": error_msg, "retry_after": "60 seconds"},
            )

        # Record this request
        self.request_history[client_ip].append((datetime.now(), request.url.path))

        # Process request
        response = await call_next(request)
        return response

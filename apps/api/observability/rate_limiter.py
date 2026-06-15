import time
import logging
from collections import defaultdict
from fastapi import HTTPException, status, Request

logger = logging.getLogger("documind.observability.rate_limiter")

class InMemoryRateLimiter:
    def __init__(self):
        # Maps (key, limit_type) -> list of timestamps
        self.requests = defaultdict(list)

    def check_rate_limit(self, key: str, limit_type: str = "standard") -> tuple[int, int, int]:
        now = time.time()
        window = 60.0
        
        if limit_type == "heavy":
            limit = 10
        else:
            limit = 100

        timestamps = self.requests[(key, limit_type)]
        
        # Filter out timestamps older than the window
        timestamps = [t for t in timestamps if now - t < window]
        self.requests[(key, limit_type)] = timestamps

        if len(timestamps) >= limit:
            reset_seconds = max(1, int(window - (now - timestamps[0])))
            logger.warning(f"[RateLimit] Exceeded for key={key[:30]} limit_type={limit_type}. Blocked for {reset_seconds}s.")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {reset_seconds} seconds.",
                headers={
                    "Retry-After": str(reset_seconds),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_seconds)
                }
            )

        timestamps.append(now)
        remaining = limit - len(timestamps)
        reset_seconds = int(window)
        return limit, remaining, reset_seconds

rate_limiter = InMemoryRateLimiter()


def rate_limit(limit_type: str = "standard"):
    """FastAPI Dependency for rate limiting based on auth token or IP address."""
    async def dependency(request: Request):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            key = auth_header
        else:
            key = request.client.host if request.client else "unknown-ip"
            
        rate_limiter.check_rate_limit(key, limit_type)
    return dependency

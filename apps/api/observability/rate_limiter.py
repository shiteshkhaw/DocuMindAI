import time
import logging
from collections import defaultdict
from fastapi import HTTPException, status, Request

from core.redis import redis_manager

logger = logging.getLogger("documind.observability.rate_limiter")


class RedisSlidingWindowRateLimiter:
    """
    Redis-backed Sliding Window Rate Limiter.
    Uses sorted sets (ZSET) to record request timestamps per client and limit type.
    Falls back to in-memory sliding window rate limiting if Redis is unconfigured or offline.
    """

    def __init__(self) -> None:
        # In-memory fallback structures
        self._fallback_requests = defaultdict(list)

    def _get_limits(self, limit_type: str) -> tuple[int, float]:
        """Returns (max_requests, window_seconds) based on limit type."""
        if limit_type == "heavy":
            return 10, 60.0  # 10 requests per minute
        elif limit_type == "upload":
            return 50, 86400.0  # 50 requests per day (24h)
        elif limit_type == "chat":
            return 1000, 86400.0  # 1000 requests per day
        elif limit_type == "analysis":
            return 20, 3600.0  # 20 requests per hour
        else:
            return 100, 60.0  # Standard: 100 requests per minute

    async def check_rate_limit(self, key: str, limit_type: str = "standard") -> tuple[int, int, int]:
        """
        Check rate limit. If limit is exceeded, raises FastAPI HTTP 429 exception.
        Otherwise returns (limit, remaining, reset_seconds).
        """
        limit, window = self._get_limits(limit_type)
        now = time.time()
        
        # Check if Redis is connected and configured
        redis_client = redis_manager.get_client()
        is_redis_active = redis_manager._connected

        if is_redis_active:
            # Redis Sorted Set implementation:
            # Key shape: documind:ratelimit:{limit_type}:{hashed_client_key}
            import hashlib
            client_hash = hashlib.sha256(key.encode("utf-8")).hexdigest()
            redis_key = f"documind:ratelimit:{limit_type}:{client_hash}"
            
            try:
                # Remove timestamps older than window
                min_time = 0
                max_time = now - window
                
                # Execute pipeline for atomicity and latency reduction
                pipe = redis_client.pipeline()
                pipe.zremrangebyscore(redis_key, min_time, max_time)
                pipe.zcard(redis_key)
                pipe.zrangebyscore(redis_key, "-inf", "+inf")
                pipe.zadd(redis_key, {str(now): now})
                pipe.expire(redis_key, int(window))
                
                _, current_count, existing_timestamps, _, _ = await pipe.execute()
                
                if current_count >= limit:
                    first_timestamp = float(existing_timestamps[0])
                    reset_seconds = max(1, int(window - (now - first_timestamp)))
                    logger.warning(
                        f"[RateLimit] REDIS limit exceeded for client_hash={client_hash[:10]} "
                        f"limit_type={limit_type}. Blocked for {reset_seconds}s."
                    )
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
                
                remaining = limit - current_count - 1
                reset_seconds = int(window)
                return limit, remaining, reset_seconds

            except HTTPException:
                raise
            except Exception as exc:
                logger.warning(f"[RateLimit] Redis command failed, falling back to local memory: {exc}")
                # Fall back to in-memory check below

        # ── In-Memory Fallback Implementation ───────────────────────────────
        timestamps = self._fallback_requests[(key, limit_type)]
        
        # Filter older timestamps
        timestamps = [t for t in timestamps if now - t < window]
        self._fallback_requests[(key, limit_type)] = timestamps
        
        if len(timestamps) >= limit:
            reset_seconds = max(1, int(window - (now - timestamps[0])))
            logger.warning(
                f"[RateLimit] IN-MEMORY limit exceeded for key={key[:30]} "
                f"limit_type={limit_type}. Blocked for {reset_seconds}s."
            )
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


# ── Limiter instance ──────────────────────────────────────────────────────
rate_limiter = RedisSlidingWindowRateLimiter()


def rate_limit(limit_type: str = "standard"):
    """
    FastAPI dependency for rate limiting based on Authorization header or IP.
    """
    async def dependency(request: Request):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            key = auth_header
        else:
            key = request.client.host if request.client else "unknown-ip"
            
        await rate_limiter.check_rate_limit(key, limit_type)
    return dependency

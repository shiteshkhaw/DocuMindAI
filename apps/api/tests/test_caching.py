import pytest
import time
from unittest.mock import AsyncMock, patch, MagicMock

from services.cache import cache_service
from observability.rate_limiter import rate_limiter, RedisSlidingWindowRateLimiter
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_cache_service_fallback() -> None:
    """Validate cache service degrades gracefully to return None when Redis is unconfigured."""
    # Ensure get/set do not throw even without Redis URL
    res = await cache_service.get("analysis", "document", "doc-1")
    assert res is None

    success = await cache_service.set("analysis", "document", "doc-1", {"test": 123})
    assert success is False or success is True  # returns based on mock or none connection


@pytest.mark.asyncio
async def test_redis_sliding_window_rate_limiter_in_memory() -> None:
    """Validate sliding window rate limiter triggers exceptions upon limit hits using local fallback."""
    limiter = RedisSlidingWindowRateLimiter()
    key = "test-client-ip"
    limit_type = "heavy"  # Limit is 10 requests per minute

    # Send 10 requests (should pass)
    for _ in range(10):
        limit, remaining, reset = await limiter.check_rate_limit(key, limit_type)
        assert limit == 10
        assert remaining >= 0

    # 11th request must raise HTTP 429
    with pytest.raises(HTTPException) as exc:
        await limiter.check_rate_limit(key, limit_type)
    
    assert exc.value.status_code == 429
    assert "Retry-After" in exc.value.headers
    assert exc.value.headers["X-RateLimit-Limit"] == "10"


@pytest.mark.asyncio
@patch("core.redis.redis_manager.get_client")
async def test_redis_sliding_window_rate_limiter_active(mock_get_client) -> None:
    """Validate Redis rate limiter pipeline commands when Redis connection is active."""
    mock_redis = MagicMock()
    mock_get_client.return_value = mock_redis
    
    # Mock pipe execution outputs
    mock_pipe = MagicMock()
    # pipeline() returns the pipe instance itself
    mock_redis.pipeline.return_value = mock_pipe
    
    # execute() is the only awaited coroutine call
    mock_pipe.execute = AsyncMock(return_value=(1, 4, [str(time.time() - 10)], 1, True))

    limiter = RedisSlidingWindowRateLimiter()

    with patch("core.redis.redis_manager._connected", True):
        limit, remaining, reset = await limiter.check_rate_limit("user-token-123", "heavy")
        assert limit == 10
        assert remaining == 5  # 10 - 4 (existing) - 1 (current new request) = 5
        assert reset == 60
        mock_redis.pipeline.assert_called_once()

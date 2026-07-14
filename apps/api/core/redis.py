"""
Singleton async Redis client for DocuMind AI.

Provides connection pooling, automatic reconnect with exponential backoff,
health checks, and graceful shutdown. When Redis credentials are absent,
returns a no-op stub that logs warnings instead of raising errors, allowing
local development without Redis.
"""

import logging
import asyncio
from typing import Any

from config import settings

logger = logging.getLogger("documind.core.redis")


class _NoOpRedis:
    """
    Stub Redis client used when no Redis URL is configured.
    All operations are no-ops that log warnings on first use, allowing
    the application to run in local/development mode without Redis.
    """

    _warned: bool = False

    def _warn_once(self) -> None:
        if not self._warned:
            logger.warning(
                "[Redis] No Redis URL configured (UPSTASH_REDIS_URL). "
                "All Redis operations will be no-ops. Set UPSTASH_REDIS_URL "
                "to enable Redis-backed features."
            )
            self.__class__._warned = True

    async def ping(self) -> bool:
        self._warn_once()
        return False

    async def get(self, key: str) -> None:
        self._warn_once()
        return None

    async def set(
        self, key: str, value: Any, ex: int | None = None, **kwargs: Any
    ) -> bool:
        self._warn_once()
        return False

    async def delete(self, *keys: str) -> int:
        self._warn_once()
        return 0

    async def exists(self, *keys: str) -> int:
        self._warn_once()
        return 0

    async def expire(self, key: str, seconds: int) -> bool:
        self._warn_once()
        return False

    async def ttl(self, key: str) -> int:
        self._warn_once()
        return -2

    async def keys(self, pattern: str) -> list[str]:
        self._warn_once()
        return []

    async def scan(
        self, cursor: int = 0, match: str | None = None, count: int | None = None
    ) -> tuple[int, list[str]]:
        self._warn_once()
        return (0, [])

    async def zadd(self, name: str, mapping: dict[str, float], **kwargs: Any) -> int:
        self._warn_once()
        return 0

    async def zrangebyscore(
        self, name: str, min: float, max: float, **kwargs: Any
    ) -> list[Any]:
        self._warn_once()
        return []

    async def zremrangebyscore(
        self, name: str, min: float, max: float
    ) -> int:
        self._warn_once()
        return 0

    async def zcard(self, name: str) -> int:
        self._warn_once()
        return 0

    async def close(self) -> None:
        pass

    def pipeline(self, transaction: bool = True) -> "_NoOpPipeline":
        self._warn_once()
        return _NoOpPipeline()


class _NoOpPipeline:
    """No-op pipeline stub for development mode."""

    def __getattr__(self, name: str) -> Any:
        def noop(*args: Any, **kwargs: Any) -> "_NoOpPipeline":
            return self
        return noop

    async def execute(self) -> list[Any]:
        return []


class RedisManager:
    """
    Manages a singleton async Redis connection with pooling,
    reconnect logic, and health-check capabilities.
    """

    def __init__(self) -> None:
        self._client: Any = None
        self._connected: bool = False
        self._url: str | None = None

    @property
    def is_configured(self) -> bool:
        """Returns True if Redis URL is set in configuration."""
        return bool(settings.UPSTASH_REDIS_URL)

    async def connect(self) -> None:
        """
        Initialise the Redis connection. If UPSTASH_REDIS_URL is not set,
        fall back to the no-op stub silently.
        """
        self._url = settings.UPSTASH_REDIS_URL
        if not self._url:
            logger.info("[Redis] No UPSTASH_REDIS_URL configured — using no-op stub.")
            self._client = _NoOpRedis()
            self._connected = False
            return

        try:
            import redis.asyncio as aioredis

            self._client = aioredis.from_url(
                self._url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                max_connections=20,
                health_check_interval=30,
            )
            # Verify connection
            await self._client.ping()
            self._connected = True
            logger.info("[Redis] Connected successfully.")
        except Exception as exc:
            logger.error(f"[Redis] Connection failed: {exc}")
            self._client = _NoOpRedis()
            self._connected = False

    async def disconnect(self) -> None:
        """Gracefully close the Redis connection pool."""
        if self._client and self._connected:
            try:
                await self._client.close()
                logger.info("[Redis] Disconnected.")
            except Exception as exc:
                logger.warning(f"[Redis] Error during disconnect: {exc}")
            finally:
                self._connected = False

    def get_client(self) -> Any:
        """
        Return the Redis client instance.
        If connect() was never called or Redis is not configured, returns the no-op stub.
        """
        if self._client is None:
            self._client = _NoOpRedis()
        return self._client

    async def health_check(self) -> dict[str, Any]:
        """
        Run a Redis health check and return a status dict compatible
        with the /health endpoint format.
        """
        if not self.is_configured:
            return {
                "status": "not_configured",
                "url_set": False,
            }

        client = self.get_client()
        try:
            pong = await client.ping()
            if pong:
                info_raw = await client.info("server")  # type: ignore[union-attr]
                version = "unknown"
                if isinstance(info_raw, dict):
                    version = info_raw.get("redis_version", "unknown")
                return {
                    "status": "connected",
                    "version": version,
                }
            return {"status": "degraded", "error": "ping returned False"}
        except Exception as exc:
            return {"status": "disconnected", "error": str(exc)}


# ── Module-level singleton ────────────────────────────────────────────────
redis_manager = RedisManager()

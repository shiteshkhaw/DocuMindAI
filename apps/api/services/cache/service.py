import json
import logging
from typing import Any

from core.redis import redis_manager

logger = logging.getLogger("documind.services.cache")


class CacheService:
    """
    Production-grade Redis Caching Layer.
    Provides key-versioning, automatic serialization, TTL enforcement,
    and falls back to no-op silently if Redis is disconnected.
    """

    def __init__(self, key_prefix: str = "documind") -> None:
        self.prefix = key_prefix

    def _make_key(self, service: str, resource: str, identifier: str) -> str:
        """Construct standard key pattern: documind:{service}:{resource}:{identifier}"""
        return f"{self.prefix}:{service}:{resource}:{identifier}"

    async def get(self, service: str, resource: str, identifier: str) -> Any | None:
        """Retrieve key value and deserialize automatically."""
        key = self._make_key(service, resource, identifier)
        client = redis_manager.get_client()
        try:
            val = await client.get(key)
            if val is not None:
                logger.debug(f"[Cache] Hit for key: {key}")
                return json.loads(val)
            logger.debug(f"[Cache] Miss for key: {key}")
            return None
        except Exception as exc:
            logger.warning(f"[Cache] Get operation failed for key={key}: {exc}")
            return None

    async def set(
        self,
        service: str,
        resource: str,
        identifier: str,
        value: Any,
        ttl_seconds: int = 3600,
    ) -> bool:
        """Store key value and serialize automatically with TTL enforcement."""
        key = self._make_key(service, resource, identifier)
        client = redis_manager.get_client()
        try:
            val_str = json.dumps(value)
            await client.set(key, val_str, ex=ttl_seconds)
            logger.debug(f"[Cache] Set key: {key} with TTL: {ttl_seconds}s")
            return True
        except Exception as exc:
            logger.warning(f"[Cache] Set operation failed for key={key}: {exc}")
            return False

    async def delete(self, service: str, resource: str, identifier: str) -> bool:
        """Invalidate a specific cache key."""
        key = self._make_key(service, resource, identifier)
        client = redis_manager.get_client()
        try:
            await client.delete(key)
            logger.debug(f"[Cache] Deleted key: {key}")
            return True
        except Exception as exc:
            logger.warning(f"[Cache] Delete operation failed for key={key}: {exc}")
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate cache keys matching pattern wildcard.
        Uses non-blocking SCAN instead of KEYS to protect production Redis instances.
        """
        client = redis_manager.get_client()
        full_pattern = f"{self.prefix}:{pattern}"
        logger.info(f"[Cache] Invalidating pattern: {full_pattern}")
        
        count = 0
        try:
            cursor = 0
            while True:
                cursor, keys = await client.scan(cursor, match=full_pattern, count=100)
                if keys:
                    await client.delete(*keys)
                    count += len(keys)
                if cursor == 0:
                    break
            logger.info(f"[Cache] Invalidated {count} keys matching pattern: {full_pattern}")
            return count
        except Exception as exc:
            logger.warning(f"[Cache] Invalidation failed for pattern={full_pattern}: {exc}")
            return 0


# ── Module-level singleton ────────────────────────────────────────────────
cache_service = CacheService()

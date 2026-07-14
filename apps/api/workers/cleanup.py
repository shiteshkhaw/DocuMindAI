import asyncio
import logging
import dramatiq

from workers.broker import broker

logger = logging.getLogger("documind.workers.cleanup")


async def _run_async_cleanup() -> None:
    logger.info("[CleanupWorker] Starting scheduled background tasks cleanup.")
    # Standard cleanup tasks: remove orphaned records, temp upload slices, etc.
    # Exists as a placeholder/template for general background garbage collection.
    await asyncio.sleep(0.1)
    logger.info("[CleanupWorker] Background cleanup complete.")


@dramatiq.actor(max_retries=1)
def run_background_cleanup() -> None:
    """Dramatiq actor for periodic cleanup tasks."""
    from workers.broker import run_async
    run_async(_run_async_cleanup())

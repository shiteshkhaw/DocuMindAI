import logging
from typing import Any
import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.brokers.stub import StubBroker

from config import settings

logger = logging.getLogger("documind.workers.broker")

# Create and set the broker
broker_url = settings.effective_broker_url

if broker_url:
    logger.info(f"[Workers] Initialising Redis broker with URL: {broker_url}")
    broker = RedisBroker(url=broker_url)
else:
    logger.warning("[Workers] No Redis URL configured. Falling back to StubBroker (in-memory).")
    broker = StubBroker()

dramatiq.set_broker(broker)


def is_stub_broker() -> bool:
    """Returns True if the broker is running in-memory (stub mode)."""
    return isinstance(broker, StubBroker)


def run_async(coro) -> Any:
    """
    Safely execute an async coroutine from a synchronous context.
    If called from a thread with an already running event loop (e.g. pytest-asyncio tests),
    runs the coroutine in a separate thread to prevent event loop nesting errors.
    """
    import asyncio
    import concurrent.futures

    try:
        asyncio.get_running_loop()
        # A loop is running, spawn a new thread to run the coroutine in a fresh loop
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(asyncio.run, coro).result()
    except RuntimeError:
        # No loop is running, safe to run in the current thread
        return asyncio.run(coro)

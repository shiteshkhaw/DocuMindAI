import logging
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from config import settings

logger = logging.getLogger("documind.core.sentry")


def init_sentry() -> None:
    """Initialize Sentry Monitoring with distributed tracing and profiling."""
    dsn = settings.SENTRY_DSN
    if not dsn:
        logger.info("[Sentry] No SENTRY_DSN configured. Monitoring disabled.")
        return

    try:
        sentry_sdk.init(
            dsn=dsn,
            environment=settings.SENTRY_ENVIRONMENT,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,
            send_default_pii=True,  # Allows capturing user context safely
        )
        logger.info(
            f"[Sentry] Initialised successfully in environment: {settings.SENTRY_ENVIRONMENT}"
        )
    except Exception as exc:
        logger.error(f"[Sentry] Failed to initialise Sentry: {exc}")


def set_user_context(user_id: str, email: str | None = None) -> None:
    """Safely associate current request/context with a user in Sentry."""
    sentry_sdk.set_user({"id": user_id, "email": email})

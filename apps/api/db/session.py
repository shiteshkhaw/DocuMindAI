from typing import AsyncGenerator
from sqlalchemy import event
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import settings

# Create async engine with pool configuration suitable for production
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Event listener to set a flushed flag on session info
@event.listens_for(Session, 'after_flush')
def receive_after_flush(session, flush_context):
    session.info['flushed'] = True

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection helper that yields an async database session
    and ensures proper cleanup. Only commits if the session has been
    modified or has flushed changes during the request, saving round-trips.
    """
    async with async_session_factory() as session:
        try:
            yield session
            # Commit only if session is dirty, has new/deleted objects, or was flushed
            if (
                session.new or 
                session.dirty or 
                session.deleted or 
                session.sync_session.info.get('flushed', False)
            ):
                await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

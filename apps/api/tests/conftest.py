import os
from typing import AsyncGenerator
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from db.base import Base
# Import all models so SQLAlchemy metadata is fully populated before table creation
from models import DocumentModel, DocumentAnalysisModel, ChatSessionModel, MessageModel  # noqa: F401

# Ensure ChromaVectorStore uses ephemeral in-memory mode during tests
os.environ["CHROMA_SERVER_HOST"] = ""
os.environ["CHROMA_PERSIST_DIRECTORY"] = ""
os.environ["CHROMA_API_KEY"] = ""

# Ensure storage provider uses LocalStorageProvider during tests
os.environ["SUPABASE_URL"] = ""
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = ""

# Ensure dramatiq uses StubBroker (in-memory) during tests
os.environ["UPSTASH_REDIS_URL"] = ""
os.environ["DRAMATIQ_BROKER_URL"] = ""


@pytest_asyncio.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides an isolated, in-memory SQLite AsyncSession per test function.
    All tables are created fresh and torn down after each test.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with session_factory() as session:
        yield session
        await session.rollback()

    await engine.dispose()


from httpx import AsyncClient
from main import app
from db.session import get_db

@pytest_asyncio.fixture
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provides an AsyncClient configured to use the in-memory test database."""
    async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
        yield test_db

    app.dependency_overrides[get_db] = _get_test_db
    import httpx
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

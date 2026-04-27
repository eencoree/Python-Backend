import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.models import Base

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DB_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

TestSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        async_session = async_sessionmaker(
            bind=conn,
            expire_on_commit=False
        )

        async with async_session() as session:
            yield session
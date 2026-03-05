"""Test configuration and fixtures."""
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from app.core.session import get_async_session
from app.core.settings import Settings, get_default_settings
from app.identity.application.security import get_password_hasher
from app.identity.application.services import UserCommandService, UserQueryService
from app.identity.domain.entities import User
from app.identity.infra.repositories.user_command_repository import UserCommandRepository
from app.identity.infra.repositories.user_query_repository import UserQueryRepository
from app.main import create_app


def get_test_settings() -> Settings:
    """Create test settings with test database and simple password validation."""
    return get_default_settings(
        DB_HOST="localhost",
        DB_NAME="test",
        DB_USER="test",
        DB_PASSWORD="test",
        ADMIN_EMAIL="admin@test.com",
        ADMIN_PASSWORD="admin@test.com",
        AUTH_ALLOW_SIMPLE_PASSWORDS=True,
    )


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Get test settings."""
    return get_test_settings()


@pytest_asyncio.fixture(scope="function")
async def db_engine(test_settings: Settings):
    """Create async database engine for tests."""
    engine = create_async_engine(
        test_settings.DB.dsn,
        echo=False,
        pool_pre_ping=True,
    )

    # Create all tables
    from app.core.infra.base_model import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session_factory(db_engine):
    """Create session factory for tests."""
    return async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


@pytest_asyncio.fixture(scope="function")
async def db_session(db_session_factory) -> AsyncGenerator[AsyncSession, None]:
    async with db_session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def test_app(
    db_session: AsyncSession,
    test_settings: Settings,
) -> AsyncGenerator[FastAPI, None]:

    async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    application = create_app(test_settings)
    application.dependency_overrides[get_async_session] = get_test_session

    yield application

    application.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def admin_user(
    db_session: AsyncSession,
    test_settings: Settings,
) -> User:
    user_command_repo = UserCommandRepository(db_session)
    user_query_repo = UserQueryRepository(db_session)
    password_hasher = get_password_hasher()

    command_service = UserCommandService(
        command_repo=user_command_repo,
        query_repo=user_query_repo,
        password_hasher=password_hasher,
    )

    from app.identity.dto.user_dto import UserCreateRequestDTO

    admin_data = UserCreateRequestDTO(
        email=test_settings.ADMIN_EMAIL,
        password=test_settings.ADMIN_PASSWORD.get_secret_value(),
        first_name="Super",
        last_name="Admin",
    )

    user_id = await command_service.create_user(admin_data)

    query_service = UserQueryService(user_query_repo)
    user_model = await query_service.get_user_by_id(user_id)

    return user_model



@pytest.fixture(scope="function")
def client(test_app: FastAPI) -> Generator[TestClient, None, None]:
    http_client = TestClient(test_app)
    yield http_client
    http_client.close()


@pytest_asyncio.fixture(scope="function")
async def admin_client(
    test_app: FastAPI,
    test_settings: Settings,
    admin_user: User,
) -> AsyncGenerator[AsyncClient, None]:
    from httpx import ASGITransport
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        resp = await http_client.post('/api/v1/auth/login', data={
            'username': test_settings.ADMIN_EMAIL,
            'password': test_settings.ADMIN_PASSWORD.get_secret_value(),
        })
        assert resp.status_code == 200, f"Login failed: {resp.text}"
        http_client.headers['Authorization'] = f'Bearer {resp.json()["access_token"]}'
        yield http_client

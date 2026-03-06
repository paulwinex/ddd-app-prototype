"""Application and HTTP client fixtures."""
from typing import AsyncGenerator

import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.session import get_async_session
from app.core.settings import Settings
from app.identity.application.security import get_password_hasher
from app.identity.domain.entities import User
from app.main import create_app


@pytest_asyncio.fixture(scope="function")
async def async_db_session(test_settings: Settings) -> AsyncGenerator[AsyncSession, None]:
    """Create async database session for test app."""
    engine = create_async_engine(test_settings.DB.dsn, echo=False)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, autocommit=False, autoflush=False)

    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        finally:
            await session.rollback()
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_app(
    async_db_session: AsyncSession,
    test_settings: Settings,
) -> AsyncGenerator[FastAPI, None]:
    """Create test app with overridden dependencies."""

    async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
        yield async_db_session

    application = create_app(test_settings)
    application.dependency_overrides[get_async_session] = get_test_session

    yield application

    application.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create HTTP client for testing."""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://localhost:8000") as http_client:
        yield http_client


@pytest_asyncio.fixture(scope="function")
async def admin_client(
    test_app: FastAPI,
    test_settings: Settings,
    admin_user: User,
) -> AsyncGenerator[AsyncClient, None]:
    """Create authenticated HTTP client with admin privileges."""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://localhost:8000") as http_client:
        resp = await http_client.post(
            '/api/v1/auth/login', data={
                'username': test_settings.ADMIN_EMAIL,
                'password': test_settings.ADMIN_PASSWORD.get_secret_value(),
                'grant_type': 'password',
            },
            headers={'accept': 'application/json'}
        )
        assert resp.status_code == 200, f"Login failed: {resp.text}"
        http_client.headers['Authorization'] = f'Bearer {resp.json()["access_token"]}'
        yield http_client


@pytest_asyncio.fixture(scope="function")
async def authenticated_client(
    test_app: FastAPI,
    regular_user: User,
) -> AsyncGenerator[AsyncClient, None]:
    """Create authenticated HTTP client with regular user privileges."""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://localhost:8000") as http_client:
        resp = await http_client.post(
            '/api/v1/auth/login', data={
                'username': str(regular_user.email),
                'password': 'regularpass123',
                'grant_type': 'password',
            },
            headers={'accept': 'application/json'}
        )
        assert resp.status_code == 200, f"Login failed: {resp.text}"
        http_client.headers['Authorization'] = f'Bearer {resp.json()["access_token"]}'
        yield http_client

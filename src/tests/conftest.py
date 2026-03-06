from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker

from app.core.session import get_async_session
from app.core.settings import Settings, get_default_settings
from app.identity.application.security import get_password_hasher
from app.identity.domain.entities import User
from app.identity.infra.models.user_model import UserModel
from app.identity.mappers.user_mapper import UserMapper
from app.main import create_app


def get_test_settings() -> Settings:
    """Create test settings with test database and simple password validation."""
    return get_default_settings(
        DB_HOST="celan_arch_prototype-db-testing",
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
async def admin_user(test_settings: Settings) -> User:
    dsn = test_settings.DB.dsn.replace("postgresql+asyncpg", "postgresql+psycopg")
    sync_engine = create_engine(dsn, echo=False)
    sync_session_factory = sessionmaker(bind=sync_engine, class_=Session, autocommit=False, autoflush=False)

    with sync_session_factory() as session:
        stmt = select(UserModel).where(UserModel.email == test_settings.ADMIN_EMAIL.lower())
        result = session.execute(stmt)
        user_model = result.scalar_one_or_none()

        if not user_model:
            password_hasher = get_password_hasher()
            user_model = UserModel(
                email=test_settings.ADMIN_EMAIL.lower(),
                password_hash=password_hasher.hash(test_settings.ADMIN_PASSWORD.get_secret_value()),
                first_name="Super",
                last_name="Admin",
                is_active=True,
                is_superuser=True,
                is_verified=True,
            )
            session.add(user_model)
            session.commit()
            session.refresh(user_model)
        return UserMapper.to_entity(user_model)


@pytest_asyncio.fixture(scope="function")
async def async_db_session(test_settings: Settings) -> AsyncGenerator[AsyncSession, None]:
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

    async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
        yield async_db_session

    application = create_app(test_settings)
    application.dependency_overrides[get_async_session] = get_test_session
    yield application
    application.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://localhost:8000") as http_client:
        yield http_client


@pytest_asyncio.fixture(scope="function")
async def admin_client(
    test_app: FastAPI,
    test_settings: Settings,
    admin_user: User,
) -> AsyncGenerator[AsyncClient, None]:
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

import uuid

import pytest_asyncio
from sqlalchemy import create_engine, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, sessionmaker

from app.core.settings import Settings
from app.identity.application.security import get_password_hasher
from app.identity.domain.entities import User
from app.identity.infra.models.user_model import UserModel
from app.identity.mappers.user_mapper import UserMapper


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
async def regular_user(test_settings: Settings, async_db_session: AsyncSession) -> User:
    password_hasher = get_password_hasher()
    unique_id = str(uuid.uuid4())[:8]
    user_model = UserModel(
        email=f"regular_{unique_id}@test.com",
        password_hash=password_hasher.hash("regularpass123"),
        first_name="Regular",
        last_name="User",
        is_active=True,
        is_superuser=False,
        is_verified=False,
    )
    async_db_session.add(user_model)
    await async_db_session.commit()
    await async_db_session.refresh(user_model)

    return UserMapper.to_entity(user_model)

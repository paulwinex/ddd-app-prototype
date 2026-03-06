from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import get_default_settings
from app.identity.application.security import get_password_hasher
from app.identity.domain.entities import User
from app.identity.domain.value_objects import UserID, EmailVO, PasswordVO
from app.identity.infra.models import UserModel


async def init_database(session: AsyncSession) -> None:
    await _init_superuser(session)


async def _init_superuser(session: AsyncSession) -> None:
    settings = get_default_settings()
    stmt = select(UserModel).where(UserModel.is_superuser == True)
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        logger.info("Superuser already exists")
        return

    stmt = select(UserModel).where(UserModel.email == settings.ADMIN_EMAIL)
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        logger.warning(f"User with email {settings.ADMIN_EMAIL} already exists")
        return

    hasher = get_password_hasher()
    password_hash = hasher.hash(settings.ADMIN_PASSWORD.get_secret_value())

    user = User(
        id=UserID(),
        email=EmailVO.create(settings.ADMIN_EMAIL),
        password=PasswordVO(password_hash),
        first_name="Super",
        last_name="Admin",
        is_superuser=True,
        is_active=True,
        is_verified=True,
    )

    model = UserModel(
        id=str(user.id),
        email=str(user.email),
        password_hash=str(user.password.value),
        first_name=user.first_name,
        last_name=user.last_name,
        is_superuser=user.is_superuser,
        is_active=user.is_active,
        is_verified=user.is_verified,
    )
    session.add(model)
    await session.flush()
    logger.info(f"Created superuser: {settings.ADMIN_EMAIL}")

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import get_default_settings
from app.core.domain.permission_discovery import get_all_permissions
from app.identity.application.security import get_password_hasher
from app.identity.domain.entities import User, Group, Permission
from app.identity.domain.value_objects import UserID, GroupID, PermissionID, EmailVO, PasswordVO
from app.identity.infra.models import UserModel, GroupModel, PermissionModel


async def init_database(session: AsyncSession) -> None:
    await _init_superuser(session)
    await _init_permissions(session)
    await _init_system_group(session)
    await _assign_superuser_to_system_group(session)


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


async def _init_permissions(session: AsyncSession) -> None:
    """Initialize permissions from all permission enums discovered in the codebase."""
    all_permissions = get_all_permissions()

    stmt = select(PermissionModel.codename)
    result = await session.execute(stmt)
    existing_codenames = {row.codename for row in result.all()}

    permissions_to_create = []
    for perm_enum in all_permissions:
        codename = str(perm_enum)
        if codename in existing_codenames:
            continue

        permissions_to_create.append(
            Permission(
                id=PermissionID(),
                name=perm_enum.name.replace("_", " ").title(),
                codename=codename,
            )
        )

    if permissions_to_create:
        for perm in permissions_to_create:
            session.add(PermissionModel(
                id=str(perm.id),
                name=perm.name,
                codename=perm.codename,
            ))
        await session.flush()
        logger.info(f"Created {len(permissions_to_create)} permissions")
    else:
        logger.info("All permissions already exist")


async def _init_system_group(session: AsyncSession) -> None:
    """Create system admins group if it doesn't exist."""
    default_group_name = "admins"
    stmt = select(GroupModel).where(GroupModel.name == default_group_name)
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        logger.info(f"System group '{default_group_name}' already exists")
        return

    group = Group(
        id=GroupID(),
        name=default_group_name,
        description="System administrators with full access",
        is_system=True,
    )

    model = GroupModel(
        id=str(group.id),
        name=group.name,
        description=group.description,
        is_system=group.is_system,
    )
    session.add(model)
    await session.flush()
    logger.info(f"Created system group: {default_group_name}")


async def _assign_superuser_to_system_group(session: AsyncSession) -> None:
    """Assign superuser to system admins group if not already assigned."""
    from app.identity.infra.models import UserGroupModelM2M

    stmt = select(UserModel).where(UserModel.is_superuser == True)
    result = await session.execute(stmt)
    superuser = result.scalar_one_or_none()

    if not superuser:
        logger.warning("No superuser found to assign to system group")
        return

    stmt = select(GroupModel).where(GroupModel.name == "admins", GroupModel.is_system == True)
    result = await session.execute(stmt)
    admins_group = result.scalar_one_or_none()

    if not admins_group:
        logger.warning("System admins group not found")
        return

    stmt = select(UserGroupModelM2M).where(
        UserGroupModelM2M.user_id == superuser.id,
        UserGroupModelM2M.group_id == admins_group.id,
    )
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        logger.info("Superuser already assigned to system admins group")
        return

    association = UserGroupModelM2M(user_id=superuser.id, group_id=admins_group.id)
    session.add(association)
    await session.flush()
    logger.info("Assigned superuser to system admins group")

import uuid

import pytest_asyncio
from sqlalchemy import select

from app.identity.application.mappers import GroupMapper, PermissionMapper
from app.identity.domain.entities import Group, Permission
from app.identity.domain.value_objects import GroupID, PermissionID
from app.identity.infra.models import GroupModel, PermissionModel, UserGroupModelM2M, GroupPermissionModelM2M


@pytest_asyncio.fixture(scope="function")
async def test_group(async_db_session) -> Group:
    unique_id = str(uuid.uuid4())[:8]
    group_model = GroupModel(
        id=str(GroupID()),
        name=f"Test Group {unique_id}",
        description="Test group for testing",
        is_system=False,
    )
    async_db_session.add(group_model)
    await async_db_session.commit()
    await async_db_session.refresh(group_model)
    return GroupMapper.orm_to_entity(group_model)


@pytest_asyncio.fixture(scope="function")
async def system_group(async_db_session) -> Group:
    stmt = select(GroupModel).where(GroupModel.name == "admins", GroupModel.is_system == True)
    result = await async_db_session.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        return GroupMapper.orm_to_entity(existing)

    group_model = GroupModel(
        id=str(GroupID()),
        name="admins",
        description="System administrators",
        is_system=True,
    )
    async_db_session.add(group_model)
    await async_db_session.commit()
    await async_db_session.refresh(group_model)
    return GroupMapper.orm_to_entity(group_model)


@pytest_asyncio.fixture(scope="function")
async def test_permission(async_db_session) -> Permission:
    unique_id = str(uuid.uuid4())[:8]
    permission_model = PermissionModel(
        id=str(PermissionID()),
        name=f"Test Permission {unique_id}",
        codename=f"test.can_test_{unique_id}",
    )
    async_db_session.add(permission_model)
    await async_db_session.commit()
    await async_db_session.refresh(permission_model)
    return PermissionMapper.to_entity(permission_model)


@pytest_asyncio.fixture(scope="function")
async def group_with_permissions(async_db_session, test_permission) -> Group:
    unique_id = str(uuid.uuid4())[:8]
    group_model = GroupModel(
        id=str(GroupID()),
        name=f"Group With Permissions {unique_id}",
        description="Test group with permissions",
        is_system=False,
    )
    async_db_session.add(group_model)
    await async_db_session.flush()

    group_perm = GroupPermissionModelM2M(
        group_id=group_model.id,
        permission_id=test_permission.id.value,
    )
    async_db_session.add(group_perm)
    await async_db_session.commit()
    await async_db_session.refresh(group_model)

    return GroupMapper.orm_to_entity(group_model)


@pytest_asyncio.fixture(scope="function")
async def user_in_group(async_db_session, regular_user, test_group):
    user_group = UserGroupModelM2M(
        user_id=str(regular_user.id),
        group_id=str(test_group.id),
    )
    async_db_session.add(user_group)
    await async_db_session.commit()
    return regular_user

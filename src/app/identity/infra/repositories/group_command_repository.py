from sqlalchemy import update, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.infra.repository_base import BaseRepository
from app.core.exceptions import NotFoundError
from app.identity.domain.entities import Group
from app.identity.domain.interfaces import GroupCommandRepositoryProtocol
from app.identity.application.mappers import GroupMapper
from app.identity.infra.models import GroupModel, UserGroupModelM2M, GroupPermissionModelM2M


class GroupCommandRepository(BaseRepository, GroupCommandRepositoryProtocol):
    model_class = GroupModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create(self, group: Group) -> str:
        model = GroupMapper.to_model(group)
        self.session.add(model)
        await self.session.flush([model])
        return model.id

    async def update(self, id: str, group: Group) -> str:
        model = GroupMapper.to_model(group)
        await self.session.execute(
            update(GroupModel)
            .where(GroupModel.id == id)
            .values(
                name=model.name,
                description=model.description,
                is_system=model.is_system,
            )
        )
        await self.session.flush()
        return id

    async def delete(self, id: str) -> None:
        await self.session.execute(
            delete(GroupModel).where(GroupModel.id == id)
        )
        await self.session.flush()

    async def add_user(self, group_id: str, user_id: str) -> None:
        stmt = select(UserGroupModelM2M).where(
            UserGroupModelM2M.user_id == user_id,
            UserGroupModelM2M.group_id == group_id,
        )
        result = await self.session.execute(stmt)
        if result.scalar_one_or_none():
            return

        association = UserGroupModelM2M(user_id=user_id, group_id=group_id)
        self.session.add(association)
        await self.session.flush()

    async def remove_user(self, group_id: str, user_id: str) -> None:
        await self.session.execute(
            delete(UserGroupModelM2M).where(
                UserGroupModelM2M.user_id == user_id,
                UserGroupModelM2M.group_id == group_id,
            )
        )
        await self.session.flush()

    async def add_permission(self, group_id: str, permission_id: str) -> None:
        stmt = select(GroupPermissionModelM2M).where(
            GroupPermissionModelM2M.group_id == group_id,
            GroupPermissionModelM2M.permission_id == permission_id,
        )
        result = await self.session.execute(stmt)
        if result.scalar_one_or_none():
            return

        association = GroupPermissionModelM2M(group_id=group_id, permission_id=permission_id)
        self.session.add(association)
        await self.session.flush()

    async def remove_permission(self, group_id: str, permission_id: str) -> None:
        await self.session.execute(
            delete(GroupPermissionModelM2M).where(
                GroupPermissionModelM2M.group_id == group_id,
                GroupPermissionModelM2M.permission_id == permission_id,
            )
        )
        await self.session.flush()

    async def get_group_users(self, group_id: str) -> list[str]:
        stmt = select(UserGroupModelM2M.user_id).where(UserGroupModelM2M.group_id == group_id)
        result = await self.session.execute(stmt)
        return [row.user_id for row in result.all()]

    async def get_group_permissions(self, group_id: str) -> list[str]:
        stmt = select(GroupPermissionModelM2M.permission_id).where(
            GroupPermissionModelM2M.group_id == group_id
        )
        result = await self.session.execute(stmt)
        return [row.permission_id for row in result.all()]

    async def get_by_id(self, id: str) -> GroupModel:
        stmt = select(self.model_class).where(self.model_class.id == id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise NotFoundError(f"Group with id {id} not found")
        return model

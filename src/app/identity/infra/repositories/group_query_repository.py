from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.infra.repository_base import BaseRepository
from app.core.exceptions import NotFoundError
from app.identity.domain.entities import Group
from app.identity.domain.interfaces import GroupQueryRepositoryProtocol
from app.identity.domain.value_objects import GroupID
from app.identity.application.mappers import GroupMapper
from app.identity.infra.models import GroupModel, UserGroupModelM2M, UserModel


class GroupQueryRepository(BaseRepository[GroupModel, Group], GroupQueryRepositoryProtocol):
    model_class = GroupModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_id(
        self,
        id_: str | GroupID,
        load_members: bool = False,
        load_permissions: bool = False,
    ) -> Group:
        if isinstance(id_, GroupID):
            id_ = str(id_)

        stmt = select(self.model_class).where(GroupModel.id == id_)
        options = []
        if load_members:
            options.append(joinedload(self.model_class.users))
        if load_permissions:
            options.append(joinedload(self.model_class.permissions))
        if options:
            stmt = stmt.options(*options)

        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise NotFoundError(f"Group with id {id_} not found")
        return self._to_entity(model)

    async def get_by_name(
        self,
        name: str,
        load_members: bool = False,
        load_permissions: bool = False,
    ) -> Group | None:
        stmt = select(GroupModel).where(GroupModel.name == name)
        options = []
        if load_members:
            options.append(joinedload(GroupModel.users))
        if load_permissions:
            options.append(joinedload(GroupModel.permissions))

        if options:
            stmt = stmt.options(*options)

        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def user_in_group(self, user_id: str, group_id: str) -> bool:
        stmt = select(UserGroupModelM2M).where(
            UserGroupModelM2M.user_id == user_id,
            UserGroupModelM2M.group_id == group_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_user_groups(self, user_id: str) -> list[Group]:
        stmt = select(GroupModel).join(GroupModel.users).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        models = list(result.scalars().all())
        return [self._to_entity(model) for model in models]

    def _to_entity(self, model: GroupModel) -> Group:
        return GroupMapper.orm_to_entity(model)

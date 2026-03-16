from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.infra.repository_base import BaseRepository
from app.core.exceptions import NotFoundError
from app.identity.domain.entities import Permission
from app.identity.domain.interfaces import PermissionQueryRepositoryProtocol
from app.identity.domain.value_objects import PermissionID
from app.identity.application.mappers import PermissionMapper
from app.identity.infra.models import PermissionModel


class PermissionQueryRepository(
    BaseRepository[PermissionModel, Permission], PermissionQueryRepositoryProtocol
):
    model_class = PermissionModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_id(self, id_: str | PermissionID) -> Permission:
        if isinstance(id_, PermissionID):
            id_ = str(id_)

        stmt = select(self.model_class).where(PermissionModel.id == id_)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise NotFoundError(f"Permission with id {id_} not found")
        return self._to_entity(model)

    async def get_by_codename(self, codename: str) -> Permission | None:
        stmt = select(PermissionModel).where(PermissionModel.codename == codename)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    def _to_entity(self, model: PermissionModel) -> Permission:
        return PermissionMapper.to_entity(model)

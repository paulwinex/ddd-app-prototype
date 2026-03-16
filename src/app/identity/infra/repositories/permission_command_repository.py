from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.infra.repository_base import BaseRepository
from app.core.exceptions import NotFoundError
from app.identity.domain.entities import Permission
from app.identity.domain.interfaces import PermissionCommandRepositoryProtocol
from app.identity.application.mappers import PermissionMapper
from app.identity.infra.models import PermissionModel


class PermissionCommandRepository(BaseRepository, PermissionCommandRepositoryProtocol):
    model_class = PermissionModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create(self, permission: Permission) -> str:
        model = PermissionMapper.to_model(permission)
        await super().create(model)
        return str(permission.id)

    async def update(self, id: str, permission: Permission) -> str:
        model = PermissionMapper.to_model(permission)
        await self.session.execute(
            update(PermissionModel)
            .where(PermissionModel.id == id)
            .values(
                name=model.name,
            )
        )
        await self.session.flush()
        return id

    async def delete(self, id: str) -> None:
        model = await self.get_by_id(id)
        await super().delete(model)

    async def get_by_id(self, id: str) -> PermissionModel:
        stmt = select(self.model_class).where(self.model_class.id == id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise NotFoundError(f"Permission with id {id} not found")
        return model

from sqlalchemy import select

from app.core.exceptions import NotFoundError
from app.core.infra.repository_base import BaseRepository
from app.identity.domain.entities.user import User
from app.identity.domain.interfaces.user_query_repository_protocol import (
    UserQueryRepositoryProtocol,
)
from app.identity.domain.value_objects import UserID
from app.identity.dto import UserDTO
from app.identity.infra.models.user_model import UserModel


class UserQueryRepository(BaseRepository[UserModel, UserDTO], UserQueryRepositoryProtocol):
    model_class = UserModel

    async def get_by_id(self, id_: str | UserID) -> UserModel:
        # Convert UserID to str for SQLAlchemy comparison
        id_value = str(id_) if isinstance(id_, UserID) else id_
        stmt = select(UserModel).where(UserModel.id == id_value)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise NotFoundError(f"User with id {id_} not found")
        return model

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email.lower())
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return model

    async def exists_by_email(self, email: str) -> bool:
        stmt = select(UserModel.id).where(UserModel.email == email.lower())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

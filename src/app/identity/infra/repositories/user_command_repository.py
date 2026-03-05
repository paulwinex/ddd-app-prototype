from sqlalchemy import select

from app.core.exceptions import NotFoundError
from app.core.infra.repository_base import BaseRepository
from app.identity.api.auth_schemas import LoginRequestSchema
from app.identity.application.security import verify_password
from app.identity.domain.interfaces.user_command_repository_protocol import (
    UserCommandRepositoryProtocol,
)
from app.identity.infra.models.user_model import UserModel


class UserCommandRepository(BaseRepository, UserCommandRepositoryProtocol):
    model_class = UserModel

    async def authenticate_user(self, payload: LoginRequestSchema) -> UserModel:
        stmt = select(UserModel).where(UserModel.email == payload.username.lower())
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()

        if not user_model:
            raise NotFoundError("User not found")

        if not verify_password(payload.password, user_model.password_hash):
            raise NotFoundError("User not found")

        return user_model

from sqlalchemy import select

from app.core.exceptions import NotFoundError
from app.core.infra.repository_base import BaseRepository
from app.identity.api.auth_schemas import LoginRequestSchema
from app.identity.application.security import verify_password
from app.identity.domain.entities import User
from app.identity.domain.exceptions import UserInactiveError, InvalidCredentialsError
from app.identity.domain.interfaces.user_command_repository_protocol import (
    UserCommandRepositoryProtocol,
)
from app.identity.infra.models.user_model import UserModel
from app.identity.application.mappers import UserMapper


class UserCommandRepository(BaseRepository, UserCommandRepositoryProtocol):
    model_class = UserModel

    async def create(self, user: User) -> str:
        model = UserMapper.to_model(user)
        self.session.add(model)
        await self.session.flush([model])
        return model.id

    async def authenticate_user(self, payload: LoginRequestSchema) -> UserModel:
        stmt = select(UserModel).where(UserModel.email == payload.username.lower())
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()

        if not user_model:
            raise InvalidCredentialsError()

        if not verify_password(payload.password, user_model.password_hash):
            raise InvalidCredentialsError()

        if not user_model.is_active:
            raise UserInactiveError()

        return user_model

from typing import Protocol

from pydantic_core.core_schema import TimeSchema

from app.identity.api.auth_schemas import LoginRequestSchema
from app.identity.domain.entities import User
from app.identity.domain.value_objects import UserID
from app.identity.dto.user_dto import UserPasswordChangeRequestDTO
from app.identity.infra.models import UserModel


class UserCommandRepositoryProtocol(Protocol):
    async def create(self, user: User) -> str: ...

    async def update(self, user_id: str | UserID, data: TimeSchema) -> str: ...

    async def delete(self, user_id: str | UserID) -> None: ...

    async def authenticate_user(self, payload: LoginRequestSchema) -> UserModel: ...

    async def change_password(
        self, user_id: str | UserID, payload: UserPasswordChangeRequestDTO
    ) -> None: ...

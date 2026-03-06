from app.identity.api.auth_schemas import LoginRequestSchema
from app.identity.domain.entities import User
from app.identity.domain.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserInactiveError,
)
from app.identity.domain.interfaces import (
    UserCommandRepositoryProtocol,
    UserQueryRepositoryProtocol,
)
from app.identity.domain.interfaces.password_hasher_protocol import PasswordHasherProtocol
from app.identity.domain.value_objects import UserID, EmailVO, PasswordVO
from app.identity.application.dto.user_dto import (
    UserCreateRequestDTO,
    UserUpdateRequestDTO,
    UserPasswordChangeRequestDTO, UserCreateDbDTO,
)
from app.identity.mappers.user_mapper import UserMapper


class UserCommandService:
    """Service for user commands."""

    def __init__(
        self,
        command_repo: UserCommandRepositoryProtocol,
        query_repo: UserQueryRepositoryProtocol,
        password_hasher: PasswordHasherProtocol,
    ):
        self.command_repo = command_repo
        self.query_repo = query_repo
        self.password_hasher = password_hasher

    async def create_user(self, payload: UserCreateRequestDTO) -> str:
        exists = await self.query_repo.exists_by_email(str(payload.email))
        if exists:
            raise UserAlreadyExistsError(f"Email already used {payload.email}")
        payload.password = self.password_hasher.hash(payload.password)
        creation_data = UserCreateDbDTO(
            password_hash=self.password_hasher.hash(payload.password),
            **payload.model_dump(exclude_none=True))
        user_id = await self.command_repo.create(creation_data)
        print('CREATED USER', user_id)
        return user_id

    async def update_user(self, user_id: str | UserID, payload: UserUpdateRequestDTO) -> str:
        user_model = await self.query_repo.get_by_id(user_id)
        user = UserMapper.to_entity(user_model)
        user.update(**payload.model_dump(exclude_unset=True, exclude_none=True))
        await self.command_repo.update(user.id.to_py_value(), UserMapper.to_dto(user))
        return user.id.to_py_value()

    async def delete_user(self, user_id: str | UserID) -> None:
        user = await self.query_repo.get_by_id(user_id)
        if user.is_superuser:
            raise UserInactiveError()
        await self.command_repo.delete(user_id)

    async def authenticate_user(self, payload: LoginRequestSchema) -> User:
        user = await self.query_repo.get_by_email(payload.email)
        if not user:
            raise InvalidCredentialsError()
        if not self.password_hasher.verify(payload.password, str(user.password_hash)):
            raise InvalidCredentialsError()
        if not user.is_active:
            raise UserInactiveError()
        user = UserMapper.to_entity(user)
        user.update_last_login()
        await self.command_repo.update(user)
        return user

    async def change_password(
        self, user_id: str | UserID, payload: UserPasswordChangeRequestDTO
    ) -> None:
        user = await self.query_repo.get_by_id(user_id)
        if not self.password_hasher.verify(payload.current_password, str(user.password_hash)):
            raise InvalidCredentialsError()
        user = UserMapper.to_entity(user)
        new_password = PasswordVO.create_from_raw(payload.new_password, self.password_hasher.hash)
        user.change_password(new_password)
        await self.command_repo.update(user)

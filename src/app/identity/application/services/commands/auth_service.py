from app.identity.api.auth_schemas import (
    LoginRequestSchema,
    TokenResponseSchema,
    RefreshTokenRequestSchema,
)
from app.identity.application import security
from app.identity.domain.entities import User
from app.identity.domain.interfaces import (
    UserQueryRepositoryProtocol,
    UserCommandRepositoryProtocol,
)
from app.identity.domain.value_objects import UserID
from app.identity.dto.user_dto import UserPasswordChangeRequestDTO
from app.identity.exceptions import TokenError
from app.identity.mappers.user_mapper import UserMapper


class AuthService:
    def __init__(
        self,
        user_query_repo: UserQueryRepositoryProtocol,
        user_command_repo: UserCommandRepositoryProtocol,
    ):
        self.user_query_repo = user_query_repo
        self.user_command_repo = user_command_repo

    async def login(self, payload: LoginRequestSchema) -> TokenResponseSchema:
        user_model = await self.user_command_repo.authenticate_user(payload)
        tokens_data = security.create_auth_token(str(user_model.id))
        tokens = TokenResponseSchema(
            access_token=tokens_data["access_token"],
            access_token_expire=tokens_data["access_token_expire"],
            refresh_token=tokens_data["refresh_token"],
            refresh_token_expire=tokens_data["refresh_token_expire"],
        )
        return tokens

    async def refresh_token(self, command: RefreshTokenRequestSchema) -> TokenResponseSchema:
        try:
            tokens_data = security.refresh_access_token(command.refresh_token)
            return TokenResponseSchema(
                access_token=tokens_data["access_token"],
                access_token_expire=tokens_data["access_token_expire"],
                refresh_token=tokens_data["refresh_token"],
                refresh_token_expire=tokens_data["refresh_token_expire"],
            )
        except TokenError:
            # TODO: logs?
            raise
        except Exception as e:
            raise TokenError(detail=f"Invalid refresh token: {str(e)}")

    async def get_current_user(self, token: str) -> User:
        user_id = security.validate_token(token)
        user = await self.user_query_repo.get_by_id(user_id)
        return UserMapper.to_entity(user)

    async def change_password(
        self, user_id: str | UserID, payload: UserPasswordChangeRequestDTO
    ) -> None:
        await self.user_command_repo.change_password(user_id, payload)

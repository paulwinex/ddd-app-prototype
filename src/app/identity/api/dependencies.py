from typing import Annotated

from fastapi import Depends

from app.identity.application.security import oauth2_scheme, get_password_hasher
from app.identity.application.services import AuthService, UserCommandService, UserQueryService
from app.identity.domain.entities import User
from app.identity.domain.interfaces import (
    PasswordHasherProtocol,
    UserCommandRepositoryProtocol,
    UserQueryRepositoryProtocol
)
from app.identity.exceptions import AuthorizationError
from app.identity.infra.dependencies import (
    UserQueryRepoDEP,
    get_user_query_repo,
    get_user_command_repo
)


async def get_user_query_service(
    user_query_repo: UserQueryRepoDEP,
) -> UserQueryService:
    return UserQueryService(user_query_repo)


async def get_user_command_service(
        command_repo: Annotated[UserCommandRepositoryProtocol, Depends(get_user_command_repo)],
        query_repo: Annotated[UserQueryRepositoryProtocol, Depends(get_user_query_repo)],
        password_hasher: Annotated[PasswordHasherProtocol, Depends(get_password_hasher)]
) -> UserCommandService:
    return UserCommandService(command_repo, query_repo, password_hasher)


def get_auth_service(
    user_query_repo: Annotated[UserQueryRepositoryProtocol, Depends(get_user_query_repo)],
    user_command_repo: Annotated[UserCommandRepositoryProtocol, Depends(get_user_command_repo)],
) -> AuthService:
    return AuthService(user_query_repo, user_command_repo)


UserQueryServiceDEP = Annotated[UserQueryService, Depends(get_user_query_service)]
UserCommandServiceDEP = Annotated[UserCommandService, Depends(get_user_command_service)]
AuthServiceDEP = Annotated[AuthService, Depends(get_auth_service)]
OAuthTokenDEP = Annotated[str, Depends(oauth2_scheme)]


async def get_current_active_user(
    auth_service: AuthServiceDEP,
    token: OAuthTokenDEP,
) -> User:
    user = await auth_service.get_current_user(token)
    if not user.is_active:
        raise AuthorizationError(detail="User account is inactive")
    return user


CurrentUserDEP = Annotated[User, Depends(get_current_active_user)]


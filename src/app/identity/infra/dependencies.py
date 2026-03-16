from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import get_async_session
from app.identity.infra.repositories import (
    UserCommandRepository,
    UserQueryRepository,
    GroupCommandRepository,
    GroupQueryRepository,
    PermissionCommandRepository,
    PermissionQueryRepository,
)


def get_user_query_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserQueryRepository:
    return UserQueryRepository(session)


def get_user_command_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserCommandRepository:
    return UserCommandRepository(session)


def get_group_query_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> GroupQueryRepository:
    return GroupQueryRepository(session)


def get_group_command_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> GroupCommandRepository:
    return GroupCommandRepository(session)


def get_permission_query_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> PermissionQueryRepository:
    return PermissionQueryRepository(session)


def get_permission_command_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> PermissionCommandRepository:
    return PermissionCommandRepository(session)


UserQueryRepoDEP = Annotated[UserQueryRepository, Depends(get_user_query_repo)]
UserCommandRepoDEP = Annotated[UserCommandRepository, Depends(get_user_command_repo)]
GroupQueryRepoDEP = Annotated[GroupQueryRepository, Depends(get_group_query_repo)]
GroupCommandRepoDEP = Annotated[GroupCommandRepository, Depends(get_group_command_repo)]
PermissionQueryRepoDEP = Annotated[PermissionQueryRepository, Depends(get_permission_query_repo)]
PermissionCommandRepoDEP = Annotated[
    PermissionCommandRepository, Depends(get_permission_command_repo)
]

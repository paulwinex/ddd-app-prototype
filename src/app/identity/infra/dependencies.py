from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import get_async_session
from app.identity.infra.repositories.user_command_repository import UserCommandRepository
from app.identity.infra.repositories.user_query_repository import UserQueryRepository


def get_user_query_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserQueryRepository:
    return UserQueryRepository(session)


def get_user_command_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserCommandRepository:
    return UserCommandRepository(session)


UserQueryRepoDEP = Annotated[UserQueryRepository, Depends(get_user_query_repo)]
UserCommandRepoDEP = Annotated[UserCommandRepository, Depends(get_user_command_repo)]

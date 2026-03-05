from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .session import get_async_session


def get_async_session_dep() -> AsyncGenerator[AsyncSession, None]:
    return get_async_session()


AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session_dep)]

from typing import Any, Protocol
from uuid import UUID

from app.core.infra.quary_params import OffsetPaginateQueryParams
from app.identity.domain.value_objects import UserID, EmailVO
from app.identity.infra.models import UserModel


class UserQueryRepositoryProtocol(Protocol):
    async def get_by_id(self, user_id: str | UserID) -> UserModel: ...

    async def get_by_email(self, email: str | EmailVO) -> UserModel | None: ...

    async def get_list(
        self,
        pagination: OffsetPaginateQueryParams | None = None,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[UserModel], int]:
        """Return items and total count"""
        ...

    async def count(self, filters: dict[str, Any] | None = None) -> int: ...

    async def exists(self, user_id: str | UUID | UserID) -> bool: ...

    async def exists_by_email(self, email: str | EmailVO) -> bool: ...

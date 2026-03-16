from typing import Any, Protocol

from app.core.infra.pagination import OffsetPaginationRequest, OffsetPaginationResult
from app.identity.domain.entities import Group
from app.identity.domain.value_objects import GroupID


class GroupQueryRepositoryProtocol(Protocol):
    """Protocol for group query repository (read operations)."""

    async def get_by_id(
        self,
        id_: str | GroupID,
        load_members: bool = False,
        load_permissions: bool = False,
    ) -> Group: ...

    async def get_by_name(
        self,
        name: str,
        load_members: bool = False,
        load_permissions: bool = False,
    ) -> Group | None: ...

    async def get_list(
        self,
        pagination: OffsetPaginationRequest | None = None,
        filters: dict[str, Any] | None = None,
    ) -> OffsetPaginationResult[Group]: ...

    async def count(self, filters: dict[str, Any] | None = None) -> int: ...

    async def exists(self, id_: str) -> bool: ...

    async def user_in_group(self, user_id: str, group_id: str) -> bool: ...

    async def get_user_groups(self, user_id: str) -> list[Group]: ...

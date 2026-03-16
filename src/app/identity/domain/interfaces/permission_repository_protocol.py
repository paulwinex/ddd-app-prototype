from typing import Any, Protocol

from app.core.infra.pagination import OffsetPaginationRequest, OffsetPaginationResult
from app.identity.domain.entities import Permission
from app.identity.domain.value_objects import PermissionID


class PermissionQueryRepositoryProtocol(Protocol):
    """Protocol for permission query repository (read operations)."""

    async def get_by_id(self, id_: str | PermissionID) -> Permission: ...

    async def get_by_codename(self, codename: str) -> Permission | None: ...

    async def get_list(
        self,
        pagination: OffsetPaginationRequest | None = None,
        filters: dict[str, Any] | None = None,
    ) -> OffsetPaginationResult[Permission]: ...

    async def count(self, filters: dict[str, Any] | None = None) -> int: ...

    async def exists(self, id_: str) -> bool: ...


class PermissionCommandRepositoryProtocol(Protocol):
    """Protocol for permission command repository (write operations)."""

    async def create(self, permission: Permission) -> str: ...

    async def update(self, id: str, permission: Permission) -> str: ...

    async def delete(self, id: str) -> None: ...

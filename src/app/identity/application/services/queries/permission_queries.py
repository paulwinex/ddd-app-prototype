from dataclasses import dataclass

from app.core.infra.quary_params import OffsetPaginateQueryParams
from app.core.infra.pagination import OffsetPaginationRequest
from app.identity.domain.interfaces import PermissionQueryRepositoryProtocol
from app.identity.domain.value_objects import PermissionID
from app.identity.application.mappers import PermissionMapper
from app.identity.application.dto import PermissionDTO, PermissionResponseDTO


@dataclass
class PermissionListResult:
    items: list[PermissionResponseDTO]
    total: int
    has_next: bool
    has_prev: bool
    limit: int
    offset: int
    order_by: str | None = "id"
    sorting: str = "asc"


class PermissionQueryService:
    def __init__(self, query_repo: PermissionQueryRepositoryProtocol):
        self.query_repo = query_repo

    async def get_permission_by_id(self, permission_id: str | PermissionID) -> PermissionDTO:
        permission = await self.query_repo.get_by_id(permission_id)
        return PermissionMapper.to_dto(permission)

    async def get_permission_by_codename(self, codename: str) -> PermissionDTO | None:
        permission = await self.query_repo.get_by_codename(codename)
        if not permission:
            return None
        return PermissionMapper.to_dto(permission)

    async def get_permission_list(
        self,
        pagination: OffsetPaginateQueryParams,
        filters: dict | None = None,
    ) -> PermissionListResult:
        pagination_request = OffsetPaginationRequest(
            limit=pagination.limit,
            offset=pagination.offset,
            order_by=pagination.order_by,
            sorting=pagination.sorting,
        )
        result = await self.query_repo.get_list(pagination=pagination_request, filters=filters)
        items = [PermissionMapper.to_dto(permission) for permission in result.items]
        return PermissionListResult(
            items=items,
            total=result.total,
            limit=result.limit,
            offset=result.offset,
            has_next=result.has_next,
            has_prev=result.has_prev,
            order_by=result.order_by,
            sorting=pagination.sorting,
        )

    async def permission_exists(self, permission_id: str) -> bool:
        return await self.query_repo.exists(permission_id)

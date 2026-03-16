from dataclasses import dataclass
from typing import Any

from app.core.infra.quary_params import OffsetPaginateQueryParams
from app.identity.domain.interfaces import GroupQueryRepositoryProtocol
from app.identity.domain.value_objects import GroupID
from app.identity.application.mappers import GroupMapper
from app.identity.application.dto import GroupDTO, GroupResponseDTO


@dataclass
class GroupListResult:
    items: list[GroupResponseDTO]
    total: int
    has_next: bool
    has_prev: bool
    limit: int
    offset: int
    order_by: str | None = "id"
    sorting: str = "asc"


class GroupQueryService:
    def __init__(self, query_repo: GroupQueryRepositoryProtocol):
        self.query_repo = query_repo

    async def user_in_group(self, user_id: str, group_id: str) -> bool:
        return await self.query_repo.user_in_group(user_id, group_id)

    async def get_group_by_id(
        self,
        group_id: str | GroupID,
        load_members: bool = False,
        load_permissions: bool = False,
    ) -> GroupDTO:
        group = await self.query_repo.get_by_id(
            group_id,
            load_members=load_members,
            load_permissions=load_permissions,
        )
        return GroupMapper.to_dto(group)

    async def get_group_by_name(
        self,
        name: str,
        load_members: bool = False,
        load_permissions: bool = False,
    ) -> GroupDTO | None:
        group = await self.query_repo.get_by_name(
            name,
            load_members=load_members,
            load_permissions=load_permissions,
        )
        if not group:
            return None
        return GroupMapper.to_dto(group)

    async def get_group_list(
        self,
        pagination: OffsetPaginateQueryParams,
        filters: dict[str, Any] | None = None,
    ) -> GroupListResult:
        result = await self.query_repo.get_list(pagination=pagination, filters=filters)
        items = [GroupMapper.to_dto(group) for group in result.items]
        return GroupListResult(
            items=items,
            total=result.total,
            limit=result.limit,
            offset=result.offset,
            has_next=result.has_next,
            has_prev=result.has_prev,
            order_by=result.order_by,
            sorting=pagination.sorting,
        )

    async def group_exists(self, group_id: str) -> bool:
        return await self.query_repo.exists(group_id)

    async def get_user_groups(self, user_id: str) -> list[GroupDTO]:
        groups = await self.query_repo.get_user_groups(user_id)
        return [GroupMapper.to_dto(group) for group in groups]

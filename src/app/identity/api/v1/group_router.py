from fastapi import APIRouter, Depends, status
from typing import Annotated

from app.core.infra.quary_params import OffsetPaginateQueryParams
from app.identity.api.dependencies import (
    GroupQueryServiceDEP,
    GroupCommandServiceDEP,
)
from app.identity.application.dto import (
    GroupCreateRequestDTO,
    GroupUpdateRequestDTO,
    GroupDTO,
    GroupListResponseDTO,
)
from app.identity.application.services.commands.group_commands import GroupCommandService
from app.identity.application.services.queries.group_queries import GroupQueryService
from app.identity.domain.permissions import GroupPermission
from app.identity.api.permission_dependencies import has_permissions

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.get(
    "",
    response_model=GroupListResponseDTO,
    dependencies=[Depends(has_permissions([GroupPermission.CAN_LIST_GROUPS]))],
)
async def list_groups(
    pagination: Annotated[OffsetPaginateQueryParams, Depends()],
    group_query_service: GroupQueryServiceDEP,
) -> GroupListResponseDTO:
    """List groups with pagination and filters."""
    filters = {}
    if pagination.name:
        filters["name"] = pagination.name
    if pagination.is_system is not None:
        filters["is_system"] = pagination.is_system

    from app.core.infra.pagination import OffsetPaginationRequest

    pagination_params = OffsetPaginationRequest(
        limit=pagination.limit,
        offset=pagination.offset,
        order_by=pagination.order_by,
    )

    result = await group_query_service.get_group_list(
        pagination=pagination_params,
        filters=filters if filters else None,
    )

    return GroupListResponseDTO(
        items=result.items,  # type: ignore[arg-type]
        total=result.total,
        limit=result.limit,
        offset=result.offset,
        has_next=result.has_next,
        has_prev=result.has_prev,
    )


@router.get(
    "/{group_id}",
    response_model=GroupDTO,
    dependencies=[Depends(has_permissions([GroupPermission.CAN_VIEW_GROUP]))],
)
async def get_group(
    group_id: str,
    group_query_service: GroupQueryServiceDEP,
) -> GroupDTO:
    """Get group by ID."""
    return await group_query_service.get_group_by_id(group_id)


@router.post(
    "",
    response_model=GroupDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_permissions([GroupPermission.CAN_ADD_GROUP]))],
)
async def create_group(
    request: GroupCreateRequestDTO,
    group_command_service: GroupCommandServiceDEP,
    group_query_service: GroupQueryServiceDEP,
) -> GroupDTO:
    """Create a new group."""
    group_id = await group_command_service.create_group(request)
    return await group_query_service.get_group_by_id(group_id)


@router.patch(
    "/{group_id}",
    response_model=GroupDTO,
    dependencies=[Depends(has_permissions([GroupPermission.CAN_EDIT_GROUP]))],
)
async def update_group(
    group_id: str,
    request: GroupUpdateRequestDTO,
    group_command_service: GroupCommandServiceDEP,
    group_query_service: GroupQueryServiceDEP,
) -> GroupDTO:
    """Update group."""
    await group_command_service.update_group(group_id, request)
    return await group_query_service.get_group_by_id(group_id)


@router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(has_permissions([GroupPermission.CAN_DELETE_GROUP]))],
)
async def delete_group(
    group_id: str,
    group_command_service: GroupCommandServiceDEP,
) -> None:
    """Delete group."""
    await group_command_service.delete_group(group_id)


@router.post(
    "/{group_id}/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(has_permissions([GroupPermission.CAN_MANAGE_GROUP_USERS]))],
)
async def add_user_to_group(
    group_id: str,
    user_id: str,
    group_command_service: GroupCommandServiceDEP,
) -> None:
    """Add user to group."""
    await group_command_service.add_user_to_group(user_id, group_id)


@router.delete(
    "/{group_id}/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(has_permissions([GroupPermission.CAN_MANAGE_GROUP_USERS]))],
)
async def remove_user_from_group(
    group_id: str,
    user_id: str,
    group_command_service: GroupCommandServiceDEP,
) -> None:
    """Remove user from group."""
    await group_command_service.remove_user_from_group(user_id, group_id)

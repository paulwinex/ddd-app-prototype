from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.infra.quary_params import OffsetPaginateQueryParams
from app.identity.api.dependencies import (
    GroupQueryServiceDEP,
    GroupCommandServiceDEP,
    CurrentUserDEP,
)
from app.identity.api.permission_dependencies import has_permissions
from app.identity.api.query_params import GroupListQueryParams
from app.identity.application.dto import (
    GroupCreateRequestDTO,
    GroupUpdateRequestDTO,
    GroupDTO,
    GroupListResponseDTO,
)
from app.identity.domain.permissions import GroupPermission

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.get(
    "",
    response_model=GroupListResponseDTO,
    dependencies=[Depends(has_permissions([GroupPermission.CAN_LIST_GROUPS]))],
)
async def list_groups(
    pagination_params: Annotated[OffsetPaginateQueryParams, Depends()],
    params: Annotated[GroupListQueryParams, Depends()],
    group_query_service: GroupQueryServiceDEP,
) -> GroupListResponseDTO:
    result = await group_query_service.get_group_list(
        pagination=pagination_params,
        filters=params.model_dump(exclude_unset=True),
    )
    return GroupListResponseDTO.model_validate(result)


@router.get(
    "/{group_id}",
    response_model=GroupDTO,
    dependencies=[Depends(has_permissions([GroupPermission.CAN_VIEW_GROUP]))],
)
async def get_group(
    group_id: str,
    group_query_service: GroupQueryServiceDEP,
) -> GroupDTO:
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
    await group_command_service.remove_user_from_group(user_id, group_id)


@router.get(
    "/users/{user_id}/groups",
    response_model=GroupListResponseDTO,
)
async def list_user_groups(
    user_id: str,
    group_query_service: GroupQueryServiceDEP,
) -> GroupListResponseDTO:
    groups = await group_query_service.get_user_groups(user_id)
    return GroupListResponseDTO(
        items=groups,
        total=len(groups),
        limit=len(groups),
        offset=0,
        has_next=False,
        has_prev=False,
    )


@router.get(
    "/me/groups",
    response_model=GroupListResponseDTO,
)
async def list_my_groups(
    current_user: CurrentUserDEP,
    group_query_service: GroupQueryServiceDEP,
) -> GroupListResponseDTO:
    groups = await group_query_service.get_user_groups(str(current_user.id))
    return GroupListResponseDTO(
        items=groups,
        total=len(groups),
        limit=len(groups),
        offset=0,
        has_next=False,
        has_prev=False,
    )

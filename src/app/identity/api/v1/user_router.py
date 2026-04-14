from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.identity.api.dependencies import UserQueryServiceDEP, UserCommandServiceDEP
from app.identity.api.query_params import UserListQueryParams
from app.identity.application.dto.user_dto import (
    UserListResponseDTO,
    UserResponseDTO,
    UserCreateRequestDTO,
    UserUpdateRequestDTO,
)
from app.identity.domain.permissions import UserPermission
from app.identity.api.permission_dependencies import has_permissions

router = APIRouter()


@router.get(
    "",
    response_model=UserListResponseDTO,
    dependencies=[Depends(has_permissions([UserPermission.CAN_LIST_USERS]))],
)
async def list_users(
    params: Annotated[UserListQueryParams, Depends()],
    user_query_service: UserQueryServiceDEP,
) -> UserListResponseDTO:
    return await user_query_service.get_user_list(
        pagination=params,
        filters=params.model_dump(exclude_unset=True),
    )


@router.get(
    "/{user_id}",
    response_model=UserResponseDTO,
    dependencies=[Depends(has_permissions([UserPermission.CAN_VIEW_USER]))],
)
async def get_user(
    user_id: str,
    user_query_service: UserQueryServiceDEP,
) -> UserResponseDTO:
    return await user_query_service.get_user_by_id(user_id)


@router.post(
    "",
    response_model=UserResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_permissions([UserPermission.CAN_ADD_USER]))],
)
async def create_user(
    request: UserCreateRequestDTO,
    user_command_service: UserCommandServiceDEP,
    user_query_service: UserQueryServiceDEP,
) -> UserResponseDTO:
    user_id = await user_command_service.create_user(request)
    return await user_query_service.get_user_by_id(user_id)


@router.patch(
    "/{user_id}",
    dependencies=[Depends(has_permissions([UserPermission.CAN_EDIT_USER]))],
)
async def update_user(
    user_id: str,
    request: UserUpdateRequestDTO,
    user_command_service: UserCommandServiceDEP,
) -> str:
    return await user_command_service.update_user(user_id, request)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(has_permissions([UserPermission.CAN_DELETE_USER]))],
)
async def delete_user(
    user_id: str,
    user_command_service: UserCommandServiceDEP,
) -> None:
    await user_command_service.delete_user(user_id)



from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.infra.quary_params import OffsetPaginateQueryParams
from app.identity.api.dependencies import UserQueryServiceDEP, UserCommandServiceDEP
from app.identity.api.query_params import UserListQueryParams
from app.identity.dto.user_dto import UserListResponseDTO, UserResponseDTO, UserCreateRequestDTO, UserUpdateRequestDTO, \
    UserPasswordChangeRequestDTO

router = APIRouter()


@router.get("", response_model=UserListResponseDTO)
async def list_users(
    pagination: Annotated[OffsetPaginateQueryParams, Depends()],
    filters: Annotated[UserListQueryParams, Depends()],
    user_query_service: UserQueryServiceDEP,
) -> UserListResponseDTO:

    return await user_query_service.get_user_list(filters, pagination)


@router.get("/{user_id}", response_model=UserResponseDTO)
async def get_user(
    user_id: str,
    user_query_service: UserQueryServiceDEP,
) -> UserResponseDTO:
    return await user_query_service.get_user_by_id(user_id)


@router.post("", response_model=UserResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreateRequestDTO,
    user_command_service: UserCommandServiceDEP,
    user_query_service: UserQueryServiceDEP,
) -> UserResponseDTO:
    user_id = await user_command_service.create_user(request)
    return await user_query_service.get_user_by_id(user_id)


@router.patch("/{user_id}")
async def update_user(
    user_id: str,
    request: UserUpdateRequestDTO,
    user_command_service: UserCommandServiceDEP,
) -> str:
    return await user_command_service.update_user(user_id, request)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    user_command_service: UserCommandServiceDEP,
) -> None:
    await user_command_service.delete_user(user_id)


@router.post("/{user_id}/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user_id: str,
    request: UserPasswordChangeRequestDTO,
    user_command_service: UserCommandServiceDEP,
) -> None:
    await user_command_service.change_password(user_id, request)

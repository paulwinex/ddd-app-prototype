from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from app.core.infra.quary_params import OffsetPaginateQueryParams
from app.identity.api.dependencies import PermissionQueryServiceDEP
from app.identity.application.dto import PermissionDTO, PermissionListResponseDTO
from app.identity.api.query_params import PermissionListQueryParams
from app.identity.application.services.queries.permission_queries import PermissionQueryService
from app.identity.domain.permissions import PermissionPermission
from app.identity.api.permission_dependencies import has_permissions

router = APIRouter()


@router.get(
    "",
    response_model=PermissionListResponseDTO,
    dependencies=[Depends(has_permissions([PermissionPermission.CAN_LIST_PERMISSIONS]))],
)
async def list_permissions(
    pagination_params: Annotated[OffsetPaginateQueryParams, Depends()],
    params: Annotated[PermissionListQueryParams, Depends()],
    permission_query_service: PermissionQueryServiceDEP,
) -> PermissionListResponseDTO:
    result = await permission_query_service.get_permission_list(
        pagination=pagination_params,
        filters=params.model_dump(exclude_unset=True),
    )
    return PermissionListResponseDTO(
        items=result.items,
        total=result.total,
        limit=result.limit,
        offset=result.offset,
        has_next=result.has_next,
        has_prev=result.has_prev,
    )


@router.get(
    "/{permission_id}",
    response_model=PermissionDTO,
    dependencies=[Depends(has_permissions([PermissionPermission.CAN_VIEW_PERMISSION]))],
)
async def get_permission(
    permission_id: str,
    permission_query_service: PermissionQueryServiceDEP,
) -> PermissionDTO:
    return await permission_query_service.get_permission_by_id(permission_id)


@router.get(
    "/codename/{codename}",
    response_model=PermissionDTO,
    dependencies=[Depends(has_permissions([PermissionPermission.CAN_VIEW_PERMISSION]))],
)
async def get_permission_by_codename(
    codename: str,
    permission_query_service: PermissionQueryServiceDEP,
) -> PermissionDTO:
    permission = await permission_query_service.get_permission_by_codename(codename)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission

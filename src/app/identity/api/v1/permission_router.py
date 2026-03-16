from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from app.core.infra.quary_params import OffsetPaginateQueryParams
from app.identity.api.dependencies import PermissionQueryServiceDEP
from app.identity.application.dto import PermissionDTO, PermissionListResponseDTO
from app.identity.application.services.queries.permission_queries import PermissionQueryService
from app.identity.domain.permissions import PermissionPermission
from app.identity.api.permission_dependencies import has_permissions

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.get(
    "",
    response_model=PermissionListResponseDTO,
    dependencies=[Depends(has_permissions([PermissionPermission.CAN_LIST_PERMISSIONS]))],
)
async def list_permissions(
    pagination: Annotated[OffsetPaginateQueryParams, Depends()],
    permission_query_service: PermissionQueryServiceDEP,
) -> PermissionListResponseDTO:
    """List permissions with pagination."""
    from app.core.infra.pagination import OffsetPaginationRequest

    pagination_params = OffsetPaginationRequest(
        limit=pagination.limit,
        offset=pagination.offset,
        order_by=pagination.order_by,
    )

    result = await permission_query_service.get_permission_list(pagination=pagination_params)

    return PermissionListResponseDTO(
        items=result.items,  # type: ignore[arg-type]
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
    """Get permission by ID."""
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
    """Get permission by codename."""
    permission = await permission_query_service.get_permission_by_codename(codename)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission

from typing import Optional

from fastapi import Query
from pydantic import BaseModel

from app.core.infra.quary_params import OffsetPaginateQueryParams


class UserListQueryParams(OffsetPaginateQueryParams):
    email: Optional[str] = Query(None, description="Filter by email")
    is_active: Optional[bool] = Query(None, description="Filter by active status")
    is_superuser: Optional[bool] = Query(None, description="Filter by superuser status")
    is_verified: Optional[bool] = Query(None, description="Filter by verified status")


class GroupListQueryParams(BaseModel):
    name: Optional[str] = Query(None, description="Filter by group name")
    is_system: Optional[bool] = Query(None, description="Filter by system status")


class PermissionListQueryParams(OffsetPaginateQueryParams):
    name: Optional[str] = Query(None, description="Filter by permission name")
    codename: Optional[str] = Query(None, description="Filter by permission codename")

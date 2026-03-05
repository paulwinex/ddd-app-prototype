from typing import Optional

from fastapi import Query
from pydantic import BaseModel


class UserListQueryParams(BaseModel):
    email: Optional[str] = Query(None, description="Filter by email")
    is_active: Optional[bool] = Query(None, description="Filter by active status")
    is_superuser: Optional[bool] = Query(None, description="Filter by superuser status")
    is_verified: Optional[bool] = Query(None, description="Filter by verified status")


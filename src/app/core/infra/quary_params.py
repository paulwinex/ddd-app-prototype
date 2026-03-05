from typing import Optional

from fastapi import Query
from pydantic import BaseModel


class BaseQueryParams(BaseModel):
    id: Optional[str] = Query(None, description="Filter by id")


class SortOrderQueryParams(BaseQueryParams):
    order_by: Optional[str] = Query("id", description="Order by field (default: id)")
    sorting: Optional[str] = Query("asc", description="Sorting direction (default: asc)")

    @property
    def is_desc(self):
        return self.order_by == "desc"


class OffsetPaginateQueryParams(SortOrderQueryParams):
    limit: int = Query(50, ge=1, le=1000, description="Items count limit")
    offset: int = Query(0, ge=0, description="Items offset")

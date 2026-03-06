from dataclasses import dataclass
from typing import Generic, Any

from pydantic import BaseModel

from app.core.type_aliases import TModelORM


@dataclass
class OffsetPaginationRequest(Generic[TModelORM]):
    limit: int = 50
    offset: int = 0
    order_by: str = None
    sorting: str = "asc"

    def is_desc(self):
        return self.sorting == "desc"

    def to_dict(self) -> dict[str, Any]:
        return {
            "limit": self.limit,
            "offset": self.offset,
            "sort_by": self.sorting,
            "order_by": self.order_by,
        }


@dataclass
class OffsetPaginationResult(Generic[TModelORM]):
    items: list[TModelORM]
    total: int
    has_next: bool
    has_prev: bool

    limit: int
    offset: int
    order_by: str
    sorting: str

    def is_desc(self):
        return self.sorting == "desc"

    def to_dict(self) -> dict[str, Any]:
        return {
            "items": self.items,
            "total": self.total,
            "limit": self.limit,
            "offset": self.offset,
            "sort_by": self.sorting,
            "order_by": self.order_by,
            "has_next": self.has_next,
            "has_prev": self.has_prev,
        }


class OffsetPaginationResultSchema(BaseModel):
    total: int
    has_next: bool
    has_prev: bool
    limit: int
    offset: int
    order_by: str = "id"
    sorting: str = "asc"
from typing import TypeVar, Protocol
from uuid import UUID

from pydantic import BaseModel

from app.core.infra.base_model import Base

TEntity = TypeVar("TEntity", bound="EntityBase")
TModelORM = TypeVar("TModelORM", bound=Base)
TDTO = TypeVar("TDTO", bound="DtoBase")
TSchema = TypeVar("TSchema", bound="BaseModel")


UUIDv7 = UUID


class SupportsID(Protocol):
    id: UUIDv7


class EntityBase(Protocol):
    id: UUIDv7

    def to_dict(self) -> dict:
        ...


class DtoBase(Protocol):
    model_config: dict


class PaginationResult(Protocol[TModelORM]):
    items: list[TModelORM]
    total: int
    limit: int
    offset: int
    has_next: bool
    has_prev: bool


Cursor = str

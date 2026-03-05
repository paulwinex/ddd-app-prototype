from abc import ABC
from typing import Any, Generic, Protocol
from uuid import UUID

from sqlalchemy import Select, select, func, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.infra.pagination import OffsetPaginationResult, OffsetPaginationRequest
from app.core.type_aliases import TModelORM, PaginationResult, TDTO, TSchema


class QueryRepositoryProtocol(Protocol[TModelORM, TDTO]):
    """Protocol for query repositories (read operations)"""

    async def get_by_id(self, id_: str) -> TModelORM:
        ...

    async def get_list(
        self,
        pagination: OffsetPaginationRequest | None = None,
        filters: dict[str, Any] | None = None,
    ) -> PaginationResult[TModelORM]:
        ...

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        ...

    async def exists(self, id_: str) -> bool:
        ...


class CommandRepositoryProtocol(Protocol[TDTO]):
    """Protocol for command repositories (write operations)"""

    async def create(self, entity: TDTO) -> str:
        ...

    async def update(self, id_: str, entity: TDTO) -> str:
        ...

    async def delete(self, id_: str) -> None:
        ...

    async def bulk_create(self, entities: list[TDTO]) -> list[str]:
        ...

    async def bulk_update(self, entities: list[TDTO]) -> list[str]:
        ...

    async def bulk_delete(self, ids: list[str|UUID]) -> int:
        ...


class BaseRepository(ABC, Generic[TModelORM, TDTO]):
    """Base repository with common CRUD operations."""
    model_class: type[TModelORM]

    def __init__(self, session: AsyncSession):
        if self.model_class is None:
            raise NotImplementedError("model_class must be set")
        self.session = session

    def _apply_filters(self, stmt: Select, filters: dict[str, Any] | None) -> Select:
        """Apply filters to query statement."""
        if not filters or not self.model_class:
            return stmt

        for field, value in filters.items():
            if hasattr(self.model_class, field):
                column = getattr(self.model_class, field)
                if value is None:
                    stmt = stmt.where(column.is_(None))
                elif isinstance(value, (list, tuple)):
                    stmt = stmt.where(column.in_(value))
                elif isinstance(value, dict):
                    # Support operators like {"gt": 5, "lt": 10}
                    for op, val in value.items():
                        if op == "gt":
                            stmt = stmt.where(column > val)
                        elif op == "gte":
                            stmt = stmt.where(column >= val)
                        elif op == "lt":
                            stmt = stmt.where(column < val)
                        elif op == "lte":
                            stmt = stmt.where(column <= val)
                        elif op == "ne":
                            stmt = stmt.where(column != val)
                        elif op == "like":
                            stmt = stmt.where(column.like(val))
                        elif op == "ilike":
                            stmt = stmt.where(column.ilike(val))
                        elif op == "in":
                            stmt = stmt.where(column.in_(val))
                else:
                    stmt = stmt.where(column == value)
        return stmt

    def _apply_ordering(self, stmt: Select, pagination: OffsetPaginationRequest) -> Select:
        order_field = pagination.order_by or 'id'
        order_column = getattr(self.model_class, order_field, None)
        if pagination.is_desc:
            return stmt.order_by(order_column.desc())
        return stmt.order_by(order_column.asc())

    async def _count_query(self, filters: dict[str, Any] | None = None) -> int:
        stmt = select(func.count()).select_from(self.model_class)
        stmt = self._apply_filters(stmt, filters)
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def get_by_id(self, id_: str|UUID) -> TModelORM:
        stmt = select(self.model_class).where(self.model_class.id == id_)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise NotFoundError(f"{self.model_class.__name__} with id {id_} not found")
        return model

    async def get_list(
        self,
        pagination: OffsetPaginationRequest | None = None,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[TModelORM], int]:
        if pagination is None:
            pagination = OffsetPaginationRequest()
        filters = {k: v for k, v in filters.items() if v is not None}
        total = await self._count_query(filters)
        stmt = select(self.model_class)
        stmt = self._apply_filters(stmt, filters)
        stmt = self._apply_ordering(stmt, pagination)
        stmt = stmt.offset(pagination.offset).limit(pagination.limit)
        result = await self.session.execute(stmt)
        models = list(result.scalars().all())
        return  models, total

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        return await self._count_query(filters)

    async def exists(self, id_: str|UUID) -> bool:
        try:
            await self.get_by_id(id_)
            return True
        except NotFoundError:
            return False

    async def create(self, payload: TSchema) -> TModelORM:
        model = self.model_class(**payload.model_dump(exclude_unset=True))
        self.session.add(model)
        await self.session.flush(model)
        return model

    async def update(self, entity_id: str, data: TSchema) -> None:
        stmt = (update(self.model_class)
            .where(self.model_class.id == entity_id)
            .values(**data.model_dump(exclude_unset=True))
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def delete(self, entity_id: str|UUID) -> None:
        stmt = delete(self.model_class).where(self.model_class.id == entity_id)
        await self.session.delete(stmt)

    async def bulk_create(self, models: list[TModelORM]) -> list[TModelORM]:
        raise NotImplementedError
        self.session.add_all(models)
        await self.session.flush()
        return models

    async def bulk_delete(self, models: list[TModelORM]) -> int:
        raise NotImplementedError
        count = len(models)
        for model in models:
            await self.session.delete(model)
        return count

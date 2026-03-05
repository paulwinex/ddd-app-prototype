from typing import Protocol, TypeVar
from .type_aliases import TEntity, TModelORM, TDTO


class Mapper(Protocol):
    @staticmethod
    def to_entity(model: TModelORM) -> TEntity:
        ...

    @staticmethod
    def to_model(entity: TEntity) -> TModelORM:
        ...

    @staticmethod
    def to_dto(entity: TEntity|TModelORM) -> TDTO:
        ...


TMapper = TypeVar("TMapper", bound="Mapper")

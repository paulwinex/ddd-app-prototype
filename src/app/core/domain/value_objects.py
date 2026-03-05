from dataclasses import dataclass, field
from uuid import UUID, uuid7

from .value_object_base import ValueObjectBase
from ..exceptions import ValueObjectValidationError


@dataclass(frozen=True, slots=True)
class EntityID(ValueObjectBase):
    """Base value object for entity IDs using UUIDv7.
    All entity ID value objects should inherit from this class.
    """

    value: str | UUID = field(default_factory=uuid7)

    def __post_init__(self) -> None:
        try:
            UUID(str(self.value), version=7)
        except ValueError:
            raise ValueObjectValidationError("Invalid UUID format")

    def to_py_value(self) -> str:
        return str(self.value)

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.value}')"

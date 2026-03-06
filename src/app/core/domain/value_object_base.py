from abc import ABC, abstractmethod
from typing import Any


class ValueObjectBase(ABC):
    """Base class for all value objects"""

    @abstractmethod
    def to_py_value(self) -> Any: ...

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ValueObjectBase):
            return NotImplemented
        return self.to_py_value() == other.to_py_value()

    def __hash__(self) -> int:
        return hash(self.to_py_value())

    def __str__(self) -> str:
        return str(self.to_py_value())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.to_py_value()!r})"

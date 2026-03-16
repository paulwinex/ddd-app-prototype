from dataclasses import dataclass
from typing import Self

from pydantic import EmailStr

from app.core.domain.value_object_base import ValueObjectBase
from app.core.domain.value_objects import EntityID
from app.core.exceptions import ValueObjectValidationError


@dataclass(frozen=True, slots=True)
class UserID(EntityID):
    pass


@dataclass(frozen=True, slots=True)
class GroupID(EntityID):
    pass


@dataclass(frozen=True, slots=True)
class PermissionID(EntityID):
    pass


@dataclass(frozen=True, slots=True)
class EmailVO(ValueObjectBase):
    value: str

    def __post_init__(self) -> None:
        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, self.value):
            raise ValueObjectValidationError("Invalid email format")

    @classmethod
    def create(cls, value: str | EmailStr) -> Self:
        return cls(value=value.lower().strip())

    def to_py_value(self) -> str:
        return self.value

    @property
    def domain(self) -> str:
        return self.value.split("@")[1]

    @property
    def username(self) -> str:
        return self.value.split("@")[0]

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class PasswordVO(ValueObjectBase):
    value: str

    def __post_init__(self) -> None:
        if not self.value.startswith("$"):
            raise ValueObjectValidationError("Password must be hashed")

    @classmethod
    def create_from_raw(cls, raw_password: str, hash_function) -> Self:
        return cls(value=hash_function(raw_password))

    def to_py_value(self) -> str:
        return self.value

    def verify(self, raw_password: str, verify_function) -> bool:
        return verify_function(raw_password, self.value)

    def __str__(self) -> str:
        return "[REDACTED]"

    def __repr__(self) -> str:
        return "PasswordVO('[REDACTED]')"

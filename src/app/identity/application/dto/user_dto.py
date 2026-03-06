from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_serializer

from app.core.infra.pagination import OffsetPaginationResultSchema
from app.identity.domain.value_objects import UserID, EmailVO


class UserDTOBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserResponseDTO(UserDTOBase):
    id: str | UserID
    email: str | EmailVO
    first_name: str | None = None
    last_name: str | None = None

    @field_serializer("id", when_used="json")
    def serialize_id(self, value: Any) -> str:
        if isinstance(value, UserID):
            return str(value)
        return value

    @field_serializer("email", when_used="json")
    def serialize_email(self, value: Any) -> str:
        if isinstance(value, EmailVO):
            return value.to_py_value()
        return value


class UserFullResponseDTO(UserResponseDTO):
    created_at: datetime
    updated_at: datetime | None = None
    last_login_at: datetime | None = None


class UserAdminResponseDTO(UserFullResponseDTO):
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserDTO(UserAdminResponseDTO):
    pass


class UserCreateRequestDTO(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)


class UserCreateDbDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str
    password_hash: str
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)


class UserUpdateRequestDTO(UserDTOBase):
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)


class UserAdminUpdateRequestDTO(UserUpdateRequestDTO):
    email: EmailStr | None = None
    is_active: bool | None = None
    is_verified: bool | None = None


class UserPasswordChangeRequestDTO(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class UserListResponseDTO(OffsetPaginationResultSchema):
    items: list[UserResponseDTO]

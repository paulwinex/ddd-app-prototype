from datetime import datetime

from pydantic import Field, BaseModel, ConfigDict

from app.core.infra.pagination import OffsetPaginationResultSchema


class PermissionDTOBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PermissionResponseDTO(PermissionDTOBase):
    id: str
    name: str
    codename: str


class PermissionFullResponseDTO(PermissionResponseDTO):
    created_at: datetime
    updated_at: datetime


class PermissionDTO(PermissionFullResponseDTO):
    pass


class PermissionCreateRequestDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    codename: str = Field(..., min_length=1, max_length=100)


class PermissionUpdateRequestDTO(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)


class PermissionListResponseDTO(OffsetPaginationResultSchema):
    items: list[PermissionResponseDTO]

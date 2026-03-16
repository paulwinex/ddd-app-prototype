from datetime import datetime

from pydantic import Field, BaseModel, ConfigDict

from app.core.infra.pagination import OffsetPaginationResultSchema


class GroupDTOBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class GroupResponseDTO(GroupDTOBase):
    id: str
    name: str
    description: str | None = None
    is_system: bool = False


class GroupFullResponseDTO(GroupResponseDTO):
    created_at: datetime
    updated_at: datetime


class GroupDTO(GroupFullResponseDTO):
    pass


class GroupCreateRequestDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    is_system: bool = False


class GroupUpdateRequestDTO(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class GroupListResponseDTO(OffsetPaginationResultSchema):
    items: list[GroupResponseDTO]

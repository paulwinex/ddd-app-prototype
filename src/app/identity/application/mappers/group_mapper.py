from app.identity.domain.entities import Group
from app.identity.domain.value_objects import GroupID
from app.identity.application.dto import GroupDTO, GroupCreateRequestDTO
from app.identity.infra.models import GroupModel


class GroupMapper:
    @staticmethod
    def orm_to_entity(model: GroupModel) -> Group:
        return Group(
            id=GroupID(model.id),
            name=model.name,
            description=model.description,
            is_system=model.is_system,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def dto_to_entity(dto: GroupDTO) -> Group:
        return Group(
            id=GroupID(dto.id),
            name=dto.name,
            description=dto.description,
            is_system=dto.is_system,
        )

    @staticmethod
    def create_entity(dto: GroupCreateRequestDTO) -> Group:
        return Group(
            id = GroupID(),
            name = dto.name,
            description = dto.description,
            is_system = dto.is_system,
        )

    @staticmethod
    def to_model(entity: Group) -> GroupModel:
        return GroupModel(
            id=str(entity.id),
            name=entity.name,
            description=entity.description,
            is_system=entity.is_system,
        )

    @staticmethod
    def to_dto(entity: Group | GroupModel) -> GroupDTO:
        return GroupDTO.model_validate(entity)

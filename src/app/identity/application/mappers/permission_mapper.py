from app.identity.domain.entities import Permission
from app.identity.domain.value_objects import PermissionID
from app.identity.application.dto import PermissionDTO
from app.identity.infra.models import PermissionModel


class PermissionMapper:
    @staticmethod
    def to_entity(model: PermissionModel) -> Permission:
        return Permission(
            id=PermissionID(model.id),
            name=model.name,
            codename=model.codename,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Permission) -> PermissionModel:
        return PermissionModel(
            id=str(entity.id),
            name=entity.name,
            codename=entity.codename,
        )

    @staticmethod
    def to_dto(entity: Permission | PermissionModel) -> PermissionDTO:
        return PermissionDTO(
            id=str(entity.id),
            name=entity.name,
            codename=entity.codename,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

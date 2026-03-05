from app.identity.domain.entities import User
from app.identity.domain.value_objects import UserID, EmailVO, PasswordVO
from app.identity.dto.user_dto import UserResponseDTO
from app.identity.infra.models import UserModel


class UserMapper:
    @staticmethod
    def to_entity(model: UserModel) -> User:
        return User(
            id=UserID(model.id),
            email=EmailVO.create(model.email),
            password=PasswordVO(model.password_hash),
            first_name=model.first_name,
            last_name=model.last_name,
            is_active=model.is_active,
            is_superuser=model.is_superuser,
            is_verified=model.is_verified,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login_at=model.last_login_at,
        )

    @staticmethod
    def to_model(entity: User) -> UserModel:
        return UserModel(
            id=str(entity.id),
            email=str(entity.email),
            password_hash=str(entity.password),
            first_name=entity.first_name,
            last_name=entity.last_name,
            is_active=entity.is_active,
            is_superuser=entity.is_superuser,
            is_verified=entity.is_verified,
            last_login_at=entity.last_login_at,
        )

    @staticmethod
    def to_dto(entity: User|UserModel) -> UserResponseDTO:
        if isinstance(entity, User):
            return UserResponseDTO(
                id=str(entity.id),
                email=str(entity.email),
                first_name=entity.first_name,
                last_name=entity.last_name,
            )
        return UserResponseDTO(
            id=str(entity.id),
            email=entity.email,
            first_name=entity.first_name,
            last_name=entity.last_name,
        )

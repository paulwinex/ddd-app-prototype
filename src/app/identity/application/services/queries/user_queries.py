from app.core.infra.quary_params import OffsetPaginateQueryParams
from app.identity.api.query_params import UserListQueryParams
from app.identity.domain.interfaces import UserQueryRepositoryProtocol
from app.identity.domain.value_objects import UserID
from app.identity.application.dto.user_dto import UserListResponseDTO, UserResponseDTO, UserDTO
from app.identity.application.mappers import UserMapper


class UserQueryService:
    def __init__(self, query_repo: UserQueryRepositoryProtocol):
        self.query_repo = query_repo

    async def get_user_by_id(self, user_id: str | UserID) -> UserDTO:
        user = await self.query_repo.get_by_id(user_id)
        return UserMapper.to_dto(user)

    async def get_user_by_email(self, email: str) -> UserResponseDTO | None:
        user = await self.query_repo.get_by_email(email)
        if not user:
            return None
        return UserMapper.to_dto(user)

    async def get_user_list(
        self, pagination: OffsetPaginateQueryParams, filters: dict | None = None
    ) -> UserListResponseDTO:
        items, total = await self.query_repo.get_list(
            pagination=pagination,
            filters=filters,
        )
        items = [UserMapper.to_dto(user) for user in items]  # TODO check direct

        return UserListResponseDTO(
            items=items,
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            has_next=pagination.offset + len(items) < total,
            has_prev=pagination.offset > 0,
        )

    async def user_exists(self, user_id: str) -> bool:
        return await self.query_repo.exists(user_id)

    async def user_exists_by_email(self, email: str) -> bool:
        return await self.query_repo.exists_by_email(email)

from app.identity.application.dto import GroupCreateRequestDTO, GroupUpdateRequestDTO
from app.identity.application.mappers import GroupMapper
from app.identity.domain.exceptions import (
    GroupAlreadyExistsError,
    SuperUserGroupError,
    UserAlreadyInGroupError,
    UserNotInGroupError,
)
from app.identity.domain.interfaces import (
    GroupQueryRepositoryProtocol,
    GroupCommandRepositoryProtocol,
    UserQueryRepositoryProtocol,
    UserCommandRepositoryProtocol,
)


class GroupCommandService:
    def __init__(
        self,
        cmd_repo: GroupCommandRepositoryProtocol,
        query_repo: GroupQueryRepositoryProtocol,
        user_command_repo: UserCommandRepositoryProtocol | None = None,
        user_query_repo: UserQueryRepositoryProtocol | None = None,
    ):
        self.cmd_repo = cmd_repo
        self.query_repo = query_repo
        self.user_command_repo = user_command_repo
        self.user_query_repo = user_query_repo

    async def create_group(self, payload: GroupCreateRequestDTO) -> str:
        existing = await self.query_repo.get_by_name(payload.name)
        if existing:
            raise GroupAlreadyExistsError(payload.name)
        group_entity = GroupMapper.create_entity(payload)
        return await self.cmd_repo.create(group_entity)

    async def update_group(self, group_id: str, payload: GroupUpdateRequestDTO) -> str:
        group = await self.query_repo.get_by_id(group_id)

        if payload.name is not None and payload.name != group.name:
            existing = await self.query_repo.get_by_name(payload.name)
            if existing and str(existing.id) != str(group_id):
                raise GroupAlreadyExistsError(payload.name)

        group.update(name=payload.name, description=payload.description)
        await self.cmd_repo.update(group_id, group)
        return str(group_id)

    async def delete_group(self, group_id: str) -> None:
        group = await self.query_repo.get_by_id(group_id)
        if group.is_system:
            raise SuperUserGroupError("Cannot delete system group")
        await self.cmd_repo.delete(group_id)

    async def add_user_to_group(self, user_id: str, group_id: str) -> None:
        if await self.query_repo.user_in_group(user_id, group_id):
            raise UserAlreadyInGroupError(detail=f"User {user_id} already in group {group_id}")
        group = await self.query_repo.get_by_id(group_id)
        if group.is_system:
            superuser_group_users = await self.cmd_repo.get_group_users(group_id)
            if len(superuser_group_users) > 0:
                raise SuperUserGroupError("SuperUser group can only contain one user")
        await self.cmd_repo.add_user(group_id, user_id)

    async def remove_user_from_group(self, user_id: str, group_id: str) -> None:
        group = await self.query_repo.get_by_id(group_id)

        if not await self.query_repo.user_in_group(user_id, group_id):
            raise UserNotInGroupError(detail=f"User {user_id} not in group {group_id}")
        if group.is_system:
            superuser_group_users = await self.cmd_repo.get_group_users(group_id)
            if len(superuser_group_users) == 1:
                raise SuperUserGroupError("Cannot remove the only user from SuperUser group")
        await self.cmd_repo.remove_user(group_id, user_id)

    async def add_permission_to_group(self, group_id: str, permission_id: str) -> None:
        await self.cmd_repo.add_permission(group_id, permission_id)

    async def remove_permission_from_group(self, group_id: str, permission_id: str) -> None:
        await self.cmd_repo.remove_permission(group_id, permission_id)

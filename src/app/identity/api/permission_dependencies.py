from functools import partial
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

from app.identity.domain.permissions import PermissionsBase
from app.identity.domain.interfaces import (
    GroupQueryRepositoryProtocol,
    GroupCommandRepositoryProtocol,
    PermissionQueryRepositoryProtocol,
)
from app.identity.exceptions import AuthorizationError
from app.identity.infra.dependencies import (
    GroupQueryRepoDEP,
    GroupCommandRepoDEP,
    PermissionQueryRepoDEP,
)

if TYPE_CHECKING:
    from app.identity.domain.entities import User


class PermissionChecker:
    """Dependency for checking user permissions."""

    def __init__(
        self,
        group_query_repo: GroupQueryRepositoryProtocol,
        group_command_repo: GroupCommandRepositoryProtocol,
        permission_query_repo: PermissionQueryRepositoryProtocol,
    ):
        self.group_query_repo = group_query_repo
        self.group_command_repo = group_command_repo
        self.permission_query_repo = permission_query_repo

    async def check_permissions(
        self,
        required_permissions: list[PermissionsBase],
        user_id: str,
        is_superuser: bool = False,
    ) -> None:
        """Check if user has all required permissions."""
        if not required_permissions:
            return

        if is_superuser:
            return

        user_groups = await self.group_query_repo.get_user_groups(user_id)

        user_permission_codenames = set()
        for group in user_groups:
            group_permissions = await self.group_command_repo.get_group_permissions(
                str(group.id)
            )
            user_permission_codenames.update(group_permissions)

        for permission in required_permissions:
            if str(permission) not in user_permission_codenames:
                raise AuthorizationError(detail=f"Permission {permission.value} is required")


async def get_permission_checker(
    group_query_repo: GroupQueryRepoDEP,
    group_command_repo: GroupCommandRepoDEP,
    permission_query_repo: PermissionQueryRepoDEP,
) -> PermissionChecker:
    return PermissionChecker(group_query_repo, group_command_repo, permission_query_repo)


def has_permissions(required_permissions: list[PermissionsBase]):
    """Dependency for checking permissions in FastAPI routes.

    Usage:
        @router.post('/users', dependencies=[Depends(has_permissions([UserPermission.CAN_ADD_USER]))])
        async def create_user(payload):
            ...

    Note: Must be wrapped in Depends() when used in dependencies list.
    """
    from app.identity.api.dependencies import get_current_active_user

    async def permission_checker(
        current_user: Annotated["User", Depends(get_current_active_user)],
        checker: PermissionChecker = Depends(get_permission_checker),
    ) -> None:
        await checker.check_permissions(
            required_permissions,
            str(current_user.id),
            current_user.is_superuser,
        )

    return permission_checker


PermissionCheckerDEP = Annotated[PermissionChecker, Depends(get_permission_checker)]

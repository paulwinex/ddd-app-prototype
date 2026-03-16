from http import HTTPStatus

from app.core.exceptions import DomainError, EntityNotFoundError


class UserNotFoundError(EntityNotFoundError):
    pass


class UserAlreadyExistsError(DomainError):
    status_code = HTTPStatus.CONFLICT


class InvalidCredentialsError(DomainError):
    status_code = HTTPStatus.UNAUTHORIZED


class UserInactiveError(DomainError):
    status_code = HTTPStatus.FORBIDDEN


class SuperUserError(DomainError):
    status_code = HTTPStatus.UNAUTHORIZED


class GroupNotFoundError(EntityNotFoundError):
    pass


class GroupAlreadyExistsError(DomainError):
    status_code = HTTPStatus.CONFLICT


class PermissionNotFoundError(EntityNotFoundError):
    pass


class PermissionAlreadyExistsError(DomainError):
    status_code = HTTPStatus.CONFLICT


class SuperUserGroupError(DomainError):
    status_code = HTTPStatus.FORBIDDEN

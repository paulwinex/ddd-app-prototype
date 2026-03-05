from http import HTTPStatus

from app.core.exceptions import DomainError, EntityNotFoundError


class UserNotFoundError(EntityNotFoundError):
    pass


class UserAlreadyExistsError(DomainError):
    """User already exists."""
    status_code = HTTPStatus.CONFLICT


class InvalidCredentialsError(DomainError):
    """Invalid email or password"""
    status_code = HTTPStatus.UNAUTHORIZED


class UserInactiveError(DomainError):
    """User account is inactive"""
    status_code = HTTPStatus.FORBIDDEN


class SuperUserError(DomainError):
    """Super user error."""
    status_code = HTTPStatus.UNAUTHORIZED
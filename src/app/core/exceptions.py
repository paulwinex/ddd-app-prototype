from typing import Any
from http import HTTPStatus


class AppError(Exception):
    """Application Error"""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(
        self,
        detail: str | None = None,
        status: int | HTTPStatus = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ):
        self.detail = detail or self.__doc__ or "An error occurred"
        self.status = status or self.status_code
        self.headers = headers
        self.extra = kwargs
        super().__init__(self.detail)

    @property
    def code(self):
        return self.status.value if isinstance(self.status, HTTPStatus) else self.status

    @property
    def message(self):
        return self.detail or self.status.phrase


class DomainError(AppError):
    """Base domain exception"""

    status_code = HTTPStatus.BAD_REQUEST


class EntityNotFoundError(DomainError):
    """Entity not found"""

    status_code = HTTPStatus.NOT_FOUND


class ValueObjectValidationError(DomainError):
    """Value object validation error"""


class BusinessRuleError(DomainError):
    """Business rule violation error"""

    status_code = HTTPStatus.CONFLICT


class RepositoryError(AppError):
    """Base repository exception"""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR


class NotFoundError(RepositoryError):
    """Entity not found in repository"""

    status_code = HTTPStatus.NOT_FOUND


class IntegrityError(RepositoryError):
    """Database integrity error"""

    status_code = HTTPStatus.CONFLICT


class ValidationError(AppError):
    """Validation error"""

    status_code = HTTPStatus.BAD_REQUEST

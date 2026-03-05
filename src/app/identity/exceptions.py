from app.core.exceptions import AppError


class AuthenticationError(AppError):
    """Authentication error"""

    status_code = 401


class UnauthenticatedError(AuthenticationError):
    """Not authenticated"""

    status_code = 401

    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenError(AuthenticationError):
    """Invalid token"""


class AuthorizationError(AppError):
    """Authorization error"""

    status_code = 403

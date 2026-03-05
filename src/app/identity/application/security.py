import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from passlib.handlers.bcrypt import bcrypt

from app.core.settings import get_default_settings, Settings
from app.core.utils.datetime_utils import utcnow
from app.identity.exceptions import AuthenticationError, TokenError, UnauthenticatedError, AuthorizationError
import bcrypt

oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


class PasswordHasher:
    @staticmethod
    def hash(password: str) -> str:
        return hash_password(password)

    @staticmethod
    def verify(password: str, hashed_password: str) -> bool:
        return verify_password(password, hashed_password)


def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()


def verify_password(raw_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password=raw_password.encode('utf-8'),
        hashed_password=hashed_password.encode('utf-8')
    )


def hash_password(raw_password: str) -> str:
    hashed_password = bcrypt.hashpw(password=raw_password.encode('utf-8'), salt=bcrypt.gensalt())
    return hashed_password.decode('utf-8')


def create_auth_token(user_id: str, settings: Settings = None) -> dict[str, Any]:
    now = utcnow()
    settings = settings or get_default_settings()

    access_token_expire = timedelta(seconds=settings.AUTH.JWT_ACCESS_EXPIRE_SECONDS)
    access_token_expire_dt = now + access_token_expire
    access_payload = {
        "alg": settings.AUTH.JWT_ALGORITHM,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int(access_token_expire_dt.timestamp()),
        "sub": str(user_id),
        "type": "access",
    }
    access_token = jwt.encode(
        access_payload,
        settings.AUTH.JWT_SECRET.get_secret_value(),
        algorithm=settings.AUTH.JWT_ALGORITHM,
    )

    refresh_token_expire = timedelta(seconds=settings.AUTH.JWT_REFRESH_EXPIRE_SECONDS)
    refresh_token_expire_dt = now + refresh_token_expire
    refresh_payload = {
        "alg": settings.AUTH.JWT_ALGORITHM,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int(refresh_token_expire_dt.timestamp()),
        "sub": str(user_id),
        "type": "refresh",
    }
    refresh_token = jwt.encode(
        refresh_payload,
        settings.AUTH.JWT_SECRET.get_secret_value(),
        algorithm=settings.AUTH.JWT_ALGORITHM,
    )

    return {
        "access_token": access_token,
        "access_token_expire": int(access_token_expire_dt.timestamp()),
        "refresh_token": refresh_token,
        "refresh_token_expire": int(refresh_token_expire_dt.timestamp()),
    }


def create_token(payload: dict[str, Any], token_type: str) -> str:
    settings = get_default_settings()
    payload["type"] = token_type
    return jwt.encode(
        payload,
        settings.AUTH.JWT_SECRET.get_secret_value(),
        algorithm=settings.AUTH.JWT_ALGORITHM,
    )


def decode_token(token: str, verify_exp: bool = True) -> dict[str, Any]:
    settings = get_default_settings()
    return jwt.decode(
        token,
        settings.AUTH.JWT_SECRET.get_secret_value(),
        algorithms=[settings.AUTH.JWT_ALGORITHM],
        options={"verify_exp": verify_exp},
    )


def validate_token(token: str) -> str:
    if not token:
        raise AuthenticationError(detail="Token is required")
    try:
        payload = decode_token(token)
        check_payload(payload, check_type="access")
    except ExpiredSignatureError:
        raise AuthenticationError(detail="Token has expired")
    except JWTError as e:
        logging.exception(f"JWT decode error: {e}")
        raise AuthenticationError(detail="Invalid token")
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError(detail="Invalid token payload")
    return user_id


def refresh_access_token(refresh_token: str) -> dict[str, Any]:
    if not refresh_token:
        raise AuthenticationError(detail="Refresh token is required")
    try:
        payload = decode_token(refresh_token)
        check_payload(payload, check_type="refresh")
    except JWTError as e:
        logging.exception(f"JWT decode error: {e}")
        raise TokenError(detail="Invalid refresh token")
    user_id = payload.get("sub")
    if not user_id:
        raise TokenError(detail="Invalid refresh token payload")
    return create_auth_token(user_id)


def check_payload(payload: dict[str, Any], check_type: str = "access") -> None:
    if payload.get("type") != check_type:
        raise AuthenticationError(detail=f"Invalid token type. Expected {check_type}")
    if not payload.get("sub"):
        raise AuthenticationError(detail="Invalid token payload")


async def get_current_user(token: str = oauth2_scheme) -> dict[str, Any]:
    if not token:
        raise UnauthenticatedError()
    try:
        payload = decode_token(token)
        check_payload(payload, check_type="access")
    except ExpiredSignatureError:
        raise UnauthenticatedError(detail="Token has expired")
    except JWTError as e:
        logging.exception(f"JWT decode error: {e}")
        raise UnauthenticatedError(detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthenticatedError(detail="Invalid token payload")
    return {
        "sub": user_id,
        "exp": payload.get("exp"),
        "iat": payload.get("iat"),
    }


def require_permission(required_permission: str):

    async def permission_checker(current_user: dict = get_current_user()) -> bool:
        if current_user.get("is_superuser"):
            return True
        raise AuthorizationError(detail=f"Permission {required_permission} required")

    return permission_checker


def require_role(required_role: str):
    async def role_checker(current_user: dict = get_current_user()) -> bool:
        if current_user.get("is_superuser"):
            return True
        raise AuthorizationError(detail=f"Role {required_role} required")
    return role_checker

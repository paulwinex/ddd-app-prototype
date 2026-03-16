from fastapi import APIRouter

from .user_router import router as user_router
from .auth_router import router as auth_router
from .group_router import router as group_router
from .permission_router import router as permission_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(user_router, prefix="/users")
api_router.include_router(group_router, prefix="/groups")
api_router.include_router(permission_router, prefix="/permissions")

__all__ = ["api_router"]

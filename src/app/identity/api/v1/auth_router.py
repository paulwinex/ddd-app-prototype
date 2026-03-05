from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.identity.api.auth_schemas import TokenResponseSchema, LoginRequestSchema, RefreshTokenRequestSchema
from app.identity.api.dependencies import AuthServiceDEP, CurrentUserDEP, UserCommandServiceDEP
from app.identity.dto.user_dto import UserResponseDTO

router = APIRouter()


@router.post("/login", response_model=TokenResponseSchema)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthServiceDEP,
) -> TokenResponseSchema:
    result = await auth_service.login(LoginRequestSchema(username=form_data.username, password=form_data.password))
    return result


@router.post("/refresh", response_model=TokenResponseSchema)
async def refresh_token(
    token: RefreshTokenRequestSchema,
    auth_service: AuthServiceDEP,
) -> TokenResponseSchema:
    return await auth_service.refresh_token(token)


@router.get("/me", response_model=UserResponseDTO)
async def get_current_user_profile(
    user: CurrentUserDEP,
):
    return user


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    current_user: CurrentUserDEP,
    user_command_service: UserCommandServiceDEP,
) -> None:
    # TODO: email integration require
    raise NotImplementedError

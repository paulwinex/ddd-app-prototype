from http import HTTPStatus

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.exc import DBAPIError

from app.core.exceptions import AppError


def setup_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.error(f"AppError: {exc.message}", extra={"request": str(request.url)})
        return JSONResponse(
            status_code=exc.code,
            content={"detail": exc.message, "type": exc.__class__.__name__},
            headers=exc.headers,
        )

    @app.exception_handler(DBAPIError)
    async def db_error_handler(request: Request, exc: DBAPIError):
        message = f"Error: {exc.orig}. {exc.detail}"
        logger.exception(message)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": message, "type": exc.__class__.__name__})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(f"Unhandled exception: {exc}", extra={"request": str(request.url)})
        http_status = HTTPStatus.INTERNAL_SERVER_ERROR
        return JSONResponse(
            status_code=http_status.value,
            content={"detail": http_status.phrase, "type": exc.__class__.__name__},
        )

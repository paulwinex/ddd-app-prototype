from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI

from app.core.session import db_session
from app.core.startup.init_database import init_database
from loguru import logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting up application...")
    db_session.setup()
    logger.info("Database session initialized")
    await init_database()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down application...")
    await db_session.shutdown()
    logger.info("Database connections closed")
    logger.info("Application shutdown complete")

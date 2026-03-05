from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.core.startup.lifespan import lifespan
from app.core.startup.exception_handlers import setup_exception_handlers
from app.core.settings import get_default_settings, Settings
from app.identity.api.v1.user_router import router as user_router
from app.identity.api.v1.auth_router import router as auth_router
from app import __version__


def create_app(settings: Settings = None) -> FastAPI:
    settings = settings or get_default_settings()
    app = FastAPI(
        title=settings.NAME,
        description="DDD Architecture Prototype with FastAPI",
        version=__version__,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    app.state.settings = settings
    _setup_middleware(app)
    setup_exception_handlers(app)
    _include_routers(app)

    # health check
    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "healthy", "app": settings.NAME}

    return app


def _setup_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def _include_routers(app: FastAPI) -> None:
    main_router_v1 = APIRouter(prefix="/api/v1")
    main_router_v1.include_router(auth_router, prefix="/auth", tags=["Authentication"])
    main_router_v1.include_router(user_router, prefix="/users", tags=["Users"])
    app.include_router(main_router_v1)

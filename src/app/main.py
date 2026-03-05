import uvicorn

from app.core.settings import get_default_settings
from app.core.startup.create_app import create_app  # noqa: F401


if __name__ == "__main__":
    settings = get_default_settings()
    uvicorn.run(
        "app.main:create_app",
        host=settings.DEFAULT_HOST,
        port=settings.DEFAULT_PORT,
        reload=settings.DEBUG,
    )

import inspect

from loguru import logger

from app.core.session import db_session
from app.core.utils.modules import collect_domain_modules


async def init_database() -> None:
    #################################################
    # async with db_session._engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    #     logger.info("Database tables created")
    ################################################

    modules = collect_domain_modules("infra/init_db")
    if modules:
        async with db_session.get_session() as session:
            for module in modules:
                func = getattr(module, "init_database", None)
                if not func:
                    continue
                logger.info(f"Execute init func in {module.__name__}{func.__name__}")
                if inspect.iscoroutinefunction(func):
                    await func(session)
                else:
                    raise TypeError(f"{func.__name__} is not a coroutine function")

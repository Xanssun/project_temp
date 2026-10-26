from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from dishka import Provider, Scope
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from taskiq import AsyncBroker

from src.api.common.broker.nats.connection import create_nats_connection
from src.api.common.exceptions import setup_exception_handlers
from src.api.common.middlewares import setup_global_middlewares
from src.api.common.responses import ORJSONResponse
from src.api.v1.di import setup_dependencies
from src.api.v1.endpoints import setup_routers
from src.api.v1.middlewares import setup_middlewares
from src.api.v1.tasks.setup_taskiq_broker import setup_taskiq_broker
from src.common.di import container
from src.core.logger import log
from src.core.settings import Settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    try:
        await create_nats_connection()
        await setup_taskiq_broker()

        yield
    finally:
        if engine := app.state.engine:
            await engine.dispose()
        if redis := app.state.redis:
            await redis.aclose()
        if provider := app.state.provider:
            await provider.close_session()


def init_app_v1(
    settings: Settings,
    broker: AsyncBroker | None = None,
    title: str = "FastAPI",
    version: str = "0.1.0",
    docs_url: str | None = "/docs",
    redoc_url: str | None = "/redoc",
    swagger_ui_oauth2_redirect_url: str | None = "/docs/oauth2-redirect",
    **kw: Any,
) -> FastAPI:
    log.info("Initialize V1 API")
    app = FastAPI(
        title=title,
        version=version,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
        docs_url=docs_url,
        redoc_url=redoc_url,
        root_path="/api/v1",
        swagger_ui_oauth2_redirect_url=swagger_ui_oauth2_redirect_url,
        **kw,
    )
    provider = Provider(Scope.APP)
    setup_dependencies(provider, settings, app=app, taskiq_broker=broker)
    container.add_providers(provider)

    setup_dishka(container.get_container(), app)
    setup_routers(app)
    setup_exception_handlers(app)
    setup_middlewares(app)
    setup_global_middlewares(app, settings)

    return app

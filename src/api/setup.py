from collections.abc import AsyncIterator
from typing import Any, Tuple

from dishka import Provider, Scope
from dishka.integrations.faststream import setup_dishka as setup_faststream
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from faststream import FastStream
from faststream.nats import NatsBroker as FaststreamNatsBroker
from faststream.security import SASLPlaintext
from taskiq import AsyncBroker, TaskiqEvents, TaskiqScheduler, TaskiqState
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_nats import NatsBroker

from src.api.common.broker.nats.connection import create_nats_connection
from src.api.common.middlewares import setup_global_middlewares
from src.api.common.provider.base import AsyncProvider
from src.api.common.responses import ORJSONResponse
from src.api.v1.di import setup_dependencies, setup_taskiq_dependencies
from src.api.v1.subscribers.setup import setup_subscribers_routers
from src.api.v1.tasks import setup_tasks
from src.common.di import container
from src.common.tools.serializer import decoder
from src.core.logger import log
from src.core.settings import Settings


def init_app(
    *sub_apps: Tuple[str, FastAPI, str | None],
    settings: Settings,
    **kw: Any,
) -> FastAPI:
    log.info("Initialize General")
    app = FastAPI(
        default_response_class=ORJSONResponse,
        docs_url=None,
        redoc_url=None,
        swagger_ui_oauth2_redirect_url=None,
        **kw,
    )
    for apps in sub_apps:
        app.mount(*apps)

    setup_global_middlewares(app, settings)

    return app


async def on_taskiq_startup(_: TaskiqState) -> None: ...


async def on_taskiq_shutdown(_: TaskiqState) -> None:
    ioc_container = container.get_container()

    if aiohttp_provider := await ioc_container.get(AsyncProvider):
        await aiohttp_provider.close_session()

    await ioc_container.close()


def init_taskiq_v1(settings: Settings) -> tuple[AsyncBroker, TaskiqScheduler]:
    log.info("Initialize Taskiq v1")
    broker = NatsBroker(
        settings.nats.servers,
        subject="taskiq.arbiter",
        queue="taskiq_arbiter",
        user=settings.nats.user,
        password=settings.nats.password,
    )
    scheduler = TaskiqScheduler(broker=broker, sources=[LabelScheduleSource(broker)])
    setup_taskiq_dependencies(settings, broker)
    setup_tasks(broker)

    broker.add_event_handler(TaskiqEvents.WORKER_STARTUP, on_taskiq_startup)
    broker.add_event_handler(TaskiqEvents.WORKER_SHUTDOWN, on_taskiq_shutdown)

    return broker, scheduler


@asynccontextmanager
async def _faststream_lifespan() -> AsyncIterator[None]:
    ioc_container = container.get_container()

    await create_nats_connection()

    yield

    await ioc_container.close()


def init_faststream_app(settings: Settings) -> tuple[FaststreamNatsBroker, FastStream]:
    provider = Provider(Scope.APP)
    setup_dependencies(provider, settings)
    container.add_providers(provider)

    broker = FaststreamNatsBroker(
        servers=settings.nats.servers,
        decoder=decoder,
        security=SASLPlaintext(
            username=settings.nats.user,
            password=settings.nats.password,
            use_ssl=True,
        ),
    )

    app = FastStream(
        broker,
        lifespan=_faststream_lifespan,
    )
    setup_subscribers_routers(broker)

    setup_faststream(container.get_container(), app, auto_inject=True)

    return broker, app

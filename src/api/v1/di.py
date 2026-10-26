from typing import Callable, TypeVar

from dishka import Provider, Scope
from dishka.integrations.taskiq import (
    TaskiqProvider,
)
from dishka.integrations.taskiq import (
    setup_dishka as setup_dishka_taskiq,
)
from fastapi import FastAPI
from nats.aio.client import Client as NatsClient
from taskiq import AsyncBroker
from taskiq_nats import NatsBroker as TaskiqNatsBroker

from src.api.common.broker.nats.core import NatsBroker, NatsJetStreamBroker
from src.api.common.bus.core import EventBusImpl
from src.api.common.cache.destributed_lock import DistributedLock
from src.api.common.cache.redis import RedisCache, get_redis
from src.api.common.interfaces.event_bus import EventBus
from src.api.common.provider.aiohttp import AiohttpProvider
from src.api.common.provider.base import AsyncProvider
from src.api.common.provider.curlcffi import CurlCffiProvider
from src.api.v1.handlers import MediatorImpl, setup_mediator
from src.common.di import container
from src.common.interfaces.encrypt import AbstractAESCipher
from src.common.interfaces.mediator import MediatorProtocol
from src.common.security.aescipher import get_aes_cipher
from src.common.security.argon2 import get_argon2_hasher
from src.common.security.jwt import JWT
from src.core.settings import Settings
from src.database import create_database_factory
from src.database.core.connection import create_sa_engine, create_sa_session_factory
from src.database.core.manager import TransactionManager
from src.database.gateway import DBGateway
from src.services import ExternalServiceGateway

DependencyType = TypeVar("DependencyType")


def singleton(dependency: DependencyType) -> Callable[[], DependencyType]:
    def singleton_factory() -> DependencyType:
        return dependency

    return singleton_factory


def setup_dependencies(
    di_provider: Provider,
    settings: Settings,
    *,
    taskiq_broker: AsyncBroker | None = None,
    nats_client: NatsClient | None = None,
    app: FastAPI | None = None,
) -> None:
    engine = create_sa_engine(
        settings.db.url,
        pool_size=settings.db.connection_pool_size,
        max_overflow=settings.db.connection_max_overflow,
        pool_pre_ping=settings.db.connection_pool_pre_ping,
    )

    redis = get_redis(settings.redis)
    session_factory = create_sa_session_factory(engine)
    database_factory = create_database_factory(TransactionManager, session_factory)

    hasher = get_argon2_hasher()
    aescipher = get_aes_cipher(settings.aescipher)
    jwt = JWT(settings.ciphers)

    if nats_client:
        nats_client = nats_client
    else:
        nats_client = NatsClient()

    nats_broker = NatsBroker(nats_client)
    jetstream_broker = NatsJetStreamBroker(nats_broker.nats.jetstream())
    event_bus = (
        EventBusImpl.builder()
        .brokers(nats_broker, jetstream_broker)
        .middleware()
        .build()
    )

    distributed_lock = DistributedLock(redis)

    # external services
    provider = AiohttpProvider()
    open_ssl_provider = CurlCffiProvider()
    external_gateway = ExternalServiceGateway(settings, provider, open_ssl_provider)

    if app:
        app.state.engine = engine
        app.state.redis = redis
        app.state.provider = provider

    mediator = MediatorImpl()
    setup_mediator(
        mediator,
        db_gateway=database_factory,
        external_gateway=external_gateway,
        redis=redis,
        jwt=jwt,
        hasher=hasher,
        aescipher=aescipher,
        event_bus=event_bus,
    )
    if app:
        app.dependency_overrides[MediatorProtocol] = singleton(mediator)
        app.dependency_overrides[DBGateway] = database_factory
        app.dependency_overrides[Settings] = singleton(settings)

    if taskiq_broker:
        di_provider.provide(singleton(taskiq_broker), provides=AsyncBroker)

    di_provider.provide(singleton(distributed_lock), provides=DistributedLock)
    di_provider.provide(singleton(settings), provides=Settings)
    di_provider.provide(singleton(event_bus), provides=EventBus)
    di_provider.provide(singleton(redis), provides=RedisCache)
    di_provider.provide(singleton(nats_broker), provides=NatsBroker)
    di_provider.provide(singleton(provider), provides=AsyncProvider)
    di_provider.provide(singleton(external_gateway), provides=ExternalServiceGateway)
    di_provider.provide(singleton(jetstream_broker), provides=NatsJetStreamBroker)
    di_provider.provide(
        singleton(mediator),
        provides=MediatorProtocol,
    )
    di_provider.provide(singleton(aescipher), provides=AbstractAESCipher)


def setup_taskiq_dependencies(settings: Settings, broker: TaskiqNatsBroker) -> None:
    provider = Provider(scope=Scope.APP)
    setup_dependencies(
        provider,
        settings,
        nats_client=broker.client,
        taskiq_broker=broker,
    )

    container.add_providers(provider, TaskiqProvider())
    setup_dishka_taskiq(container.get_container(), broker)

from nats.aio.client import Client as NatsClient

from src.api.common.broker.nats.core import NatsBroker
from src.common.di.base import inject
from src.common.di.marker import Depends, FromDepends
from src.core.settings import Settings


@inject
async def create_nats_connection(
    settings: Depends[Settings] = FromDepends(),
    broker: Depends[NatsBroker] = FromDepends(),
) -> NatsClient:
    await broker.nats.connect(
        servers=settings.nats.servers,
        user=settings.nats.user,
        password=settings.nats.password,
    )
    return broker.nats

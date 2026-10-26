from taskiq import AsyncBroker

from src.common.di.base import inject
from src.common.di.marker import Depends, FromDepends


@inject
async def setup_taskiq_broker(
    taskiq_broker: Depends[AsyncBroker] = FromDepends(),
) -> None:
    await taskiq_broker.startup()

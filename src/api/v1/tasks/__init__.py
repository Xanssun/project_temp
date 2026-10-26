from typing import Any

from taskiq import AsyncBroker

from src.api.v1.tasks.types import TasksEnum
from src.common.di.base import inject
from src.common.di.marker import Depends, FromDepends


def setup_tasks(broker: AsyncBroker) -> None:
    pass


@inject
async def kiq_task(
    task_name: TasksEnum,
    taskiq_broker: Depends[AsyncBroker] = FromDepends(),
    *args: Any,
    **kwargs: Any,
) -> None:
    if not (task := taskiq_broker.find_task(task_name.value)):
        raise ValueError(f"Task {task_name} not found")
    await task.kiq(*args, **kwargs)

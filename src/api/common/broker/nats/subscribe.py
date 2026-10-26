from typing import Awaitable, Callable

from nats.aio.msg import Msg

from src.api.common.interfaces.handler import HandlerType


def nats_callback(
    handler: HandlerType,
) -> Callable[[Msg], Awaitable[None]]:
    if not hasattr(handler, "func"):
        setattr(handler, "func", handler.__call__)  # noqa: B010

    return handler

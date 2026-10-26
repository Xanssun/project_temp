from typing import Any

import msgpack
from faststream.nats import NatsMessage


def decoder(msg: NatsMessage) -> Any:
    if isinstance(msg.body, list):
        return [msgpack.unpackb(body) for body in msg.body]
    return msgpack.unpackb(msg.body)

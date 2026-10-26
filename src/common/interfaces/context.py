from __future__ import annotations

from types import TracebackType
from typing import Protocol, Type


class AsyncContextManager(Protocol):
    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    async def __aenter__(self) -> AsyncContextManager: ...

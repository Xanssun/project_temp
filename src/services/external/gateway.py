from typing import Any, Callable

from src.api.common.provider.base import AsyncProvider
from src.api.common.provider.curlcffi import CurlCffiProvider
from src.common.interfaces.gateway import BaseGateway
from src.core.settings import Settings


class ExternalServiceGateway(BaseGateway):
    __slots__ = (
        "settings",
        "provider",
        "open_ssl_provider",
        "_cache",
    )

    def __init__(
        self,
        settings: Settings,
        provider: AsyncProvider,
        open_ssl_provider: CurlCffiProvider,
    ) -> None:
        self.settings = settings
        self.provider = provider
        self.open_ssl_provider = open_ssl_provider
        self._cache: dict[str, Any] = {}
        super().__init__(provider)

    def _from_cache[S, **P](
        self, key: str, factory: Callable[P, S], *args: P.args, **kwargs: P.kwargs
    ) -> S:
        if not (cached := self._cache.get(key)):
            cached = factory(*args, **kwargs)
            self._cache[key] = cached

        return cached

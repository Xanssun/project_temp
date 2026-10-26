from typing import Any

from src.api.common.cache.redis import RedisCache
from src.api.v1.handlers.auth.tools import refresh_token_key
from src.api.v1.handlers.base import BaseHandler
from src.common import dtos
from src.common.dtos.base import DTO
from src.common.exceptions import UnAuthorizedError


class LogoutQuery(DTO):
    user: dtos.PrivateUser


class LogoutHandler(BaseHandler[LogoutQuery, dtos.Status]):
    __slots__ = ("_cache",)

    def __init__(
        self,
        redis: RedisCache,
    ) -> None:
        self._cache = redis

    async def handle(self, query: LogoutQuery, **kwargs: Any) -> dtos.Status:
        if not (refresh_token := query.user.refresh_token):
            raise UnAuthorizedError("Not allowed")

        await self._cache.delete(refresh_token_key(refresh_token))
        return dtos.Status(ok=True)

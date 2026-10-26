from typing import Any

from src.api.common.cache.redis import RedisCache
from src.api.v1.handlers.base import BaseHandler
from src.common import dtos
from src.common.dtos.base import DTO
from src.common.exceptions import NotFoundError
from src.common.tools.code import generate_code


class ResendCodeQuery(DTO):
    login: str


class ResendCodeHandler(BaseHandler[ResendCodeQuery, dtos.Status]):
    def __init__(
        self,
        redis: RedisCache,
    ) -> None:
        self._cache = redis

    async def handle(self, query: ResendCodeQuery, **kwargs: Any) -> dtos.Status:
        cache_key = f"password-reset:{query.login}"
        old_code = await self._cache.get_single(cache_key)
        if old_code is None:
            raise NotFoundError("not found")

        cached_data = await self._cache.get_single(old_code)
        if cached_data is None:
            raise NotFoundError("not found")

        confirm_code = generate_code()
        await self._cache.delete(old_code)
        await self._cache.set_single(
            confirm_code,
            cached_data,
            expire_seconds=360,
        )
        await self._cache.set_single(
            cache_key,
            confirm_code,
            expire_seconds=360,
        )

        return dtos.Status(ok=True)

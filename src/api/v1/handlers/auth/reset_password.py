from typing import Any

from src.api.common.cache.redis import RedisCache
from src.api.v1.handlers.base import BaseHandler
from src.common import dtos
from src.common.dtos.base import DTO
from src.common.tools.code import generate_code
from src.database.gateway import DBGateway


class ResetPasswordQuery(DTO):
    login: str


class ResetPasswordHandler(BaseHandler[ResetPasswordQuery, dtos.Status]):
    def __init__(
        self,
        redis: RedisCache,
        db_gateway: DBGateway,
    ) -> None:
        self._cache = redis
        self._db_gateway = db_gateway
        self._user_repository = db_gateway.user()

    async def handle(self, query: ResetPasswordQuery, **kwargs: Any) -> dtos.Status:
        async with self._db_gateway:
            await self._user_repository.get(login=query.login)

        reset_code = generate_code()
        await self._cache.set_single(
            reset_code,
            query.model_dump_json(),
            expire_seconds=360,
        )
        await self._cache.set_single(
            f"password-reset:{query.login}",
            reset_code,
            expire_seconds=360,
        )

        return dtos.Status(ok=True)

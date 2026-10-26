from typing import Any

from src.api.common.cache.redis import RedisCache
from src.api.v1.handlers.auth.tools import (
    create_tokens,
    refresh_token_key,
    verify_token,
)
from src.api.v1.handlers.base import BaseHandler
from src.common import dtos
from src.common.dtos.base import DTO
from src.common.exceptions import UnAuthorizedError
from src.common.security.jwt import JWT


class RefresTokenQuery(DTO):
    data: dtos.Fingerprint
    user: dtos.PrivateUser


class RefreshTokenHandler(BaseHandler[RefresTokenQuery, dtos.TokensExpire]):
    def __init__(
        self,
        jwt: JWT,
        redis: RedisCache,
    ) -> None:
        self._jwt = jwt
        self._cache = redis

    async def handle(self, query: RefresTokenQuery, **kwargs: Any) -> dtos.TokensExpire:
        if not (refresh_token := query.user.refresh_token):
            raise UnAuthorizedError("Not allowed")

        user_uuid = await verify_token(
            self._jwt, self._cache, refresh_token, "refresh"
        )
        await self._cache.delete(refresh_token_key(refresh_token))
        return await create_tokens(
            self._jwt,
            self._cache,
            user_uuid,
            query.data.fingerprint,
        )

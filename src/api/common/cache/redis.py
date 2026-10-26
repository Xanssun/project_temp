from contextlib import asynccontextmanager
from datetime import timedelta
from typing import (
    Any,
    AsyncGenerator,
    Final,
    List,
    Literal,
    TypeVar,
    Union,
)
from uuid import uuid4

import orjson
import redis.asyncio as aioredis

from src.common.dtos.base import DTO
from src.common.serializers.orjson import orjson_dumps
from src.core.settings import RedisSettings

ValueType = TypeVar("ValueType", float, int, str, bytes, bool)


class NonSerializableObjectsProvidedError(Exception):
    pass


ONE_MINUTE: Final[int] = 60
ONE_HOUR: Final[int] = 3600
ONE_DAY: Final[int] = 86_400
ONE_MONTH: Final[int] = 2_592_000


def _str_key(key: Any) -> str:
    return str(key)


class RedisCache:
    __slots__ = ("_redis",)

    # why mypy thinks that Redis is Generic if it isn't.
    def __init__(self, redis: aioredis.Redis) -> None:  # type: ignore
        self._redis = redis

    async def get_single(self, key: Any) -> str | None:
        return await self._redis.get(_str_key(key))

    async def set_single(
        self,
        key: Union[str, Any],
        value: ValueType,
        expire_seconds: int | None = ONE_HOUR,
        expire_milliseconds: int | None = None,
        return_origin: bool = True,
        **additional: Any,
    ) -> Union[ValueType, bool] | None:
        serialized = None
        if isinstance(value, (DTO, dict, list)):
            try:
                serialized = orjson_dumps(value)
            except orjson.JSONDecodeError as e:
                raise NonSerializableObjectsProvidedError(
                    "Some of the objects that you've provided are not serializable"
                ) from e

        set_value = await self._redis.set(
            _str_key(key),
            serialized or value,
            ex=expire_seconds,
            px=expire_milliseconds,
            **additional,
        )
        if return_origin:
            return value

        return set_value

    async def delete(self, *keys: Any) -> None:
        r_keys = (_str_key(key) for key in keys)
        await self._redis.delete(*r_keys)

    async def set_list(
        self,
        key: Any,
        *values: str,
        side: Literal["right", "left"] = "left",
        expire_seconds: int | None = None,
        expire_milliseconds: int | None = None,
    ) -> int:
        key = _str_key(key)

        push = self._redis.lpush if side == "left" else self._redis.rpush

        result = await push(key, *values)

        if expire_seconds:
            await self._redis.expire(key, expire_seconds)
        if expire_milliseconds:
            await self._redis.pexpire(key, expire_milliseconds)

        return result

    async def get_list(self, key: Any, start: int = 0, end: int = -1) -> List[str]:
        return await self._redis.lrange(_str_key(key), start, end)

    async def pop(self, key: Any, value: str, count: int = 0) -> int:
        return await self._redis.lrem(_str_key(key), count, value)

    async def aclose(self) -> None:
        await self._redis.aclose()  # type: ignore

    async def hset(
        self,
        key: Any,
        field: str,
        value: int | str,
    ) -> int:
        """
        Set hash field to value.
        Returns number of fields added.
        """
        return await self._redis.hset(
            _str_key(key),
            field,
            value,
        )

    async def hincrby(
        self,
        key: Any,
        field: str,
        amount: int = 1,
    ) -> int:
        """
        Increment hash field by amount.
        Returns new value.
        """
        return await self._redis.hincrby(
            _str_key(key),
            field,
            amount,
        )

    async def hdel(
        self,
        key: Any,
        *fields: str,
    ) -> int:
        """
        Delete one or more hash fields.
        Returns number of fields removed.
        """
        return await self._redis.hdel(
            _str_key(key),
            *fields,
        )

    async def hgetall(self, key: Any) -> dict[str, str]:
        """
        Get all fields and values from hash.
        """
        raw = await self._redis.hgetall(_str_key(key))
        return dict(raw)

    async def hget(self, key: Any, field: str) -> str | None:
        return await self._redis.hget(_str_key(key), field)

    async def expire(
        self,
        key: Any,
        seconds: int,
    ) -> bool:
        """
        Set expiration time in seconds.
        """
        return await self._redis.expire(
            _str_key(key),
            seconds,
        )

    @asynccontextmanager
    async def lock(
        self, key: str, expire: int | timedelta | None = None
    ) -> AsyncGenerator[bool, None]:
        acquired = await self.acquire_lock(key=key, expire=expire)
        try:
            yield bool(acquired)
        finally:
            if acquired:
                await self.release_lock(key, acquired)

    async def acquire_lock(
        self,
        key: str,
        value: str | None = None,
        expire: int | timedelta | None = None,
    ) -> str | None:
        if isinstance(expire, timedelta):
            expire = expire.seconds
        owner_id = value or str(uuid4())
        acquired: bool = await self.set_single(
            key=key,
            return_origin=False,
            value=owner_id,  # type: ignore
            expire_seconds=expire,
            nx=True,  # type: ignore
        )

        if acquired:
            return owner_id
        return None

    async def is_acquired(self, key: str) -> bool:
        return bool(await self.get_single(key))

    async def release_lock(self, key: str, value: str) -> bool:
        script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
        """
        res = await self._redis.eval(script, 1, key, value)  # type: ignore
        try:
            return int(res) == 1
        except Exception:
            return bool(res)

    async def set_expire(self, key: str, expire: float | timedelta) -> bool:
        return await self._redis.expire(
            key,
            expire if isinstance(expire, timedelta) else timedelta(seconds=expire),
        )


def get_redis(settings: RedisSettings, **kw: Any) -> RedisCache:
    return RedisCache(
        aioredis.Redis(
            host=settings.host,
            port=settings.port,
            password=settings.password,
            decode_responses=True,
            **kw,
        )
    )

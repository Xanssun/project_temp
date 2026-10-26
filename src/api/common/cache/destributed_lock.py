import asyncio
from datetime import timedelta
from typing import Any
from uuid import uuid4

from src.api.common.cache.redis import RedisCache


class Lock:
    def __init__(
        self,
        cache: RedisCache,
        /,
        name: str,
        postfix: str = ":lock",
        lock_expire_sec: float = 6,
        refresh_interval: float = 3,
    ) -> None:
        self._cache = cache
        self._key = name + postfix
        self._lock_expire_sec = lock_expire_sec
        self._refresh_interval = refresh_interval
        self._heartbeat_task: asyncio.Task[None] | None = None
        self._is_running: bool = False
        self.id = uuid4().hex

    async def __aenter__(self) -> "Lock":
        if self._is_running:
            raise RuntimeError("Heartbeat already started")
        if not await self._try_acquire():
            raise RuntimeError("Aleady locked by another process")

        self._is_running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_worker())
        return self

    async def __aexit__(self, *args: Any) -> None:
        self._is_running = False
        if not self._heartbeat_task:
            raise RuntimeError("Heartbeat task not started")
        try:
            await asyncio.wait_for(
                self._heartbeat_task, timeout=self._refresh_interval + 0.5
            )
            await self._try_release()
        except TimeoutError:
            pass

    async def _try_acquire(self) -> bool:
        result = await self._cache.acquire_lock(
            key=self._key,
            value=self.id,
            expire=timedelta(seconds=self._lock_expire_sec),
        )
        return result is not None

    async def _try_release(self) -> bool:
        return await self._cache.release_lock(key=self._key, value=self.id)

    async def _heartbeat_worker(self) -> None:
        while self._is_running:
            if not self._key:
                raise RuntimeError("Lock key not set")

            lock_refreshed = await self._cache.set_expire(
                self._key, self._lock_expire_sec
            )
            if not lock_refreshed:
                lock_reacquired = await self._try_acquire()
                if not lock_reacquired:
                    raise RuntimeError(
                        "Lock heartbeat failed: lock lost and could not be re-acquired"
                    )
            await asyncio.sleep(self._refresh_interval)


class DistributedLock:
    def __init__(self, cache: RedisCache) -> None:
        self._cache = cache

    def __call__(
        self,
        name: str,
        lock_expire_sec: float = 7,
        refresh_interval: float = 3,
        postfix: str = ":lock",
    ) -> Lock:
        if lock_expire_sec < refresh_interval:
            raise ValueError("lock_expire_sec must be greater than refresh_interval")

        return Lock(
            self._cache,
            name=name,
            postfix=postfix,
            lock_expire_sec=lock_expire_sec,
            refresh_interval=refresh_interval,
        )

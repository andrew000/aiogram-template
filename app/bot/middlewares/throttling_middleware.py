from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any, Final, TypeVar

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import CallbackQuery, ChatMemberUpdated, TelegramObject, Update, User

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from redis.asyncio.client import Redis
    from redis.typing import ExpiryT

DEFAULT_RATE_LIMIT: Final[int] = 1000  # milliseconds cooldown
KeyValueT = TypeVar("KeyValueT", bound=int | str)


class TTLCache:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    @classmethod
    def key(cls, object_id: KeyValueT, throttle_key: str = "-") -> str:
        return f"{cls.__name__}:{object_id}:{throttle_key}"

    async def get(self, key: KeyValueT, throttle_key: str = "-") -> bytes | None:
        return await self.redis.get(self.key(key, throttle_key))

    async def set(
        self,
        key: KeyValueT,
        time_ms: ExpiryT,
        value: Any,
        throttle_key: str = "-",
    ) -> bool:
        return await self.redis.psetex(self.key(key, throttle_key), time_ms, value)


class LeakyBucket:
    def __init__(self, redis: Redis, limit: int, period: timedelta) -> None:
        self.redis = redis
        self.limit = limit
        self.period = period

    @classmethod
    def key(cls, object_id: KeyValueT) -> str:
        return f"{cls.__name__}:{object_id}"

    async def is_limit_reached(self, object_id: KeyValueT, bucket_decrement: int = 1) -> bool:
        key = self.key(object_id)

        if await self.redis.setnx(key, self.limit):
            await self.redis.expire(key, int(self.period.total_seconds()))

        bucket_value = await self.redis.get(key) or 0

        if int(bucket_value) > 0:
            await self.redis.decrby(key, bucket_decrement)
            return False

        return True


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, redis: Redis) -> None:
        self.ttl_cache = TTLCache(redis)
        self.leaky_bucket = LeakyBucket(redis, 4, timedelta(seconds=7))

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Update,  # type: ignore[override]
        data: dict[str, Any],
    ) -> Any:
        user: User = data["event_from_user"]

        if isinstance(event, ChatMemberUpdated):
            return await handler(event, data)

        throttle_key = get_flag(data, "throttle_key", default="-")
        throttle_time = get_flag(data, "throttle_time", default=DEFAULT_RATE_LIMIT)
        bucket_decrement = get_flag(data, "bucket_decrement", default=1)

        if isinstance(throttle_time, timedelta):
            throttle_time = int(throttle_time.total_seconds() * 1000)  # Convert to milliseconds

        if await self.ttl_cache.get(user.id, throttle_key):
            if isinstance(event, CallbackQuery):
                await event.answer("⏳ Too fast!", show_alert=True)

            if throttle_key == "-":
                await self.ttl_cache.set(
                    key=self.ttl_cache.key(user.id),
                    time_ms=throttle_time,
                    value=throttle_time,
                    throttle_key=throttle_key,
                )

            return None

        await self.ttl_cache.set(
            key=user.id,
            time_ms=throttle_time,
            value=throttle_time,
            throttle_key=throttle_key,
        )

        if await self.leaky_bucket.is_limit_reached(user.id, bucket_decrement=bucket_decrement):
            if isinstance(event, CallbackQuery):
                await event.answer("🪣 Too fast!", show_alert=True)

            return None

        return await handler(event, data)

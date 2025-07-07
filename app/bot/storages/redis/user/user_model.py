from datetime import datetime, timedelta
from typing import Final, Self

import msgspec.msgpack
from redis.asyncio import Redis
from redis.typing import ExpiryT

from storages.psql.utils.alchemy_struct import AlchemyStruct

ENCODER: Final[msgspec.msgpack.Encoder] = msgspec.msgpack.Encoder()


class RDUserModel(msgspec.Struct, AlchemyStruct["RDUserModel"], kw_only=True, array_like=True):
    id: int
    username: str | None = msgspec.field(default=None)
    first_name: str
    last_name: str | None = msgspec.field(default=None)
    registration_datetime: datetime
    pm_active: bool

    @classmethod
    def key(cls, user_id: int | str) -> str:
        return f"{cls.__name__}:{user_id}"

    @classmethod
    async def get(cls, redis: Redis, user_id: int | str) -> Self | None:
        data = await redis.get(cls.key(user_id))
        if data:
            return msgspec.msgpack.decode(data, type=cls)
        return None

    async def save(self, redis: Redis, ttl: ExpiryT = timedelta(days=1)) -> str:
        return await redis.setex(self.key(self.id), ttl, ENCODER.encode(self))

    @classmethod
    async def delete(cls, redis: Redis, user_id: int | str) -> int:
        return await redis.delete(cls.key(user_id))

    @classmethod
    async def delete_all(cls, redis: Redis) -> int:
        keys = await redis.keys(f"{cls.__name__}:*")
        return await redis.delete(*keys) if keys else 0

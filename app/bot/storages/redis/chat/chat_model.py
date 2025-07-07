from datetime import datetime, timedelta
from typing import Final, Literal, Self

import msgspec
from redis.asyncio import Redis
from redis.typing import ExpiryT

from storages.psql.utils.alchemy_struct import AlchemyStruct

ENCODER: Final[msgspec.msgpack.Encoder] = msgspec.msgpack.Encoder()


class RDChatModel(msgspec.Struct, AlchemyStruct["RDChatModel"], kw_only=True, array_like=True):
    id: int
    chat_type: Literal["group", "supergroup", "channel"]
    title: str | None = msgspec.field(default=None)
    username: str | None = msgspec.field(default=None)
    registration_datetime: datetime
    migrate_from_chat_id: int | None = msgspec.field(default=None)
    migrate_datetime: datetime | None = msgspec.field(default=None)

    @classmethod
    def key(cls, chat_id: int | str) -> str:
        return f"{cls.__name__}:{chat_id}"

    @classmethod
    async def get(cls, redis: Redis, chat_id: int | str) -> Self | None:
        data = await redis.get(cls.key(chat_id))
        if data:
            return msgspec.msgpack.decode(data, type=cls)
        return None

    async def save(self, redis: Redis, ttl: ExpiryT = timedelta(days=1)) -> int:
        return await redis.setex(self.key(self.id), ttl, ENCODER.encode(self))

    @classmethod
    async def delete(cls, redis: Redis, chat_id: int | str) -> int:
        return await redis.delete(cls.key(chat_id))

    @classmethod
    async def delete_all(cls, redis: Redis) -> int:
        keys = await redis.keys(f"{cls.__name__}:*")
        return await redis.delete(*keys)

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Protocol, Self

import msgspec
from aiogram.filters import Filter

if TYPE_CHECKING:
    from collections.abc import Sequence

    from aiogram.types import CallbackQuery
    from redis.asyncio import Redis
    from redis.typing import ExpiryT

    from stub import I18nContext


class HasOwnerId(Protocol):
    owner_id: int


class CallbackClickedByTargetUser[T: HasOwnerId](Filter):
    async def __call__(
        self,
        query: CallbackQuery,
        callback_data: T | None = None,
    ) -> bool:
        if not callback_data or not hasattr(callback_data, "owner_id"):
            return False

        if query.from_user.id != callback_data.owner_id:
            await query.answer("❌", show_alert=True)
            return False

        return True


class RDMessageOwner(msgspec.Struct, kw_only=True, array_like=True):
    owner_id: int

    @classmethod
    def key(cls, chat_id: int, message_id: int) -> str:
        return f"{cls.__name__}:{chat_id}:{message_id}"

    @classmethod
    async def get(cls, redis: Redis, chat_id: int, message_id: int) -> Self | None:
        data = await redis.get(cls.key(chat_id, message_id))
        if data:
            return msgspec.msgpack.decode(data, type=cls)
        return None

    @classmethod
    async def set(
        cls,
        redis: Redis,
        chat_id: int,
        message_id: int,
        owner_id: int,
        ttl: ExpiryT = timedelta(days=2),
    ) -> int:
        return await redis.setex(
            name=cls.key(chat_id, message_id),
            time=ttl,
            value=msgspec.msgpack.encode(cls(owner_id=owner_id)),
        )

    @classmethod
    async def delete(cls, redis: Redis, chat_id: int, message_id: int) -> None:
        await redis.delete(cls.key(chat_id, message_id))


class CallbackClickedByRedisUser(Filter):
    async def __call__(self, cb: CallbackQuery, i18n: I18nContext, redis: Redis) -> bool:
        message_owner = await RDMessageOwner.get(redis, cb.message.chat.id, cb.message.message_id)
        if not message_owner:
            await cb.message.edit_text(i18n.message.deprecated())
            return False

        if cb.from_user.id != message_owner.owner_id:
            await cb.answer("❌", show_alert=True)
            return False

        return True


class RDMessageMultipleOwners(msgspec.Struct, kw_only=True, array_like=True):
    owner_ids: frozenset[int]

    @classmethod
    def key(cls, chat_id: int, message_id: int) -> str:
        return f"{cls.__name__}:{chat_id}:{message_id}"

    @classmethod
    async def get(cls, redis: Redis, chat_id: int, message_id: int) -> Self | None:
        data = await redis.get(cls.key(chat_id, message_id))
        if data:
            return msgspec.msgpack.decode(data, type=cls)
        return None

    @classmethod
    async def set(
        cls,
        redis: Redis,
        chat_id: int,
        message_id: int,
        owner_ids: Sequence[int],
        ttl: ExpiryT = timedelta(days=2),
    ) -> int:
        return await redis.setex(
            name=cls.key(chat_id, message_id),
            time=ttl,
            value=msgspec.msgpack.encode(cls(owner_ids=frozenset(owner_ids))),
        )

    @classmethod
    async def delete(cls, redis: Redis, chat_id: int, message_id: int) -> None:
        await redis.delete(cls.key(chat_id, message_id))


class CallbackClickedByMultipleRedisUser(Filter):
    async def __call__(self, cb: CallbackQuery, i18n: I18nContext, redis: Redis) -> bool:
        message_owners = await RDMessageMultipleOwners.get(
            redis,
            cb.message.chat.id,
            cb.message.message_id,
        )
        if not message_owners:
            await cb.message.edit_text(i18n.message.deprecated())
            return False

        if cb.from_user.id not in message_owners.owner_ids:
            await cb.answer("❌", show_alert=True)
            return False

        return True

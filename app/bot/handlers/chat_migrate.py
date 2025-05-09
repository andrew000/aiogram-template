from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, cast

from aiogram import F, Router
from storages.psql import DBChatModel
from storages.redis.chat import RDChatModel, RDChatSettingsModel

if TYPE_CHECKING:
    from aiogram.types import Message
    from redis.asyncio.client import Redis
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

router = Router()


@router.message(F.migrate_from_chat_id)
async def chat_migrate(
    msg: Message,
    db_session: async_sessionmaker[AsyncSession],
    redis: Redis,
) -> None:
    async with db_session() as session:
        async with session.begin():
            chat_model = await session.get(DBChatModel, msg.migrate_from_chat_id)

            chat_model.id = msg.chat.id
            chat_model.migrate_from_chat_id = msg.migrate_from_chat_id
            chat_model.migrate_datetime = datetime.now(tz=UTC)

            await session.commit()

        await RDChatModel.delete(redis, cast(int, msg.migrate_from_chat_id))
        await RDChatSettingsModel.delete(redis, cast(int, msg.migrate_from_chat_id))

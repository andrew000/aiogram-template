from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import KICKED, MEMBER, ChatMemberUpdatedFilter
from sqlalchemy import update
from sqlalchemy.sql.operators import eq
from storages.psql.user import DBUserModel
from storages.redis.user import RDUserModel

if TYPE_CHECKING:
    from aiogram.types import ChatMemberUpdated
    from redis.asyncio import Redis
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

router = Router()
logger = logging.getLogger(__name__)


@router.my_chat_member(ChatMemberUpdatedFilter(KICKED >> MEMBER), F.chat.type == ChatType.PRIVATE)
async def my_chat_member_private_member(
    chat_member: ChatMemberUpdated,
    db_session: async_sessionmaker[AsyncSession],
    redis: Redis,
) -> None:
    async with db_session() as session:
        stmt = (
            update(DBUserModel)
            .where(eq(DBUserModel.id, chat_member.from_user.id))
            .values(pm_active=True)
            .returning(DBUserModel)
        )
        user_model: DBUserModel = await session.scalar(stmt)
        await session.commit()

        user_model: RDUserModel = RDUserModel.from_orm(user_model)
        await user_model.save(redis)

    logger.info("Bot was whitelisted by user %s", chat_member.from_user.id)


@router.my_chat_member(ChatMemberUpdatedFilter(MEMBER >> KICKED), F.chat.type == ChatType.PRIVATE)
async def my_chat_member_private_kicked(
    chat_member: ChatMemberUpdated,
    db_session: async_sessionmaker[AsyncSession],
    redis: Redis,
) -> None:
    async with db_session() as session:
        stmt = (
            update(DBUserModel)
            .where(eq(DBUserModel.id, chat_member.from_user.id))
            .values(pm_active=False)
            .returning(DBUserModel)
        )
        user_model: DBUserModel = await session.scalar(stmt)
        await session.commit()

        user_model: RDUserModel = RDUserModel.from_orm(user_model)
        await user_model.save(redis)

    logger.info("Bot was blacklisted by user %s", chat_member.from_user.id)

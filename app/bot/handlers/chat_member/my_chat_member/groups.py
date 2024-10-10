from __future__ import annotations

import logging
from datetime import timedelta
from secrets import randbelow
from typing import TYPE_CHECKING

from aiogram import Bot, F, Router
from aiogram.enums import ChatType
from aiogram.filters import (
    ADMINISTRATOR,
    IS_NOT_MEMBER,
    LEAVE_TRANSITION,
    MEMBER,
    PROMOTED_TRANSITION,
    RESTRICTED,
    ChatMemberUpdatedFilter,
)

from bot.storages.redis.chat_member import RDChatBotModel

if TYPE_CHECKING:
    from aiogram.types import ChatMemberUpdated
    from aiogram_i18n import I18nContext
    from redis.asyncio.client import Redis

logger = logging.getLogger(__name__)
router = Router()


@router.my_chat_member(
    ChatMemberUpdatedFilter(PROMOTED_TRANSITION),
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
)
async def my_chat_member_promoted_transition(
    chat_member: ChatMemberUpdated,
    bot: Bot,
    i18n: I18nContext,
    redis: Redis,
) -> None:
    bot_model = RDChatBotModel.resolve(chat_id=chat_member.chat.id, chat_member=chat_member.new_chat_member)

    await bot_model.save(redis, timedelta(minutes=45 + randbelow(75 - 45 + 1)))

    logger.info("Bot was promoted in chat %s", chat_member.chat.id)

    await bot.send_message(
        chat_id=chat_member.chat.id,
        text=i18n.my_chat_member.promoted_transition(
            can_delete_messages=bot_model.can_delete_messages,
            can_restrict_members=bot_model.can_restrict_members,
            can_invite_users=bot_model.can_invite_users,
            _path="chat_member/my_chat_member.ftl",
        ),
    )


@router.my_chat_member(
    ChatMemberUpdatedFilter(ADMINISTRATOR >> ADMINISTRATOR),
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
)
async def my_chat_member_administrator_transition(chat_member: ChatMemberUpdated, redis: Redis) -> None:
    bot_model = RDChatBotModel.resolve(chat_id=chat_member.chat.id, chat_member=chat_member.new_chat_member)

    await bot_model.save(redis, timedelta(minutes=45 + randbelow(75 - 45 + 1)))

    logger.info("Bot admin rights was changed in chat %s", chat_member.chat.id)


@router.my_chat_member(
    ChatMemberUpdatedFilter(IS_NOT_MEMBER >> (MEMBER | +RESTRICTED)),
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
)
async def my_chat_member_join_transition(
    chat_member: ChatMemberUpdated,
    bot: Bot,
    i18n: I18nContext,
    redis: Redis,
) -> None:
    bot_model = RDChatBotModel.resolve(chat_id=chat_member.chat.id, chat_member=chat_member.new_chat_member)

    await bot_model.save(redis, timedelta(minutes=45 + randbelow(75 - 45 + 1)))

    logger.info("Bot was added to chat %s", chat_member.chat.id)

    await bot.send_message(
        chat_id=chat_member.chat.id,
        text=i18n.my_chat_member.join_transition(
            can_delete_messages="✅" if bot_model.can_delete_messages else "❌",
            can_restrict_members="✅" if bot_model.can_restrict_members else "❌",
            can_invite_users="✅" if bot_model.can_invite_users else "❌",
            _path="chat_member/my_chat_member.ftl",
        ),
    )


@router.my_chat_member(
    ChatMemberUpdatedFilter(+RESTRICTED >> (MEMBER | +RESTRICTED)),
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
)
async def my_chat_member_unrestricted_transition(chat_member: ChatMemberUpdated, redis: Redis) -> None:
    bot_model = RDChatBotModel.resolve(chat_id=chat_member.chat.id, chat_member=chat_member.new_chat_member)

    await bot_model.save(redis, timedelta(minutes=45 + randbelow(75 - 45 + 1)))

    logger.info("Bot was un/restricted in chat %s", chat_member.chat.id)


@router.my_chat_member(
    ChatMemberUpdatedFilter(ADMINISTRATOR >> (MEMBER | +RESTRICTED)),
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
)
async def my_chat_member_demoted_transition(
    chat_member: ChatMemberUpdated,
    i18n: I18nContext,
    bot: Bot,
    redis: Redis,
) -> None:
    bot_model = RDChatBotModel.resolve(chat_id=chat_member.chat.id, chat_member=chat_member.new_chat_member)

    await bot_model.save(redis, timedelta(minutes=45 + randbelow(75 - 45 + 1)))

    logger.info("Bot was demoted in chat %s", chat_member.chat.id)

    await bot.send_message(
        chat_id=chat_member.chat.id,
        text=i18n.my_chat_member.demoted_transition(_path="chat_member/my_chat_member.ftl"),
    )


@router.my_chat_member(
    ChatMemberUpdatedFilter(LEAVE_TRANSITION),
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
)
async def my_chat_member_leave_transition(chat_member: ChatMemberUpdated, redis: Redis) -> None:
    bot_model = RDChatBotModel.resolve(chat_id=chat_member.chat.id, chat_member=chat_member.new_chat_member)
    await bot_model.save(redis, timedelta(minutes=45 + randbelow(75 - 45 + 1)))

    logger.info("Bot was kicked from chat %s", chat_member.chat.id)

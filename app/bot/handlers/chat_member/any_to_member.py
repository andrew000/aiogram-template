from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Bot, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import JOIN_TRANSITION, MEMBER, ChatMemberUpdatedFilter

from errors.errors import TopicClosedError, resolve_exception
from storages.redis.chat_member import RDChatMemberModel

if TYPE_CHECKING:
    from aiogram.types import ChatMemberUpdated
    from redis.asyncio.client import Redis

    from storages.redis.chat import ChatSettingsModelRD
    from stub import I18nContext

router = Router()


@router.chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def left_to_member(
    chat_member: ChatMemberUpdated,
    bot: Bot,
    i18n: I18nContext,
    redis: Redis,
    chat_settings: ChatSettingsModelRD,
) -> None:
    chat_user_model = RDChatMemberModel.resolve(chat_member.chat.id, chat_member.new_chat_member)
    await chat_user_model.save(redis)

    try:
        with i18n.use_locale(chat_settings.language_code):
            await bot.send_message(
                chat_id=chat_member.chat.id,
                text=i18n.chat_member.join_transition(
                    mention=chat_member.new_chat_member.user.mention_html(),
                    _path="chat_member/chat_member.ftl",
                ),
            )

    except TelegramBadRequest as e:
        e = resolve_exception(e)

        match e:
            case TopicClosedError():
                return

            case _:
                raise


@router.chat_member(ChatMemberUpdatedFilter(MEMBER))
async def any_to_member(chat_member: ChatMemberUpdated, redis: Redis) -> None:
    chat_user_model = RDChatMemberModel.resolve(chat_member.chat.id, chat_member.new_chat_member)
    await chat_user_model.save(redis)

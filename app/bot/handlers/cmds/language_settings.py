from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Router
from aiogram.filters import Command, or_f

from bot.filters.cb_click_by_user import RDMessageOwner
from bot.filters.lazy_filter import LF
from bot.handlers.cbs.language_settings.keyboards import select_language_keyboard

if TYPE_CHECKING:
    from aiogram.types import Message
    from aiogram_i18n import I18nContext
    from redis.asyncio import Redis

router = Router()


@router.message(
    or_f(
        Command("language", "lang"),
        LF("settings-lang", _path="cmds/user_settings.ftl"),
        LF("settings-language", _path="cmds/user_settings.ftl"),
    ),
)
async def language_cmd(msg: Message, i18n: I18nContext, redis: Redis) -> None:
    sent = await msg.answer(
        i18n.settings.select_language.text(_path="cmds/user_settings.ftl"),
        reply_markup=select_language_keyboard(i18n),
    )

    await RDMessageOwner.set(
        redis=redis,
        chat_id=msg.chat.id,
        message_id=sent.message_id,
        owner_id=msg.from_user.id,
    )

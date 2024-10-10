from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiogram import Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.filters.cb_click_by_user import RDMessageOwner
from bot.handlers.cbs.language_settings.keyboards import LanguageWindowCB
from bot.handlers.cbs.universal_close import UniversalWindowCloseCB

if TYPE_CHECKING:
    from aiogram_i18n import I18nContext
    from redis.asyncio import Redis

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart(deep_link=True))
async def start_cmd_with_deep_link(msg: Message, command: CommandObject, i18n: I18nContext) -> None:
    args = command.args.split() if command.args else []
    deep_link = args[0]

    logger.info("User %s started bot with deeplink: %s", msg.from_user.id, deep_link)

    await start_cmd(msg, i18n)


@router.message(CommandStart(deep_link=False))  # Deeplink in False will not work as expected
async def start_cmd(msg: Message, i18n: I18nContext, redis: Redis) -> None:
    sent = await msg.answer(
        i18n.start.start_text(user_mention=msg.from_user.mention_html(), _path="cmds/start.ftl"),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=i18n.change_language.button(_path="cmds/start.ftl"),
                        callback_data=LanguageWindowCB().pack(),
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=i18n.close.windows(),
                        callback_data=UniversalWindowCloseCB().pack(),
                    ),
                ],
            ],
        ),
        disable_web_page_preview=True,
    )

    await RDMessageOwner.set(
        redis=redis,
        chat_id=msg.chat.id,
        message_id=sent.message_id,
        owner_id=msg.from_user.id,
    )

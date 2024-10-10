from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.filters.cb_click_by_user import CallbackClickedByRedisUser, RDMessageOwner
from bot.handlers.cbs.language_settings.keyboards import LanguageWindowCB
from bot.handlers.cbs.universal_close import UniversalWindowCloseCB
from bot.utils.callback_data_prefix_enums import CallbackDataPrefix

if TYPE_CHECKING:
    from aiogram_i18n import I18nContext
    from redis.asyncio import Redis

router = Router()


class GOTOStartCB(CallbackData, prefix=CallbackDataPrefix.goto_start):  # type: ignore[call-arg]
    pass


@router.callback_query(GOTOStartCB.filter(), CallbackClickedByRedisUser())
async def start_cb(cb: CallbackQuery, i18n: I18nContext, redis: Redis) -> None:
    await cb.message.edit_text(
        i18n.start.start_text(user_mention=cb.from_user.mention_html(), _path="cmds/start.ftl"),
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
        chat_id=cb.message.chat.id,
        message_id=cb.message.message_id,
        owner_id=cb.from_user.id,
    )

from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Router
from aiogram.filters.callback_data import CallbackData

from filters.cb_click_by_user import CallbackClickedByRedisUser, RDMessageOwner
from utils.callback_data_prefix_enums import CallbackDataPrefix

if TYPE_CHECKING:
    from aiogram.types import CallbackQuery
    from redis.asyncio import Redis

    from stub import I18nContext

router = Router()


class UniversalWindowCloseCB(CallbackData, prefix=CallbackDataPrefix.universal_close):
    pass


@router.callback_query(UniversalWindowCloseCB.filter(), CallbackClickedByRedisUser())
async def universal_close_cb(cb: CallbackQuery, i18n: I18nContext, redis: Redis) -> None:
    await cb.message.edit_text(i18n.window.closed())

    await RDMessageOwner.delete(
        redis=redis,
        chat_id=cb.message.chat.id,
        message_id=cb.message.message_id,
    )

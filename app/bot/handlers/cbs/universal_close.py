from aiogram import Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery
from aiogram_i18n import I18nContext
from redis.asyncio import Redis

from bot.filters.cb_click_by_user import CallbackClickedByRedisUser, RDMessageOwner
from bot.utils.callback_data_prefix_enums import CallbackDataPrefix

router = Router()


class UniversalWindowCloseCB(CallbackData, prefix=CallbackDataPrefix.universal_close):  # type: ignore[call-arg]
    pass


@router.callback_query(UniversalWindowCloseCB.filter(), CallbackClickedByRedisUser())
async def universal_close_cb(cb: CallbackQuery, i18n: I18nContext, redis: Redis) -> None:
    await cb.message.edit_text(i18n.window.closed())

    await RDMessageOwner.delete(
        redis=redis,
        chat_id=cb.message.chat.id,
        message_id=cb.message.message_id,
    )

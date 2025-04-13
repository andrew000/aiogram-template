from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from filters.cb_click_by_user import CallbackClickedByRedisUser, RDMessageOwner
from handlers.cbs.language_settings.keyboards import (
    LanguageWindowCB,
    SelectLanguageCB,
    select_language_keyboard,
)
from handlers.cbs.start import GOTOStartCB
from sqlalchemy import update
from sqlalchemy.sql.operators import eq
from storages.psql.user import DBUserSettingsModel
from storages.redis.user import RDUserSettingsModel

if TYPE_CHECKING:
    from aiogram.types import CallbackQuery
    from aiogram_i18n import I18nContext
    from redis.asyncio import Redis
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

router = Router()


@router.callback_query(LanguageWindowCB.filter(), CallbackClickedByRedisUser())
async def language_window_cb(
    cb: CallbackQuery,
    i18n: I18nContext,
    redis: Redis,
) -> None:
    await cb.message.edit_text(
        i18n.settings.select_language.text(_path="cmds/user_settings.ftl"),
        reply_markup=select_language_keyboard(i18n),
    )

    await RDMessageOwner.set(
        redis=redis,
        chat_id=cb.message.chat.id,
        message_id=cb.message.message_id,
        owner_id=cb.from_user.id,
    )


@router.callback_query(SelectLanguageCB.filter(), CallbackClickedByRedisUser())
async def language_selected_cb(
    cb: CallbackQuery,
    callback_data: SelectLanguageCB,
    i18n: I18nContext,
    db_session: async_sessionmaker[AsyncSession],
    redis: Redis,
) -> None:
    async with db_session() as session:
        stmt = (
            update(DBUserSettingsModel)
            .where(eq(DBUserSettingsModel.id, cb.from_user.id))
            .values(language_code=callback_data.language.value)
        )
        await session.execute(stmt)
        await session.commit()

    await RDUserSettingsModel.delete(redis, cb.from_user.id)

    await i18n.set_locale(callback_data.language.value)

    await cb.message.edit_text(
        i18n.settings.select_language.changed(
            language_code=callback_data.language.value,
            _path="cmds/user_settings.ftl",
        ),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=i18n.settings.select_language.goto_start(_path="cmds/user_settings.ftl"),
                        callback_data=GOTOStartCB().pack(),
                    ),
                ],
            ],
        ),
    )

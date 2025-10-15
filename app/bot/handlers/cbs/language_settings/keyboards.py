from __future__ import annotations

from typing import TYPE_CHECKING, cast

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.callback_datas import PossibleLanguages, SelectLanguageCB

if TYPE_CHECKING:
    from stub import I18nContext


def select_language_keyboard(i18n: I18nContext) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder().row(
        *[
            InlineKeyboardButton(
                text=i18n.settings.select_language.code(
                    language_code=language.value,
                    _path="cmds/user_settings.ftl",
                ),
                callback_data=SelectLanguageCB(language=language).pack(),
            )
            for language in PossibleLanguages
        ],
        width=2,
    )
    return cast(InlineKeyboardMarkup, builder.as_markup())

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, cast

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.callback_data_prefix_enums import CallbackDataPrefix

if TYPE_CHECKING:
    from aiogram_i18n import I18nContext


class PossibleLanguages(Enum):
    en = "en"  # English
    uk = "uk"  # Ukrainian


class LanguageWindowCB(CallbackData, prefix=CallbackDataPrefix.language_window):
    pass


class SelectLanguageCB(CallbackData, prefix=CallbackDataPrefix.select_language):
    language: PossibleLanguages


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

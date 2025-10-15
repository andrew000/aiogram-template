from __future__ import annotations

from enum import Enum
from typing import ClassVar, TypeVar

from aiogram.filters.callback_data import CallbackData

from utils.callback_data_prefix_enums import CallbackDataPrefix

# Type that is a subclass of CallbackData and has an owner_id attribute of type int
OwnerCallbackData = TypeVar("OwnerCallbackData", bound=CallbackData)
OwnerCallbackData.owner_id = ClassVar[int]


class PossibleLanguages(Enum):
    en = "en"  # English
    uk = "uk"  # Ukrainian


class LanguageWindowCB(CallbackData, prefix=CallbackDataPrefix.language_window):
    pass


class SelectLanguageCB(CallbackData, prefix=CallbackDataPrefix.select_language):
    language: PossibleLanguages

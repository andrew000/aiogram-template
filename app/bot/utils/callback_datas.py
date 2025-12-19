from __future__ import annotations

from enum import Enum
from typing import Protocol, runtime_checkable

from aiogram.filters.callback_data import CallbackData

from utils.callback_data_prefix_enums import CallbackDataPrefix


@runtime_checkable
class OwnerCallbackData(Protocol):
    owner_id: int


class PossibleLanguages(Enum):
    en = "en"  # English
    uk = "uk"  # Ukrainian


class LanguageWindowCB(CallbackData, prefix=CallbackDataPrefix.language_window):
    pass


class SelectLanguageCB(CallbackData, prefix=CallbackDataPrefix.select_language):
    language: PossibleLanguages

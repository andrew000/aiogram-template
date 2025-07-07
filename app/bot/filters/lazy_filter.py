from __future__ import annotations

from typing import TYPE_CHECKING, Any

from aiogram.filters import Filter

if TYPE_CHECKING:
    from aiogram.types import Message
    from aiogram_i18n import I18nContext


class LazyFilter(Filter):
    """
    I don't like `LazyFilter` provided by `aiogram-i18n`, so I've created my own version of
    it.
    """

    def __init__(self, key: str, casefold: bool = True, **__: Any) -> None:
        self.key = key  # FTL key
        self.casefold = casefold
        self.values: frozenset[str] = frozenset()  # FTL values
        self._is_initiated: bool = False

    def startup(self, i18n: I18nContext) -> None:
        if self._is_initiated:
            return

        self.values = frozenset(
            {i18n.core.get(self.key, locale) for locale in i18n.core.available_locales},
        )

        if self.casefold:
            self.values = frozenset({value.casefold() for value in self.values})

        self._is_initiated = True

    async def __call__(self, event: Message, i18n: I18nContext) -> bool:
        self.startup(
            i18n,
        )  # Temporary solution, because of https://github.com/aiogram/i18n/issues/38

        if not (text := (event.text or event.caption)):
            return False

        if self.casefold:
            text = text.casefold()

        return text in self.values


LF: type[LazyFilter] = LazyFilter

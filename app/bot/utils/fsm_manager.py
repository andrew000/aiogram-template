from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram_i18n.managers.base import BaseManager
from domain.user.repo import CachedUserSettingsRepository
from domain.user.service import CachedUserSettingsService

if TYPE_CHECKING:
    from aiogram.types import User
    from domain.user.dto import UserSettingsReadDTO
    from redis.asyncio import Redis


class FSMManager(BaseManager):
    key: str

    def __init__(self, key: str = "locale") -> None:
        super().__init__()
        self.key = key

    async def get_locale(
        self,
        event_from_user: User,
        redis: Redis,
        user_settings_dto: UserSettingsReadDTO | None = None,
    ) -> str:
        if user_settings_dto:
            locale: str = user_settings_dto.language_code

        else:
            cached_user_settings_service = CachedUserSettingsService(
                repo=CachedUserSettingsRepository(redis=redis)
            )
            cached_user_settings_dto: (
                UserSettingsReadDTO | None
            ) = await cached_user_settings_service.get(user_id=event_from_user.id)

            if cached_user_settings_dto:
                locale: str = cached_user_settings_dto.language_code

            else:
                locale: str = self.default_locale or "en"

        return locale

    async def set_locale(self, locale: str) -> None: ...

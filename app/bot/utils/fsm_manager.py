from aiogram.types import User
from aiogram_i18n.managers.base import BaseManager
from redis.asyncio import Redis

from bot.storages.redis.user.user_settings_model import RDUserSettingsModel


class FSMManager(BaseManager):
    key: str

    def __init__(self, key: str = "locale") -> None:
        super().__init__()
        self.key = key

    async def get_locale(
        self,
        event_from_user: User,
        redis: Redis,
        user_settings: RDUserSettingsModel | None = None,
    ) -> str:
        if user_settings:
            locale: str = user_settings.language_code

        else:
            user_settings = await RDUserSettingsModel.get(redis, event_from_user.id)

            if user_settings:
                locale: str = user_settings.language_code

            else:
                locale: str = self.default_locale

        return locale

    async def set_locale(self, locale: str) -> None: ...

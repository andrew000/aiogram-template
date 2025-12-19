from __future__ import annotations

from typing import TYPE_CHECKING, Final

import msgspec
from domain.user.dto import (
    UserReadDTO,
    UserSettingsCreateDTO,
    UserSettingsReadDTO,
    UserSettingsUpdateDTO,
    UserUpdateDTO,
)

if TYPE_CHECKING:
    from domain.user.dto import UserCreateDTO
    from domain.user.interface import (
        ICachedUserRepository,
        ICachedUserSettingsRepository,
        IUserRepository,
        IUserSettingsRepository,
    )

ENCODER: Final[msgspec.msgpack.Encoder] = msgspec.msgpack.Encoder()


class UserService:
    def __init__(self, repo: IUserRepository):
        self.repo = repo

    async def upsert(self, user_dto: UserCreateDTO) -> UserReadDTO:
        if user_dto.username:
            existing_user_by_username = await self.repo.get_by_username(username=user_dto.username)

            if existing_user_by_username and existing_user_by_username.id != user_dto.id:
                await self.repo.update_username(
                    user_id=existing_user_by_username.id, new_username=None
                )

        existing_user = await self.repo.get_by_id(user_dto.id)

        if not existing_user:
            created_user = await self.repo.upsert(user_dto)
            return msgspec.convert(created_user, UserReadDTO, from_attributes=True)

        updated_user = await self.repo.update(user_dto=UserUpdateDTO.from_create_dto(user_dto))
        return msgspec.convert(updated_user, UserReadDTO, from_attributes=True)

    async def get_user_by_id(self, user_id: int) -> UserReadDTO | None:
        user = await self.repo.get_by_id(user_id)
        if user:
            return msgspec.convert(user, UserReadDTO, from_attributes=True)
        return None

    async def get_user_by_username(self, username: str) -> UserReadDTO | None:
        user = await self.repo.get_by_username(username)
        if user:
            return msgspec.convert(user, UserReadDTO, from_attributes=True)
        return None

    async def update(self, user_dto: UserUpdateDTO) -> UserReadDTO:
        updated_user = await self.repo.update(user_dto)
        return msgspec.convert(updated_user, UserReadDTO, from_attributes=True)


class CachedUserService:
    def __init__(self, repo: ICachedUserRepository):
        self.repo = repo

    async def upsert(self, user_dto: UserReadDTO) -> UserReadDTO:
        """user_dto must be `UserReadDTO` due to caching purposes."""
        cached_user = await self.repo.upsert(user_dto)
        return msgspec.convert(cached_user, UserReadDTO, from_attributes=True)

    async def get_user_by_id(self, user_id: int) -> UserReadDTO | None:
        cached_user = await self.repo.get(user_id)
        if cached_user:
            return msgspec.convert(cached_user, UserReadDTO, from_attributes=True)
        return None


class UserSettingsService:
    def __init__(self, repo: IUserSettingsRepository):
        self.repo = repo

    async def upsert(self, user_settings_dto: UserSettingsCreateDTO) -> UserSettingsReadDTO:
        user_settings = await self.repo.upsert(user_settings_dto)
        return msgspec.convert(user_settings, UserSettingsReadDTO, from_attributes=True)

    async def get(self, user_id: int) -> UserSettingsReadDTO | None:
        user_settings = await self.repo.get(user_id)
        if user_settings:
            return msgspec.convert(user_settings, UserSettingsReadDTO, from_attributes=True)
        return None

    async def update(self, user_settings_dto: UserSettingsUpdateDTO) -> UserSettingsReadDTO:
        updated_user_settings = await self.repo.update(user_settings_dto)
        return msgspec.convert(updated_user_settings, UserSettingsReadDTO, from_attributes=True)


class CachedUserSettingsService:
    def __init__(self, repo: ICachedUserSettingsRepository):
        self.repo = repo

    async def upsert(self, user_settings_dto: UserSettingsReadDTO) -> UserSettingsReadDTO:
        """user_settings_dto must be `UserSettingsReadDTO` due to caching purposes."""
        cached_user_settings = await self.repo.upsert(user_settings_dto)
        return msgspec.convert(cached_user_settings, UserSettingsReadDTO, from_attributes=True)

    async def get(self, user_id: int) -> UserSettingsReadDTO | None:
        cached_user_settings = await self.repo.get(user_id)
        if cached_user_settings:
            return msgspec.convert(cached_user_settings, UserSettingsReadDTO, from_attributes=True)
        return None

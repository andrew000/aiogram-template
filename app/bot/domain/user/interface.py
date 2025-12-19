from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db.psql.user.models import UserModel, UserSettingsModel
    from db.redis.user import CachedUserRD, CachedUserSettingsRD
    from domain.user.dto import (
        UserCreateDTO,
        UserReadDTO,
        UserSettingsCreateDTO,
        UserSettingsReadDTO,
        UserSettingsUpdateDTO,
        UserUpdateDTO,
    )


class IUserRepository(ABC):
    @abstractmethod
    async def upsert(self, user_dto: UserCreateDTO) -> UserModel: ...

    @abstractmethod
    async def update_username(self, user_id: int, new_username: str | None) -> None: ...

    @abstractmethod
    async def get_by_id(self, user_id: int) -> UserModel | None: ...

    @abstractmethod
    async def get_by_username(self, username: str) -> UserModel | None: ...

    @abstractmethod
    async def update(self, user_dto: UserUpdateDTO) -> UserModel: ...


class ICachedUserRepository(ABC):
    @classmethod
    @abstractmethod
    def _key(cls, user_id: int | str) -> str: ...

    @abstractmethod
    async def upsert(self, user_dto: UserReadDTO) -> CachedUserRD:
        """`user_dto` must be `UserReadDTO` due to caching purposes."""

    @abstractmethod
    async def get(self, user_id: int) -> CachedUserRD | None: ...

    @abstractmethod
    async def delete(self, user_id: int) -> None: ...

    @abstractmethod
    async def delete_all_cached_users(self) -> None: ...


class IUserSettingsRepository(ABC):
    @abstractmethod
    async def upsert(self, user_settings_dto: UserSettingsCreateDTO) -> UserSettingsModel: ...

    @abstractmethod
    async def get(self, user_id: int) -> UserSettingsModel | None: ...

    @abstractmethod
    async def update(self, user_settings_dto: UserSettingsUpdateDTO) -> UserSettingsModel: ...


class ICachedUserSettingsRepository(ABC):
    @classmethod
    @abstractmethod
    def _key(cls, user_id: int | str) -> str: ...

    @abstractmethod
    async def upsert(self, user_settings_dto: UserSettingsReadDTO) -> CachedUserSettingsRD:
        """`user_settings_dto` must be `UserSettingsReadDTO` due to caching purposes."""

    @abstractmethod
    async def get(self, user_id: int) -> CachedUserSettingsRD | None: ...

    @abstractmethod
    async def delete(self, user_id: int) -> None: ...

    @abstractmethod
    async def delete_all_cached_user_settings(self) -> None: ...

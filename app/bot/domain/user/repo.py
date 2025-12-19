from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Final

import msgspec
from db.psql import UserModel, UserSettingsModel
from db.redis import CachedUserRD
from db.redis.user import CachedUserSettingsRD
from domain.user.interface import (
    ICachedUserRepository,
    ICachedUserSettingsRepository,
    IUserRepository,
    IUserSettingsRepository,
)
from sqlalchemy import select, update

if TYPE_CHECKING:
    from domain.user.dto import (
        UserCreateDTO,
        UserReadDTO,
        UserSettingsCreateDTO,
        UserSettingsUpdateDTO,
        UserUpdateDTO,
    )
    from redis.asyncio import Redis
    from sqlalchemy.ext.asyncio import AsyncSession


ENCODER: Final[msgspec.msgpack.Encoder] = msgspec.msgpack.Encoder()


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert(self, user_dto: UserCreateDTO) -> UserModel:
        new_user = UserModel(
            id=user_dto.id,
            username=user_dto.username,
            first_name=user_dto.first_name,
            last_name=user_dto.last_name,
        )
        self.session.add(new_user)
        await self.session.flush()
        return new_user

    async def get_by_id(self, user_id: int) -> UserModel | None:
        return await self.session.get(entity=UserModel, ident=user_id)

    async def get_by_username(self, username: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.username == username)
        return await self.session.scalar(stmt)

    async def update_username(self, user_id: int, new_username: str | None) -> None:
        stmt = update(UserModel).where(UserModel.id == user_id).values(username=new_username)
        await self.session.execute(stmt)

    async def update(self, user_dto: UserUpdateDTO) -> UserModel:
        user_model: UserModel | None = await self.get_by_id(user_dto.id)

        if not user_model:
            msg = f"User with id={user_dto.id} does not exist."
            raise ValueError(msg)

        for field in user_dto.__struct_fields__:
            setattr(user_model, field, getattr(user_dto, field))

        user_model.last_active = datetime.now(tz=UTC).replace(tzinfo=None)

        return user_model


class CachedUserRepository(ICachedUserRepository):
    def __init__(self, redis: Redis):
        self.redis = redis

    @classmethod
    def _key(cls, user_id: int | str) -> str:
        return f"{CachedUserRD.__name__}:{user_id}"

    async def upsert(self, user_dto: UserReadDTO) -> CachedUserRD:
        """`user_dto` must be `UserReadDTO` due to caching purposes."""
        cached_user = CachedUserRD(
            id=user_dto.id,
            username=user_dto.username,
            first_name=user_dto.first_name,
            last_name=user_dto.last_name,
            registration_datetime=user_dto.registration_datetime,
            pm_active=user_dto.pm_active,
            last_active=user_dto.last_active,
        )

        await self.redis.setex(
            name=self._key(user_dto.id),
            time=timedelta(days=1),
            value=ENCODER.encode(cached_user),
        )

        return cached_user

    async def get(self, user_id: int) -> CachedUserRD | None:
        data = await self.redis.get(self._key(user_id))
        if data:
            return msgspec.msgpack.decode(data, type=CachedUserRD)
        return None

    async def delete(self, user_id: int) -> None:
        await self.redis.delete(self._key(user_id))

    async def delete_all_cached_users(self) -> None:
        keys = await self.redis.keys(f"{CachedUserRD.__name__}:*")
        if keys:
            await self.redis.delete(*keys) if keys else 0


class UserSettingsRepository(IUserSettingsRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert(self, user_settings_dto: UserSettingsCreateDTO) -> UserSettingsModel:
        existing_settings: UserSettingsModel | None = await self.session.get(
            entity=UserSettingsModel, ident=user_settings_dto.id
        )
        if existing_settings:
            return existing_settings

        new_settings = UserSettingsModel(
            id=user_settings_dto.id,
            language_code=user_settings_dto.language_code,
            gender=user_settings_dto.gender,
            is_banned=user_settings_dto.is_banned,
        )
        self.session.add(new_settings)

        await self.session.flush()
        return new_settings

    async def get(self, user_id: int) -> UserSettingsModel | None:
        return await self.session.get(entity=UserSettingsModel, ident=user_id)

    async def update(self, user_settings_dto: UserSettingsUpdateDTO) -> UserSettingsModel:
        settings_model: UserSettingsModel | None = await self.get(user_settings_dto.id)

        if not settings_model:
            msg = f"UserSettings with id {user_settings_dto.id} does not exist."
            raise ValueError(msg)

        if settings_model:
            for field in user_settings_dto.__struct_fields__:
                setattr(settings_model, field, getattr(user_settings_dto, field))

        return settings_model


class CachedUserSettingsRepository(ICachedUserSettingsRepository):
    def __init__(self, redis: Redis):
        self.redis = redis

    @classmethod
    def _key(cls, user_id: int | str) -> str:
        return f"{CachedUserSettingsRD.__name__}:{user_id}"

    async def upsert(self, user_settings_dto: UserSettingsCreateDTO) -> CachedUserSettingsRD:
        cached_settings = CachedUserSettingsRD(
            id=user_settings_dto.id,
            language_code=user_settings_dto.language_code,
            gender=user_settings_dto.gender,
            is_banned=user_settings_dto.is_banned,
        )
        await self.redis.setex(
            name=self._key(user_settings_dto.id),
            time=timedelta(days=1),
            value=ENCODER.encode(cached_settings),
        )
        return cached_settings

    async def get(self, user_id: int) -> CachedUserSettingsRD | None:
        data = await self.redis.get(self._key(user_id))
        if data:
            return msgspec.msgpack.decode(data, type=CachedUserSettingsRD)
        return None

    async def delete(self, user_id: int) -> None:
        await self.redis.delete(self._key(user_id))

    async def delete_all_cached_user_settings(self) -> None:
        keys = await self.redis.keys(f"{CachedUserSettingsRD.__name__}:*")
        await self.redis.delete(*keys) if keys else 0

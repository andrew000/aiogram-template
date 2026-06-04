from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, cast

from aiogram.enums import ChatType
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.operators import eq, ne

from storages.psql.user import UserModel, UserSettingsModel
from storages.redis.user import UserRD, UserSettingsRD

if TYPE_CHECKING:
    from aiogram.types import Chat, User
    from redis.asyncio.client import Redis
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class UserProfileService:
    def __init__(self, db_pool: async_sessionmaker[AsyncSession], redis: Redis) -> None:
        self._db_pool = db_pool
        self._redis = redis

    async def get_or_create(self, *, user: User, chat: Chat) -> tuple[UserRD, UserSettingsRD]:
        user_model: UserRD | None = await UserRD.get(self._redis, user.id)
        user_settings: UserSettingsRD | None = await UserSettingsRD.get(self._redis, user.id)

        if user_model and user_settings:
            return user_model, user_settings

        async with self._db_pool() as session:
            user_model_db = await self._upsert_user(user=user, chat=chat, session=session)
            user_settings_db = await self._upsert_user_settings(user_id=user.id, session=session)
            await session.commit()

        user_model = UserRD.from_orm(user_model_db)
        user_settings = UserSettingsRD.from_orm(user_settings_db)

        if TYPE_CHECKING:
            assert user_model
            assert user_settings

        await user_model.save(self._redis)
        await user_settings.save(self._redis)

        return user_model, user_settings

    async def set_private_active(self, *, user_id: int, is_active: bool) -> UserRD | None:
        async with self._db_pool() as session:
            stmt = (
                update(UserModel)
                .where(eq(UserModel.id, user_id))
                .values(pm_active=is_active)
                .returning(UserModel)
            )
            user_model_db: UserModel | None = await session.scalar(stmt)
            await session.commit()

        if user_model_db is None:
            await UserRD.delete(self._redis, user_id)
            return None

        user_model = UserRD.from_orm(user_model_db)
        await user_model.save(self._redis)
        return user_model

    async def set_language(self, *, user_id: int, language_code: str) -> None:
        async with self._db_pool() as session:
            stmt = (
                update(UserSettingsModel)
                .where(eq(UserSettingsModel.id, user_id))
                .values(language_code=language_code)
            )
            await session.execute(stmt)
            await session.commit()

        await UserSettingsRD.delete(self._redis, user_id)

    async def _upsert_user(
        self,
        *,
        user: User,
        chat: Chat,
        session: AsyncSession,
    ) -> UserModel:
        if user.username:
            stmt = select(UserModel).where(
                eq(UserModel.username, user.username),
                ne(UserModel.id, user.id),
            )
            another_user: UserModel | None = await session.scalar(stmt)

            if another_user:
                stmt = (
                    update(UserModel)
                    .where(eq(UserModel.id, another_user.id))
                    .values(
                        username=None,
                    )
                )
                await session.execute(stmt)

        stmt = select(UserModel).where(eq(UserModel.id, user.id))
        user_model: UserModel | None = await session.scalar(stmt)
        now = datetime.now(tz=UTC).replace(tzinfo=None)

        if user_model is None:
            stmt = (
                insert(UserModel)
                .values(
                    id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    pm_active=chat.type == ChatType.PRIVATE,
                )
                .on_conflict_do_update(
                    index_elements=["id"],
                    set_={
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "last_active": now,
                    },
                )
                .returning(UserModel)
            )
            user_model = await session.scalar(stmt)

        else:
            user_model.username = user.username
            user_model.first_name = user.first_name
            user_model.last_name = user.last_name
            user_model.last_active = now

        return cast(UserModel, user_model)

    async def _upsert_user_settings(
        self,
        *,
        user_id: int,
        session: AsyncSession,
    ) -> UserSettingsModel:
        stmt = (
            insert(UserSettingsModel)
            .values(id=user_id)
            .on_conflict_do_update(
                index_elements=["id"],
                set_={"language_code": UserSettingsModel.language_code},
            )
            .returning(UserSettingsModel)
        )
        return cast(UserSettingsModel, await session.scalar(stmt))

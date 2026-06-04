from __future__ import annotations

from typing import TYPE_CHECKING, cast

from aiogram.enums import ChatType
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.operators import eq, ne

from storages.psql.chat import ChatModel, ChatSettingsModel
from storages.redis.chat import ChatModelRD, ChatSettingsModelRD

if TYPE_CHECKING:
    from aiogram.types import Chat
    from redis.asyncio.client import Redis
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class ChatProfileService:
    def __init__(self, db_pool: async_sessionmaker[AsyncSession], redis: Redis) -> None:
        self._db_pool = db_pool
        self._redis = redis

    async def get_or_create(self, chat: Chat) -> tuple[ChatModelRD, ChatSettingsModelRD]:
        chat_model: ChatModelRD | None = await ChatModelRD.get(self._redis, chat.id)
        chat_settings: ChatSettingsModelRD | None = await ChatSettingsModelRD.get(
            self._redis,
            chat.id,
        )

        if chat_model and chat_settings:
            return chat_model, chat_settings

        async with self._db_pool() as session:
            chat_model_db = await self._upsert_chat(chat=chat, session=session)
            chat_settings_db = await self._get_or_create_chat_settings(
                chat_id=chat.id,
                session=session,
            )
            await session.commit()

        chat_model = ChatModelRD.from_orm(chat_model_db)
        chat_settings = ChatSettingsModelRD.from_orm(chat_settings_db)

        if TYPE_CHECKING:
            assert chat_model
            assert chat_settings

        await chat_model.save(self._redis)
        await chat_settings.save(self._redis)

        return chat_model, chat_settings

    @staticmethod
    async def _upsert_chat(*, chat: Chat, session: AsyncSession) -> ChatModel:
        if chat.username:
            stmt = select(ChatModel).where(
                eq(ChatModel.username, chat.username),
                ne(ChatModel.id, chat.id),
            )
            another_chat: ChatModel | None = await session.scalar(stmt)

            if another_chat:
                stmt = (
                    update(ChatModel)
                    .where(eq(ChatModel.id, another_chat.id))
                    .values(
                        username=None,
                    )
                )
                await session.execute(stmt)

        stmt = select(ChatModel).where(eq(ChatModel.id, chat.id))
        chat_model: ChatModel | None = await session.scalar(stmt)
        member_count = await chat.get_member_count()

        if chat_model is None:
            stmt = (
                insert(ChatModel)
                .values(
                    id=chat.id,
                    chat_type=ChatType(chat.type),
                    title=chat.title,
                    username=chat.username,
                    member_count=member_count,
                )
                .on_conflict_do_update(
                    index_elements=["id"],
                    set_={
                        "chat_type": ChatType(chat.type),
                        "title": chat.title,
                        "username": chat.username,
                        "member_count": member_count,
                    },
                )
                .returning(ChatModel)
            )
            chat_model = await session.scalar(stmt)

        else:
            chat_model.title = chat.title
            chat_model.username = chat.username
            chat_model.member_count = member_count

        return cast(ChatModel, chat_model)

    @staticmethod
    async def _get_or_create_chat_settings(
        *,
        chat_id: int,
        session: AsyncSession,
    ) -> ChatSettingsModel:
        stmt = select(ChatSettingsModel).where(eq(ChatSettingsModel.id, chat_id))
        chat_settings_model: ChatSettingsModel | None = await session.scalar(stmt)

        if chat_settings_model is None:
            stmt = (
                insert(ChatSettingsModel)
                .values(id=chat_id, language_code="en")
                .returning(ChatSettingsModel)
            )
            chat_settings_model = await session.scalar(stmt)

        return cast(ChatSettingsModel, chat_settings_model)

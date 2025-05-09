from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from aiogram import BaseMiddleware
from aiogram.enums import ChatType
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.operators import eq
from storages.psql.chat import DBChatModel, DBChatSettingsModel
from storages.redis.chat import RDChatModel, RDChatSettingsModel

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from aiogram.types import Chat, TelegramObject, Update, User
    from redis.asyncio.client import Redis
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

ALLOWED_CHAT_TYPES: frozenset[ChatType] = frozenset(
    (ChatType.CHANNEL, ChatType.GROUP, ChatType.SUPERGROUP),
)


async def _get_or_create_chat(chat: Chat, session: AsyncSession) -> DBChatModel:
    stmt = select(DBChatModel).where(eq(DBChatModel.id, chat.id))
    chat_model: DBChatModel | None = await session.scalar(stmt)

    if not chat_model:
        stmt = (
            insert(DBChatModel)
            .values(
                id=chat.id,
                chat_type=chat.type,
                title=chat.title,
                username=chat.username,
            )
            .returning(DBChatModel)
        )
        chat_model = await session.scalar(stmt)

    else:
        chat_model.chat_type = chat.type
        chat_model.title = chat.title
        chat_model.username = chat.username

    return cast(DBChatModel, chat_model)


async def _get_or_create_chat_settings(
    chat: Chat,
    user: User,
    session: AsyncSession,
) -> DBChatSettingsModel:
    stmt = select(DBChatSettingsModel).where(eq(DBChatSettingsModel.id, chat.id))
    chat_settings_model: DBChatSettingsModel | None = await session.scalar(stmt)

    if not chat_settings_model:
        stmt = (
            insert(DBChatSettingsModel)
            .values(id=chat.id, language_code=user.language_code or "en")
            .returning(DBChatSettingsModel)
        )
        chat_settings_model = await session.scalar(stmt)

    return cast(DBChatSettingsModel, chat_settings_model)


async def _get_chat_model(
    db_session: async_sessionmaker[AsyncSession],
    redis: Redis,
    chat: Chat,
    user: User,
) -> tuple[RDChatModel, RDChatSettingsModel]:
    chat_model: RDChatModel | None = await RDChatModel.get(redis, chat.id)
    chat_settings: RDChatSettingsModel | None = await RDChatSettingsModel.get(redis, chat.id)

    if chat_model and chat_settings:
        return chat_model, chat_settings

    async with db_session() as session:
        async with session.begin():
            chat_model: DBChatModel = await _get_or_create_chat(chat, session)
            chat_settings: DBChatSettingsModel = await _get_or_create_chat_settings(
                chat,
                user,
                session,
            )

            await session.commit()

        chat_model = RDChatModel.from_orm(cast(DBChatModel, chat_model))
        chat_settings = RDChatSettingsModel.from_orm(cast(DBChatSettingsModel, chat_settings))

        await chat_model.save(redis)
        await chat_settings.save(redis)

    return chat_model, chat_settings


class CheckChatMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Update,  # type: ignore[override]
        data: dict[str, Any],
    ) -> Any:
        chat: Chat = data.get("event_chat")
        user: User = data.get("event_from_user")

        match event.event_type:
            case "message" | "callback_query" | "my_chat_member" | "chat_member":
                if chat.type in ALLOWED_CHAT_TYPES:
                    data["chat_model"], data["chat_settings"] = await _get_chat_model(
                        data["db_session"],
                        data["redis"],
                        chat,
                        user,
                    )
            case _:
                pass

        return await handler(event, data)

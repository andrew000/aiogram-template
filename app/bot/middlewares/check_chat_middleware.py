from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from aiogram import BaseMiddleware
from aiogram.enums import ChatType
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.operators import eq, ne

from storages.psql.chat import ChatModel, ChatSettingsModel
from storages.redis.chat import ChatModelRD, ChatSettingsModelRD

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from aiogram.types import Chat, TelegramObject, Update
    from redis.asyncio.client import Redis
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

ALLOWED_CHAT_TYPES: frozenset[ChatType] = frozenset(
    (ChatType.GROUP, ChatType.SUPERGROUP),
)


async def _create_chat(chat: Chat, session: AsyncSession) -> ChatModel:
    if chat.username:
        stmt = select(ChatModel).where(
            eq(ChatModel.username, chat.username), ne(ChatModel.id, chat.id)
        )
        another_chat: ChatModel | None = await session.scalar(stmt)

        if another_chat:
            stmt = update(ChatModel).where(eq(ChatModel.id, another_chat.id)).values(username=None)
            await session.execute(stmt)

    stmt = select(ChatModel).where(eq(ChatModel.id, chat.id))
    chat_model: ChatModel | None = await session.scalar(stmt)

    if not chat_model:
        stmt = (
            insert(ChatModel)
            .values(
                id=chat.id,
                chat_type=ChatType(chat.type),
                title=chat.title,
                username=chat.username,
                member_count=(member_count := await chat.get_member_count()),
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
        chat_model.member_count = await chat.get_member_count()

    return cast(ChatModel, chat_model)


async def _create_chat_settings(
    chat_id: int,
    session: AsyncSession,
) -> ChatSettingsModel:
    stmt = select(ChatSettingsModel).where(eq(ChatSettingsModel.id, chat_id))
    chat_settings_model: ChatSettingsModel | None = await session.scalar(stmt)

    if not chat_settings_model:
        stmt = (
            insert(ChatSettingsModel)
            .values(id=chat_id, language_code="en")
            .returning(ChatSettingsModel)
        )
        chat_settings_model = await session.scalar(stmt)

    return cast(ChatSettingsModel, chat_settings_model)


async def _get_chat_model(
    db_pool: async_sessionmaker[AsyncSession],
    redis: Redis,
    chat: Chat,
) -> tuple[ChatModelRD, ChatSettingsModelRD]:
    chat_model: ChatModelRD | None = await ChatModelRD.get(redis, chat.id)
    chat_settings: ChatSettingsModelRD | None = await ChatSettingsModelRD.get(redis, chat.id)

    if chat_model and chat_settings:
        return chat_model, chat_settings

    async with db_pool() as session:
        async with session.begin():
            chat_model: ChatModel = await _create_chat(chat=chat, session=session)
            chat_settings: ChatSettingsModel = await _create_chat_settings(
                chat_id=chat.id, session=session
            )

            await session.commit()

        chat_model = ChatModelRD.from_orm(cast(ChatModel, chat_model))
        chat_settings = ChatSettingsModelRD.from_orm(cast(ChatSettingsModel, chat_settings))

        await chat_model.save(redis)
        await chat_settings.save(redis)

    return chat_model, chat_settings


class CheckChatMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        chat: Chat = data["event_chat"]

        if TYPE_CHECKING:
            assert isinstance(event, Update)

        match event.event_type:
            case "message":
                if chat.type in ALLOWED_CHAT_TYPES:
                    if (
                        event.message.migrate_to_chat_id
                        or event.message.group_chat_created
                        or event.message.supergroup_chat_created
                    ):
                        return None

                    if event.message.migrate_from_chat_id:
                        return await handler(event, data)

                    data["chat_model"], data["chat_settings"] = await _get_chat_model(
                        db_pool=data["db_pool"],
                        redis=data["redis"],
                        chat=chat,
                    )

            case "callback_query" | "my_chat_member" | "chat_member":
                if chat.type in ALLOWED_CHAT_TYPES:
                    data["chat_model"], data["chat_settings"] = await _get_chat_model(
                        db_pool=data["db_pool"],
                        redis=data["redis"],
                        chat=chat,
                    )

            case _:
                pass

        return await handler(event, data)

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramAPIError
from domain.chat.dto import ChatCreateDTO, ChatSettingsCreateDTO
from domain.chat.repo import (
    CachedChatRepository,
    CachedChatSettingsRepository,
    ChatRepository,
    ChatSettingsRepository,
)
from domain.chat.service import (
    CachedChatService,
    CachedChatSettingsService,
    ChatService,
    ChatSettingsService,
)

from errors.errors import ChannelPrivateError, resolve_exception

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from aiogram.types import Chat, TelegramObject, Update
    from domain.chat.dto import ChatReadDTO, ChatSettingsReadDTO
    from redis.asyncio.client import Redis
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from utils.aiogram_data import AiogramData

ALLOWED_CHAT_TYPES: frozenset[ChatType] = frozenset(
    (ChatType.GROUP, ChatType.SUPERGROUP),
)


async def _get_chat(
    *,
    db_pool: async_sessionmaker[AsyncSession],
    redis: Redis,
    chat: Chat,
) -> tuple[ChatReadDTO, ChatSettingsReadDTO]:
    # chat_model: ChatModelRD | None = await ChatModelRD.get(redis, chat.id)
    # chat_settings: ChatSettingsModelRD | None = await ChatSettingsModelRD.get(redis, chat.id)

    cached_chat_service = CachedChatService(repo=CachedChatRepository(redis=redis))
    cached_chat_dto: ChatReadDTO | None = await cached_chat_service.get_chat_by_id(chat_id=chat.id)

    cached_chat_settings_service = CachedChatSettingsService(
        repo=CachedChatSettingsRepository(redis=redis)
    )
    cached_chat_settings_dto: ChatSettingsReadDTO | None = await cached_chat_settings_service.get(
        chat_id=chat.id
    )

    if cached_chat_dto and cached_chat_settings_dto:
        return cached_chat_dto, cached_chat_settings_dto

    member_count = 0

    try:
        member_count = await chat.get_member_count()
    except TelegramAPIError as e:
        match resolve_exception(e):
            case ChannelPrivateError():
                pass
            case _:
                raise

    async with db_pool() as session:
        async with session.begin():
            chat_service = ChatService(repo=ChatRepository(session=session))
            chat_dto = await chat_service.upsert(
                chat_dto=ChatCreateDTO(
                    id=chat.id,
                    chat_type=ChatType(chat.type),
                    title=chat.title,
                    username=chat.username,
                    member_count=member_count,
                )
            )

            chat_settings_service = ChatSettingsService(
                repo=ChatSettingsRepository(session=session)
            )
            chat_settings_dto = await chat_settings_service.upsert(
                chat_settings_dto=ChatSettingsCreateDTO(id=chat.id)
            )

        cached_chat_dto: ChatReadDTO = await cached_chat_service.upsert(chat_dto=chat_dto)
        cached_chat_settings_dto: ChatSettingsReadDTO = await cached_chat_settings_service.upsert(
            chat_settings_dto=chat_settings_dto
        )

    return cached_chat_dto, cached_chat_settings_dto


class CheckChatMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, AiogramData], Awaitable[Any]],
        event: TelegramObject,
        data: AiogramData,
    ) -> Any:  # ty:ignore[invalid-method-override]
        chat: Chat = data["event_chat"]

        if TYPE_CHECKING:
            assert isinstance(event, Update)

        if event.message and chat.type in ALLOWED_CHAT_TYPES:
            if (
                event.message.migrate_to_chat_id
                or event.message.group_chat_created
                or event.message.supergroup_chat_created
            ):
                return None

            if event.message.migrate_from_chat_id:
                return await handler(event, data)

            data["chat_dto"], data["chat_settings_dto"] = await _get_chat(
                db_pool=data["db_pool"],
                redis=data["redis"],
                chat=chat,
            )

        elif event.callback_query or event.my_chat_member or event.chat_member:
            if chat.type in ALLOWED_CHAT_TYPES:
                data["chat_dto"], data["chat_settings_dto"] = await _get_chat(
                    db_pool=data["db_pool"],
                    redis=data["redis"],
                    chat=chat,
                )

        return await handler(event, data)

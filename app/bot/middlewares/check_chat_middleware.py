from __future__ import annotations

from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware
from aiogram.enums import ChatType

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from aiogram.types import Chat, TelegramObject, Update

    from services import ChatProfileService

ALLOWED_CHAT_TYPES: frozenset[ChatType] = frozenset(
    (ChatType.GROUP, ChatType.SUPERGROUP),
)


class CheckChatMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        chat: Chat = data["event_chat"]
        chat_profile_service: ChatProfileService = data["chat_profile_service"]

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

                    (
                        data["chat_model"],
                        data["chat_settings"],
                    ) = await chat_profile_service.get_or_create(chat)

            case "callback_query" | "my_chat_member" | "chat_member":
                if chat.type in ALLOWED_CHAT_TYPES:
                    (
                        data["chat_model"],
                        data["chat_settings"],
                    ) = await chat_profile_service.get_or_create(chat)

            case _:
                pass

        return await handler(event, data)

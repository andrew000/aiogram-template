from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, cast

from aiogram import BaseMiddleware
from aiogram.types import Chat, Message, TelegramObject, Update, User

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from services import UserProfileService

# 777000 is Telegram's user id of service messages
TG_SERVICE_USER_ID: Final[int] = 777000


class CheckUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        chat: Chat = data["event_chat"]
        user: User = data["event_from_user"]
        user_profile_service: UserProfileService = data["user_profile_service"]

        if TYPE_CHECKING:
            assert isinstance(event, Update)

        match event.event_type:
            case "message":
                if user.is_bot is False and user.id != TG_SERVICE_USER_ID:
                    (
                        data["user_model"],
                        data["user_settings"],
                    ) = await user_profile_service.get_or_create(user=user, chat=chat)

                msg: Message = cast(Message, event.event)

                if (
                    msg.reply_to_message
                    and msg.reply_to_message.from_user
                    and not msg.reply_to_message.from_user.is_bot
                    and msg.reply_to_message.from_user.id != TG_SERVICE_USER_ID
                ):
                    (
                        data["reply_user_model"],
                        data["reply_user_settings"],
                    ) = await user_profile_service.get_or_create(
                        user=msg.reply_to_message.from_user, chat=chat
                    )

            case "callback_query" | "my_chat_member" | "chat_member" | "inline_query":
                if user.is_bot is False and user.id != TG_SERVICE_USER_ID:
                    (
                        data["user_model"],
                        data["user_settings"],
                    ) = await user_profile_service.get_or_create(user=user, chat=chat)

            case _:
                pass

        return await handler(event, data)

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, cast

from aiogram import BaseMiddleware
from aiogram.enums import ChatType
from aiogram.types import Chat, Message, TelegramObject, Update, User
from domain.user.dto import UserCreateDTO, UserReadDTO, UserSettingsCreateDTO, UserSettingsReadDTO
from domain.user.repo import (
    CachedUserRepository,
    CachedUserSettingsRepository,
    UserRepository,
    UserSettingsRepository,
)
from domain.user.service import (
    CachedUserService,
    CachedUserSettingsService,
    UserService,
    UserSettingsService,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from redis.asyncio.client import Redis
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from utils.aiogram_data import AiogramData

# 777000 is Telegram's user id of service messages
TG_SERVICE_USER_ID: Final[int] = 777000


async def _get_user(
    *,
    db_pool: async_sessionmaker[AsyncSession],
    redis: Redis,
    user: User,
    chat: Chat,
) -> tuple[UserReadDTO, UserSettingsReadDTO]:
    cached_user_service = CachedUserService(repo=CachedUserRepository(redis=redis))
    cached_user_dto: UserReadDTO | None = await cached_user_service.get_user_by_id(user_id=user.id)

    cached_user_settings_service = CachedUserSettingsService(
        repo=CachedUserSettingsRepository(redis=redis)
    )
    cached_user_settings_dto: UserSettingsReadDTO | None = await cached_user_settings_service.get(
        user_id=user.id
    )

    if cached_user_dto and cached_user_settings_dto:
        return cached_user_dto, cached_user_settings_dto

    async with db_pool() as session:
        async with session.begin():
            user_service = UserService(repo=UserRepository(session=session))
            user_dto = await user_service.upsert(
                user_dto=UserCreateDTO(
                    id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    pm_active=chat.type == ChatType.PRIVATE,
                )
            )

            user_settings_service = UserSettingsService(
                repo=UserSettingsRepository(session=session)
            )
            user_settings_dto = await user_settings_service.upsert(
                user_settings_dto=UserSettingsCreateDTO(id=user.id)
            )

        cached_user_dto: UserReadDTO = await cached_user_service.upsert(user_dto=user_dto)
        cached_user_settings_dto: UserSettingsReadDTO = await cached_user_settings_service.upsert(
            user_settings_dto=user_settings_dto
        )

    return cached_user_dto, cached_user_settings_dto


class CheckUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, AiogramData], Awaitable[Any]],
        event: TelegramObject,
        data: AiogramData,
    ) -> Any:  # ty:ignore[invalid-method-override]
        chat: Chat = data["event_chat"]
        user: User = data["event_from_user"]

        if TYPE_CHECKING:
            assert isinstance(event, Update)

        match event.event_type:
            case "message":
                if user.is_bot is False and user.id != TG_SERVICE_USER_ID:
                    data["user_dto"], data["user_settings_dto"] = await _get_user(
                        db_pool=data["db_pool"],
                        redis=data["redis"],
                        user=user,
                        chat=chat,
                    )

                msg: Message = cast(Message, event.event)

                if (
                    msg.reply_to_message
                    and msg.reply_to_message.from_user
                    and not msg.reply_to_message.from_user.is_bot
                    and msg.reply_to_message.from_user.id != TG_SERVICE_USER_ID
                ):
                    data["reply_user_dto"], data["reply_user_settings_dto"] = await _get_user(
                        db_pool=data["db_pool"],
                        redis=data["redis"],
                        user=msg.reply_to_message.from_user,
                        chat=chat,
                    )

            case "callback_query" | "my_chat_member" | "chat_member" | "inline_query":
                if user.is_bot is False and user.id != TG_SERVICE_USER_ID:
                    data["user_dto"], data["user_settings_dto"] = await _get_user(
                        db_pool=data["db_pool"],
                        redis=data["redis"],
                        user=user,
                        chat=chat,
                    )

            case _:
                pass

        return await handler(event, data)

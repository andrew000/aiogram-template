from collections.abc import Awaitable, Callable
from typing import ReadOnly, TypedDict

from aiogram.types import Chat, User
from domain.chat.dto import ChatReadDTO, ChatSettingsReadDTO
from domain.user.dto import UserReadDTO, UserSettingsReadDTO
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class AiogramData(TypedDict, total=False):
    allowed_user_ids: ReadOnly[frozenset[int]]
    event_chat: ReadOnly[Chat]
    event_from_user: ReadOnly[User]
    db_pool: ReadOnly[async_sessionmaker[AsyncSession]]
    db_pool_closer: ReadOnly[Callable[[AsyncSession, AsyncSession], Awaitable[None]]]
    redis: ReadOnly[Redis]

    user_dto: UserReadDTO
    user_settings_dto: UserSettingsReadDTO
    reply_user_dto: UserReadDTO
    reply_user_settings_dto: UserSettingsReadDTO

    chat_dto: ChatReadDTO
    chat_settings_dto: ChatSettingsReadDTO

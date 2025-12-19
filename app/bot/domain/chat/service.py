from __future__ import annotations

from typing import TYPE_CHECKING, Final

import msgspec
from domain.chat.dto import (
    ChatCreateDTO,
    ChatReadDTO,
    ChatSettingsCreateDTO,
    ChatSettingsReadDTO,
    ChatSettingsUpdateDTO,
    ChatUpdateDTO,
)

if TYPE_CHECKING:
    from domain.chat.interface import (
        ICachedChatRepository,
        ICachedChatSettingsRepository,
        IChatRepository,
        IChatSettingsRepository,
    )

ENCODER: Final[msgspec.msgpack.Encoder] = msgspec.msgpack.Encoder()


class ChatService:
    def __init__(self, repo: IChatRepository):
        self.repo = repo

    async def upsert(self, chat_dto: ChatCreateDTO) -> ChatReadDTO:
        existing_chat = await self.repo.get_by_id(chat_dto.id)

        if not existing_chat:
            created_chat = await self.repo.upsert(chat_dto)
            return msgspec.convert(created_chat, ChatReadDTO, from_attributes=True)

        updated_chat = await self.repo.update(chat_dto=ChatUpdateDTO.from_create_dto(chat_dto))
        return msgspec.convert(updated_chat, ChatReadDTO, from_attributes=True)

    async def get_chat_by_id(self, chat_id: int) -> ChatReadDTO | None:
        chat = await self.repo.get_by_id(chat_id)
        if chat:
            return msgspec.convert(chat, ChatReadDTO, from_attributes=True)
        return None

    async def update(self, chat_dto: ChatUpdateDTO) -> ChatReadDTO:
        updated_chat = await self.repo.update(chat_dto)
        return msgspec.convert(updated_chat, ChatReadDTO, from_attributes=True)


class CachedChatService:
    def __init__(self, repo: ICachedChatRepository):
        self.repo = repo

    async def upsert(self, chat_dto: ChatReadDTO) -> ChatReadDTO:
        """chat_dto must be `ChatReadDTO` due to caching purposes."""
        cached_chat = await self.repo.upsert(chat_dto)
        return msgspec.convert(cached_chat, ChatReadDTO, from_attributes=True)

    async def get_chat_by_id(self, chat_id: int) -> ChatReadDTO | None:
        cached_chat = await self.repo.get(chat_id)
        if cached_chat:
            return msgspec.convert(cached_chat, ChatReadDTO, from_attributes=True)
        return None


class ChatSettingsService:
    def __init__(self, repo: IChatSettingsRepository):
        self.repo = repo

    async def upsert(self, chat_settings_dto: ChatSettingsCreateDTO) -> ChatSettingsReadDTO:
        chat_settings = await self.repo.upsert(chat_settings_dto)
        return msgspec.convert(chat_settings, ChatSettingsReadDTO, from_attributes=True)

    async def get(self, chat_id: int) -> ChatSettingsReadDTO | None:
        chat_settings = await self.repo.get(chat_id)
        if chat_settings:
            return msgspec.convert(chat_settings, ChatSettingsReadDTO, from_attributes=True)
        return None

    async def update(self, chat_settings_dto: ChatSettingsUpdateDTO) -> ChatSettingsReadDTO:
        updated_chat_settings = await self.repo.update(chat_settings_dto)
        return msgspec.convert(updated_chat_settings, ChatSettingsReadDTO, from_attributes=True)


class CachedChatSettingsService:
    def __init__(self, repo: ICachedChatSettingsRepository):
        self.repo = repo

    async def upsert(self, chat_settings_dto: ChatSettingsReadDTO) -> ChatSettingsReadDTO:
        """chat_settings_dto must be `ChatSettingsReadDTO` due to caching purposes."""
        cached_chat_settings = await self.repo.upsert(chat_settings_dto)
        return msgspec.convert(cached_chat_settings, ChatSettingsReadDTO, from_attributes=True)

    async def get(self, chat_id: int) -> ChatSettingsReadDTO | None:
        cached_chat_settings = await self.repo.get(chat_id)
        if cached_chat_settings:
            return msgspec.convert(cached_chat_settings, ChatSettingsReadDTO, from_attributes=True)
        return None

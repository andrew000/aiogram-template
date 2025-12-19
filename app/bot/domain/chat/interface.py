from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db.psql import ChatModel, ChatSettingsModel
    from db.redis.chat.models import CachedChatRD, CachedChatSettingsRD
    from domain.chat.dto import (
        ChatCreateDTO,
        ChatReadDTO,
        ChatSettingsCreateDTO,
        ChatSettingsReadDTO,
        ChatSettingsUpdateDTO,
        ChatUpdateDTO,
    )


class IChatRepository(ABC):
    @abstractmethod
    async def upsert(self, chat_dto: ChatCreateDTO) -> ChatModel: ...

    @abstractmethod
    async def get_by_id(self, chat_id: int) -> ChatModel | None: ...

    @abstractmethod
    async def update_member_count(self, chat_id: int, new_member_count: int) -> None: ...

    @abstractmethod
    async def update_invite_link(self, chat_id: int, new_invite_link: str | None) -> None: ...

    @abstractmethod
    async def update(self, chat_dto: ChatUpdateDTO) -> ChatModel: ...


class ICachedChatRepository(ABC):
    @classmethod
    @abstractmethod
    def _key(cls, chat_id: int | str) -> str: ...

    @abstractmethod
    async def upsert(self, chat_dto: ChatReadDTO) -> CachedChatRD:
        """`chat_dto` must be `ChatReadDTO` due to caching purposes."""

    @abstractmethod
    async def get(self, chat_id: int) -> CachedChatRD | None: ...

    @abstractmethod
    async def delete(self, chat_id: int) -> None: ...

    @abstractmethod
    async def delete_all_cached_chats(self) -> None: ...


class IChatSettingsRepository(ABC):
    @abstractmethod
    async def upsert(self, chat_settings_dto: ChatSettingsCreateDTO) -> ChatSettingsModel: ...

    @abstractmethod
    async def get(self, chat_id: int) -> ChatSettingsModel | None: ...

    @abstractmethod
    async def update(self, chat_settings_dto: ChatSettingsUpdateDTO) -> ChatSettingsModel: ...


class ICachedChatSettingsRepository(ABC):
    @classmethod
    @abstractmethod
    def _key(cls, chat_id: int | str) -> str: ...

    @abstractmethod
    async def upsert(self, chat_settings_dto: ChatSettingsReadDTO) -> CachedChatSettingsRD:
        """`chat_settings_dto` must be `ChatSettingsReadDTO` due to caching purposes."""

    @abstractmethod
    async def get(self, chat_id: int) -> CachedChatSettingsRD | None: ...

    @abstractmethod
    async def delete(self, chat_id: int) -> None: ...

    @abstractmethod
    async def delete_all_cached_chat_settings(self) -> None: ...

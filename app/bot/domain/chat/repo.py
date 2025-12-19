from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Final

import msgspec
from db.psql import ChatModel, ChatSettingsModel
from db.redis.chat.models import CachedChatRD, CachedChatSettingsRD
from domain.chat.interface import (
    ICachedChatRepository,
    ICachedChatSettingsRepository,
    IChatRepository,
    IChatSettingsRepository,
)
from sqlalchemy import update

if TYPE_CHECKING:
    from domain.chat.dto import (
        ChatCreateDTO,
        ChatReadDTO,
        ChatSettingsCreateDTO,
        ChatSettingsReadDTO,
        ChatSettingsUpdateDTO,
        ChatUpdateDTO,
    )
    from redis.asyncio import Redis
    from sqlalchemy.ext.asyncio import AsyncSession

ENCODER: Final[msgspec.msgpack.Encoder] = msgspec.msgpack.Encoder()


class ChatRepository(IChatRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert(self, chat_dto: ChatCreateDTO) -> ChatModel:
        new_chat = ChatModel(
            id=chat_dto.id,
            chat_type=chat_dto.chat_type,
            title=chat_dto.title,
            username=chat_dto.username,
            member_count=chat_dto.member_count,
        )
        self.session.add(new_chat)
        await self.session.flush()
        return new_chat

    async def get_by_id(self, chat_id: int) -> ChatModel | None:
        return await self.session.get(entity=ChatModel, ident=chat_id)

    async def update_member_count(self, chat_id: int, new_member_count: int) -> None:
        stmt = (
            update(ChatModel).where(ChatModel.id == chat_id).values(member_count=new_member_count)
        )
        await self.session.execute(stmt)

    async def update_invite_link(self, chat_id: int, new_invite_link: str | None) -> None:
        stmt = update(ChatModel).where(ChatModel.id == chat_id).values(invite_link=new_invite_link)
        await self.session.execute(stmt)

    async def update(self, chat_dto: ChatUpdateDTO) -> ChatModel:
        chat_model: ChatModel | None = await self.get_by_id(chat_dto.id)

        if not chat_model:
            msg = f"Chat with id={chat_dto.id} not found for update."
            raise ValueError(msg)

        for field in chat_dto.__struct_fields__:
            setattr(chat_model, field, getattr(chat_dto, field))

        return chat_model


class CachedChatRepository(ICachedChatRepository):
    def __init__(self, redis: Redis):
        self.redis = redis

    @classmethod
    def _key(cls, chat_id: int | str) -> str:
        return f"{CachedChatRD.__name__}:{chat_id}"

    async def upsert(self, chat_dto: ChatReadDTO) -> CachedChatRD:
        """`chat_dto` must be `ChatReadDTO` due to caching purposes."""
        cached_chat = CachedChatRD(
            id=chat_dto.id,
            chat_type=chat_dto.chat_type,
            title=chat_dto.title,
            username=chat_dto.username,
            member_count=chat_dto.member_count,
            invite_link=chat_dto.invite_link,
            registration_datetime=chat_dto.registration_datetime,
            migrate_from_chat_id=chat_dto.migrate_from_chat_id,
            migrate_datetime=chat_dto.migrate_datetime,
        )

        await self.redis.setex(
            name=self._key(chat_dto.id),
            time=timedelta(days=1),
            value=ENCODER.encode(cached_chat),
        )

        return cached_chat

    async def get(self, chat_id: int) -> CachedChatRD | None:
        data = await self.redis.get(self._key(chat_id))
        if data:
            return msgspec.msgpack.decode(data, type=CachedChatRD)
        return None

    async def delete(self, chat_id: int) -> None:
        await self.redis.delete(self._key(chat_id))

    async def delete_all_cached_chats(self) -> None:
        keys = await self.redis.keys(f"{CachedChatRD.__name__}:*")
        if keys:
            await self.redis.delete(*keys)


class ChatSettingsRepository(IChatSettingsRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert(self, chat_settings_dto: ChatSettingsCreateDTO) -> ChatSettingsModel:
        existing_settings: ChatSettingsModel | None = await self.session.get(
            entity=ChatSettingsModel, ident=chat_settings_dto.id
        )
        if existing_settings:
            return existing_settings

        new_settings = ChatSettingsModel(
            id=chat_settings_dto.id,
            language_code=chat_settings_dto.language_code,
        )
        self.session.add(new_settings)

        await self.session.flush()
        return new_settings

    async def get(self, chat_id: int) -> ChatSettingsModel | None:
        return await self.session.get(entity=ChatSettingsModel, ident=chat_id)

    async def update(self, chat_settings_dto: ChatSettingsUpdateDTO) -> ChatSettingsModel:
        chat_settings_model: ChatSettingsModel | None = await self.get(chat_settings_dto.id)

        if not chat_settings_model:
            msg = f"ChatSettings with id={chat_settings_dto.id} not found for update."
            raise ValueError(msg)

        for field, value in chat_settings_dto.__dict__.items():
            setattr(chat_settings_model, field, value)

        return chat_settings_model


class CachedChatSettingsRepository(ICachedChatSettingsRepository):
    def __init__(self, redis: Redis):
        self.redis = redis

    @classmethod
    def _key(cls, chat_id: int | str) -> str:
        return f"{CachedChatSettingsRD.__name__}:{chat_id}"

    async def upsert(self, chat_settings_dto: ChatSettingsReadDTO) -> CachedChatSettingsRD:
        """`chat_settings_dto` must be `ChatSettingsReadDTO` due to caching purposes."""
        cached_chat_settings = CachedChatSettingsRD(
            id=chat_settings_dto.id,
            language_code=chat_settings_dto.language_code,
        )

        await self.redis.setex(
            name=self._key(chat_settings_dto.id),
            time=timedelta(days=1),
            value=ENCODER.encode(cached_chat_settings),
        )

        return cached_chat_settings

    async def get(self, chat_id: int) -> CachedChatSettingsRD | None:
        data = await self.redis.get(self._key(chat_id))
        if data:
            return msgspec.msgpack.decode(data, type=CachedChatSettingsRD)
        return None

    async def delete(self, chat_id: int) -> None:
        await self.redis.delete(self._key(chat_id))

    async def delete_all_cached_chat_settings(self) -> None:
        keys = await self.redis.keys(f"{CachedChatSettingsRD.__name__}:*")
        if keys:
            await self.redis.delete(*keys)

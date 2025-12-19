from datetime import datetime
from typing import Self

from aiogram.enums import ChatType
from msgspec import UNSET, UnsetType, field

from utils.alchemy_struct import BaseStruct


class ChatCreateDTO(BaseStruct, kw_only=True):
    id: int
    chat_type: ChatType
    title: str | None = field(default=None)
    username: str | None = field(default=None)
    member_count: int
    invite_link: str | None = field(default=None)


class ChatReadDTO(ChatCreateDTO, kw_only=True):
    registration_datetime: datetime
    migrate_from_chat_id: int | None = field(default=None)
    migrate_datetime: datetime | None = field(default=None)


class ChatUpdateDTO(BaseStruct, kw_only=True):
    id: int  # to identify which chat to update
    chat_type: str | UnsetType = field(default=UNSET)
    title: str | UnsetType | None = field(default=UNSET)
    username: str | UnsetType | None = field(default=UNSET)
    member_count: int | UnsetType = field(default=UNSET)
    invite_link: str | UnsetType | None = field(default=UNSET)

    @classmethod
    def from_create_dto(cls, chat_create_dto: ChatCreateDTO) -> Self:
        return cls(
            id=chat_create_dto.id,
            chat_type=chat_create_dto.chat_type,
            title=chat_create_dto.title,
            username=chat_create_dto.username,
            member_count=chat_create_dto.member_count,
            invite_link=chat_create_dto.invite_link,
        )


class ChatSettingsCreateDTO(BaseStruct, kw_only=True):
    id: int
    language_code: str = field(default="en")
    timezone: str | None = field(default=None)


class ChatSettingsReadDTO(ChatSettingsCreateDTO, kw_only=True):
    pass


class ChatSettingsUpdateDTO(BaseStruct, kw_only=True):
    id: int  # to identify which chat settings to update
    language_code: str | UnsetType = field(default=UNSET)
    timezone: str | UnsetType | None = field(default=UNSET)

    @classmethod
    def from_create_dto(cls, chat_settings_create_dto: ChatSettingsCreateDTO) -> Self:
        return cls(
            id=chat_settings_create_dto.id,
            language_code=chat_settings_create_dto.language_code,
            timezone=chat_settings_create_dto.timezone,
        )

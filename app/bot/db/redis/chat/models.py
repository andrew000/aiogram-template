from datetime import datetime

from aiogram.enums import ChatType
from msgspec import Struct, field


class CachedChatRD(Struct, kw_only=True, array_like=True):
    id: int
    chat_type: ChatType
    title: str | None = field(default=None)
    username: str | None = field(default=None)
    member_count: int
    invite_link: str | None = field(default=None)
    registration_datetime: datetime
    migrate_from_chat_id: int | None = field(default=None)
    migrate_datetime: datetime | None = field(default=None)


class CachedChatSettingsRD(Struct, kw_only=True, array_like=True):
    id: int
    language_code: str = field(default="en")
    timezone: str | None = field(default=None)

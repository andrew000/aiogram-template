from datetime import UTC, datetime, timedelta
from secrets import randbelow
from typing import Final, Literal, Self

import msgspec
from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.types import (
    ChatMemberAdministrator,
    ChatMemberBanned,
    ChatMemberLeft,
    ChatMemberMember,
    ChatMemberOwner,
    ChatMemberRestricted,
)
from redis.asyncio.client import Redis
from redis.typing import ExpiryT

TG_MIN_DATETIME: Final[datetime] = datetime(1970, 1, 1, tzinfo=UTC)
ENCODER: Final[msgspec.msgpack.Encoder] = msgspec.msgpack.Encoder()


class RDChatMemberModel(msgspec.Struct, kw_only=True, array_like=True):
    chat_id: int
    user_id: int
    status: ChatMemberStatus
    can_be_edited: bool | None = None
    is_anonymous: bool | None = None
    can_manage_chat: bool | None = None
    can_delete_messages: bool | None = None
    can_manage_video_chats: bool | None = None
    can_restrict_members: bool | None = None
    can_promote_members: bool | None = None
    can_change_info: bool | None = None
    can_invite_users: bool | None = None
    can_post_messages: bool | None = None
    can_edit_messages: bool | None = None
    can_pin_messages: bool | None = None
    can_manage_topics: bool | None = None
    custom_title: str | None = None

    # For restricted status
    can_send_messages: bool | None = None
    can_send_audios: bool | None = None
    can_send_documents: bool | None = None
    can_send_photos: bool | None = None
    can_send_videos: bool | None = None
    can_send_video_notes: bool | None = None
    can_send_voice_notes: bool | None = None
    can_send_polls: bool | None = None
    can_send_other_messages: bool | None = None
    can_add_web_page_previews: bool | None = None
    until_date: datetime | None = None

    @classmethod
    def key(cls, chat_id: int, user_id: int | Literal["*"]) -> str:
        return f"{cls.__name__}:{chat_id}:{user_id}"

    @classmethod
    async def get(cls, redis: Redis, chat_id: int, user_id: int) -> Self | None:
        data = await redis.get(cls.key(chat_id, user_id))
        if data:
            return msgspec.msgpack.decode(data, type=cls)
        return None

    @classmethod
    async def get_all(cls, redis: Redis, chat_id: int) -> list[Self]:
        keys = await redis.keys(cls.key(chat_id, "*"))
        if keys:
            return [msgspec.msgpack.decode(await redis.get(key), type=cls) for key in keys]
        return []

    async def save(self, redis: Redis, ttl: ExpiryT | None = None) -> Self:
        if self.until_date and ttl is None:
            if self.until_date == TG_MIN_DATETIME:
                ttl = timedelta(minutes=45 + randbelow(75 - 45 + 1))

            else:
                ttl = self.until_date - datetime.now(tz=self.until_date.tzinfo)

        elif ttl is None:
            ttl = timedelta(minutes=45 + randbelow(75 - 45 + 1))

        await redis.setex(self.key(self.chat_id, self.user_id), ttl, ENCODER.encode(self))
        return self

    @classmethod
    async def delete(cls, redis: Redis, chat_id: int, user_id: int) -> int:
        return await redis.delete(cls.key(chat_id, user_id))

    @classmethod
    async def delete_for_chat(cls, redis: Redis, chat_id: int) -> int:
        keys = await redis.keys(cls.key(chat_id, "*"))
        if keys:
            return await redis.delete(*keys)
        return 0

    @classmethod
    def resolve(
        cls,
        chat_id: int,
        chat_member: (
            ChatMemberOwner
            | ChatMemberAdministrator
            | ChatMemberMember
            | ChatMemberRestricted
            | ChatMemberLeft
            | ChatMemberBanned
        ),
    ) -> Self:
        match chat_member:
            case ChatMemberOwner():
                return cls.creator(chat_id=chat_id, chat_member=chat_member)

            case ChatMemberAdministrator():
                return cls.administrator(chat_id=chat_id, chat_member=chat_member)

            case ChatMemberMember():
                return cls.member(chat_id=chat_id, chat_member=chat_member)

            case ChatMemberRestricted():
                return cls.restricted(chat_id=chat_id, chat_member=chat_member)

            case ChatMemberLeft():
                return cls.left(chat_id=chat_id, chat_member=chat_member)

            case ChatMemberBanned():
                return cls.kicked(chat_id=chat_id, chat_member=chat_member)

            case _:
                msg = "Unsupported chat member type: %s"
                raise TypeError(msg, type(chat_member))

    @classmethod
    def creator(cls, chat_id: int, chat_member: ChatMemberOwner) -> Self:
        return cls(
            chat_id=chat_id,
            user_id=chat_member.user.id,
            status=chat_member.status,
            is_anonymous=chat_member.is_anonymous,
            custom_title=chat_member.custom_title,
        )

    @classmethod
    def administrator(cls, chat_id: int, chat_member: ChatMemberAdministrator) -> Self:
        return cls(
            chat_id=chat_id,
            user_id=chat_member.user.id,
            status=chat_member.status,
            can_be_edited=chat_member.can_be_edited,
            is_anonymous=chat_member.is_anonymous,
            can_manage_chat=chat_member.can_manage_chat,
            can_delete_messages=chat_member.can_delete_messages,
            can_manage_video_chats=chat_member.can_manage_video_chats,
            can_restrict_members=chat_member.can_restrict_members,
            can_promote_members=chat_member.can_promote_members,
            can_change_info=chat_member.can_change_info,
            can_invite_users=chat_member.can_invite_users,
            can_post_messages=chat_member.can_post_messages,
            can_edit_messages=chat_member.can_edit_messages,
            can_pin_messages=chat_member.can_pin_messages,
            can_manage_topics=chat_member.can_manage_topics,
            custom_title=chat_member.custom_title,
        )

    @classmethod
    def member(cls, chat_id: int, chat_member: ChatMemberMember) -> Self:
        return cls(chat_id=chat_id, user_id=chat_member.user.id, status=chat_member.status)

    @classmethod
    def restricted(cls, chat_id: int, chat_member: ChatMemberRestricted) -> Self:
        return cls(
            chat_id=chat_id,
            user_id=chat_member.user.id,
            status=chat_member.status,
            can_send_messages=chat_member.can_send_messages,
            can_send_audios=chat_member.can_send_audios,
            can_send_documents=chat_member.can_send_documents,
            can_send_photos=chat_member.can_send_photos,
            can_send_videos=chat_member.can_send_videos,
            can_send_video_notes=chat_member.can_send_video_notes,
            can_send_voice_notes=chat_member.can_send_voice_notes,
            can_send_polls=chat_member.can_send_polls,
            can_send_other_messages=chat_member.can_send_other_messages,
            can_add_web_page_previews=chat_member.can_add_web_page_previews,
            can_change_info=chat_member.can_change_info,
            can_invite_users=chat_member.can_invite_users,
            can_pin_messages=chat_member.can_pin_messages,
            can_manage_topics=chat_member.can_manage_topics,
            until_date=chat_member.until_date,
        )

    @classmethod
    def left(cls, chat_id: int, chat_member: ChatMemberLeft) -> Self:
        return cls(chat_id=chat_id, user_id=chat_member.user.id, status=chat_member.status)

    @classmethod
    def kicked(cls, chat_id: int, chat_member: ChatMemberBanned) -> Self:
        return cls(
            chat_id=chat_id,
            user_id=chat_member.user.id,
            status=chat_member.status,
            until_date=chat_member.until_date,
        )


class RDChatBotModel(RDChatMemberModel):
    @classmethod
    async def get_or_create(cls, redis: Redis, chat_id: int, bot: Bot) -> Self:
        bot_chat_member = await cls.get(redis, chat_id, bot.id)

        if not bot_chat_member:
            bot_chat_member = await bot.get_chat_member(chat_id, bot.id)

            bot_chat_member = await cls.resolve(chat_id=chat_id, chat_member=bot_chat_member).save(redis)

        return bot_chat_member

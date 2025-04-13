from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Router
from aiogram.filters import ADMINISTRATOR, CREATOR, PROMOTED_TRANSITION, ChatMemberUpdatedFilter
from storages.redis.chat_member import RDChatMemberModel

if TYPE_CHECKING:
    from aiogram.types import ChatMemberUpdated
    from redis.asyncio.client import Redis

router = Router()


@router.chat_member(ChatMemberUpdatedFilter(PROMOTED_TRANSITION))
@router.chat_member(ChatMemberUpdatedFilter(ADMINISTRATOR >> ADMINISTRATOR))
@router.chat_member(ChatMemberUpdatedFilter(CREATOR >> CREATOR))
async def any_to_administrator(chat_member: ChatMemberUpdated, redis: Redis) -> None:
    chat_user_model = RDChatMemberModel.resolve(chat_member.chat.id, chat_member.new_chat_member)
    await chat_user_model.save(redis)

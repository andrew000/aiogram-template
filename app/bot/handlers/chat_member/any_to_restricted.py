from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiogram import Router
from aiogram.filters import RESTRICTED, ChatMemberUpdatedFilter

from storages.redis.chat_member import RDChatMemberModel

if TYPE_CHECKING:
    from aiogram.types import ChatMemberUpdated
    from redis.asyncio.client import Redis

logger = logging.getLogger(__name__)
router = Router()


@router.chat_member(ChatMemberUpdatedFilter(RESTRICTED))
async def any_to_restricted(chat_member: ChatMemberUpdated, redis: Redis) -> None:
    chat_user_model = RDChatMemberModel.resolve(chat_member.chat.id, chat_member.new_chat_member)
    await chat_user_model.save(redis)

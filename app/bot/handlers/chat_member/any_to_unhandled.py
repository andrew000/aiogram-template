from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING

from aiogram import Bot, Router

if TYPE_CHECKING:
    from aiogram.types import ChatMemberUpdated

logger = logging.getLogger(__name__)
router = Router()


@router.chat_member()
async def any_to_unhandled(chat_member: ChatMemberUpdated, bot: Bot, developer_id: int) -> None:
    alert_id = uuid.uuid4()

    logger.warning(
        "🚨 DETECTED ANY TO UNHANDLED\n%s -> %s.\nAlert id: %s\nUser id: %s\nMention: %s\nChat id: %s\n",
        chat_member.old_chat_member,
        chat_member.new_chat_member,
        alert_id,
        chat_member.new_chat_member.user.id,
        chat_member.new_chat_member.user.mention_html(),
        chat_member.chat.id,
    )

    await bot.send_message(
        developer_id,
        f"🚨 DETECTED ANY TO UNHANDLED:\n"
        f"Alert id: {alert_id}\n"
        f"user_id: {chat_member.new_chat_member.user.id}\n"
        f"mention: {chat_member.new_chat_member.user.mention_html()}\n"
        "Details in /logs",
    )

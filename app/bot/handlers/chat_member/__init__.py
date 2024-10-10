from aiogram import F, Router
from aiogram.enums import ChatType

from . import (
    any_to_administrator,
    any_to_kicked,
    any_to_left,
    any_to_member,
    any_to_restricted,
    any_to_unhandled,
    my_chat_member,
)

router = Router()

router.include_router(my_chat_member.router)  # Must be first
router.include_routers(
    any_to_administrator.router,
    any_to_kicked.router,
    any_to_left.router,
    any_to_member.router,
    any_to_restricted.router,
)
router.include_router(any_to_unhandled.router)  # Must be last

router.chat_member.filter(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))

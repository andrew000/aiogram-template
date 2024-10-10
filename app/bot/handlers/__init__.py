from aiogram import Router

from . import cbs, chat_member, chat_migrate, cmds

router = Router()

router.include_routers(
    cbs.router,
    cmds.router,
    chat_member.router,
    chat_migrate.router,
)

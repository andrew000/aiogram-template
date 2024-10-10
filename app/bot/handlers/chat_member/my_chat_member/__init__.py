from aiogram import Router

from . import groups, private

router = Router()
router.include_routers(private.router, groups.router)

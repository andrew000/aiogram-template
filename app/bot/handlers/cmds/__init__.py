from aiogram import Router

from . import language_settings, start

router = Router()
router.include_routers(
    language_settings.router,
    start.router,
)

from aiogram import Router

from . import language_settings, start, universal_close

router = Router()
router.include_routers(
    language_settings.router,
    start.router,
    universal_close.router,
)

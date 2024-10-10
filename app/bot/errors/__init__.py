from aiogram import Router

from . import aiogram_errors

router = Router()

router.include_routers(aiogram_errors.router)

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiogram import Router

if TYPE_CHECKING:
    from aiogram.types import ErrorEvent

router = Router()
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

file_handler = logging.FileHandler("errors.log", encoding="utf-8")
formatter = logging.Formatter("%(levelname)s:%(name)s - %(asctime)s - on line `%(lineno)d`\n%(message)s\n")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.ERROR)
logger.addHandler(file_handler)


@router.errors()
async def errors_handler(event: ErrorEvent) -> None:
    logger.exception("Update: (%s)\nException: %s\n", event.update, event.exception)

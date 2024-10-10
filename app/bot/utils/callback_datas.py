from typing import Literal

from aiogram.filters.callback_data import CallbackData


class SelectStartCallbackData(CallbackData, prefix="start"):  # type: ignore[call-arg]
    owner_id: int
    action: Literal["profile"]


class CommandsCallbackData(CallbackData, prefix="commands"):  # type: ignore[call-arg]
    owner_id: int
    command: Literal["main_commands", "admin_commands", "vip_commands", "other_commands"]


class SelectProfileCallbackData(CallbackData, prefix="profile"):  # type: ignore[call-arg]
    owner_id: int
    action: Literal["inventory"]

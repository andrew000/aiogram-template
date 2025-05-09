from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, cast

from aiogram import BaseMiddleware
from aiogram.enums import ChatType
from aiogram.types import Chat, Message, TelegramObject, Update, User
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.operators import eq, ne
from storages.psql.user import DBUserModel, DBUserSettingsModel
from storages.redis.user import RDUserModel, RDUserSettingsModel

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from redis.asyncio.client import Redis
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

# 777000 is Telegram's user id of service messages
TG_SERVICE_USER_ID: Final[int] = 777000


async def _get_or_create_user(user: User, chat: Chat, session: AsyncSession) -> DBUserModel:
    if user.username:
        stmt = select(DBUserModel).where(
            eq(DBUserModel.username, user.username),
            ne(DBUserModel.id, user.id),
        )
        another_user: DBUserModel = await session.scalar(stmt)

        if another_user:
            stmt = (
                update(DBUserModel).where(eq(DBUserModel.id, another_user.id)).values(username=None)
            )
            await session.execute(stmt)

    stmt = select(DBUserModel).where(eq(DBUserModel.id, user.id))
    user_model: DBUserModel | None = await session.scalar(stmt)

    if not user_model:
        stmt = (
            insert(DBUserModel)
            .values(
                id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                pm_active=chat.type == ChatType.PRIVATE,
            )
            .returning(DBUserModel)
        )
        user_model = await session.scalar(stmt)

    else:
        user_model.username = user.username
        user_model.first_name = user.first_name
        user_model.last_name = user.last_name

    return cast(DBUserModel, user_model)


async def _get_or_create_user_settings(user: User, session: AsyncSession) -> DBUserSettingsModel:
    stmt = select(DBUserSettingsModel).where(eq(DBUserSettingsModel.id, user.id))
    user_settings_model: DBUserSettingsModel | None = await session.scalar(stmt)

    if not user_settings_model:
        stmt = (
            insert(DBUserSettingsModel)
            .values(id=user.id, language_code=user.language_code or "uk")
            .returning(DBUserSettingsModel)
        )
        user_settings_model = await session.scalar(stmt)

    return cast(DBUserSettingsModel, user_settings_model)


async def _get_user_model(
    db_session: async_sessionmaker[AsyncSession],
    redis: Redis,
    user: User,
    chat: Chat,
) -> tuple[RDUserModel, RDUserSettingsModel]:
    user_model: RDUserModel | None = await RDUserModel.get(redis, user.id)
    user_settings: RDUserSettingsModel | None = await RDUserSettingsModel.get(redis, user.id)

    if user_model and user_settings:
        return user_model, user_settings

    async with db_session() as session:
        async with session.begin():
            user_model: DBUserModel = await _get_or_create_user(user, chat, session)
            user_settings: DBUserSettingsModel = await _get_or_create_user_settings(user, session)

            await session.commit()

        user_model: RDUserModel = RDUserModel.from_orm(cast(DBUserModel, user_model))
        user_settings: RDUserSettingsModel = RDUserSettingsModel.from_orm(
            cast(DBUserSettingsModel, user_settings),
        )

        await cast(RDUserModel, user_model).save(redis)
        await cast(RDUserSettingsModel, user_settings).save(redis)

    return cast(RDUserModel, user_model), cast(RDUserSettingsModel, user_settings)


class CheckUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Update,  # type: ignore[override]
        data: dict[str, Any],
    ) -> Any:
        chat: Chat = data.get("event_chat")
        user: User = data.get("event_from_user")

        match event.event_type:
            case "message":
                if user.is_bot is False and user.id != TG_SERVICE_USER_ID:
                    data["user_model"], data["user_settings"] = await _get_user_model(
                        data["db_session"],
                        data["redis"],
                        user,
                        chat,
                    )

                msg: Message = cast(Message, event.event)

                if (
                    msg.reply_to_message
                    and msg.reply_to_message.from_user
                    and not msg.reply_to_message.from_user.is_bot
                    and msg.reply_to_message.from_user.id != TG_SERVICE_USER_ID
                ):
                    await _get_user_model(
                        data["db_session"],
                        data["redis"],
                        msg.reply_to_message.from_user,
                        chat,
                    )

            case "callback_query" | "my_chat_member" | "chat_member" | "inline_query":
                if user.is_bot is False and user.id != TG_SERVICE_USER_ID:
                    data["user_model"], data["user_settings"] = await _get_user_model(
                        data["db_session"],
                        data["redis"],
                        user,
                        chat,
                    )

            case _:
                pass

        return await handler(event, data)

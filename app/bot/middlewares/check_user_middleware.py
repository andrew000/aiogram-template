from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Final, cast

from aiogram import BaseMiddleware
from aiogram.enums import ChatType
from aiogram.types import Chat, Message, TelegramObject, Update, User
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.operators import eq, ne

from storages.psql.user import UserModel, UserSettingsModel
from storages.redis.user import UserRD, UserSettingsRD

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from redis.asyncio.client import Redis
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

# 777000 is Telegram's user id of service messages
TG_SERVICE_USER_ID: Final[int] = 777000


async def _create_user(*, user: User, chat: Chat, session: AsyncSession) -> UserModel:
    if user.username:
        stmt = select(UserModel).where(
            eq(UserModel.username, user.username), ne(UserModel.id, user.id)
        )
        another_user: UserModel = await session.scalar(stmt)

        if another_user:
            stmt = update(UserModel).where(eq(UserModel.id, another_user.id)).values(username=None)
            await session.execute(stmt)

    stmt = select(UserModel).where(eq(UserModel.id, user.id))
    user_model: UserModel | None = await session.scalar(stmt)

    if not user_model:
        stmt = (
            insert(UserModel)
            .values(
                id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                pm_active=chat.type == ChatType.PRIVATE,
            )
            .on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "last_active": datetime.now(tz=UTC).replace(tzinfo=None),
                },
            )
            .returning(UserModel)
        )
        user_model = await session.scalar(stmt)

    else:
        user_model.username = user.username
        user_model.first_name = user.first_name
        user_model.last_name = user.last_name
        user_model.last_active = datetime.now(tz=UTC).replace(tzinfo=None)

    return cast(UserModel, user_model)


async def _create_user_settings(*, user_id: int, session: AsyncSession) -> UserSettingsModel:
    stmt = (
        insert(UserSettingsModel)
        .values(id=user_id)
        .on_conflict_do_update(
            index_elements=["id"], set_={"language_code": UserSettingsModel.language_code}
        )
        .returning(UserSettingsModel)
    )
    return cast(UserSettingsModel, await session.scalar(stmt))


async def _get_user_model(
    *,
    db_pool: async_sessionmaker[AsyncSession],
    redis: Redis,
    user: User,
    chat: Chat,
) -> tuple[UserRD, UserSettingsRD]:
    user_model: UserRD | None = await UserRD.get(redis, user.id)
    user_settings: UserSettingsRD | None = await UserSettingsRD.get(redis, user.id)

    if user_model and user_settings:
        return user_model, user_settings

    async with db_pool() as session:
        async with session.begin():
            user_model: UserModel = await _create_user(user=user, chat=chat, session=session)
            user_settings: UserSettingsModel = await _create_user_settings(
                user_id=user.id, session=session
            )

            await session.commit()

        user_model: UserRD = UserRD.from_orm(cast(UserModel, user_model))
        user_settings: UserSettingsRD = UserSettingsRD.from_orm(
            cast(UserSettingsModel, user_settings),
        )

        await cast(UserRD, user_model).save(redis)
        await cast(UserSettingsRD, user_settings).save(redis)

    return cast(UserRD, user_model), cast(UserSettingsRD, user_settings)


class CheckUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        chat: Chat = data["event_chat"]
        user: User = data["event_from_user"]

        if TYPE_CHECKING:
            assert isinstance(event, Update)

        match event.event_type:
            case "message":
                if user.is_bot is False and user.id != TG_SERVICE_USER_ID:
                    data["user_model"], data["user_settings"] = await _get_user_model(
                        db_pool=data["db_pool"],
                        redis=data["redis"],
                        user=user,
                        chat=chat,
                    )

                msg: Message = cast(Message, event.event)

                if (
                    msg.reply_to_message
                    and msg.reply_to_message.from_user
                    and not msg.reply_to_message.from_user.is_bot
                    and msg.reply_to_message.from_user.id != TG_SERVICE_USER_ID
                ):
                    data["reply_user_model"], data["reply_user_settings"] = await _get_user_model(
                        db_pool=data["db_pool"],
                        redis=data["redis"],
                        user=msg.reply_to_message.from_user,
                        chat=chat,
                    )

            case "callback_query" | "my_chat_member" | "chat_member" | "inline_query":
                if user.is_bot is False and user.id != TG_SERVICE_USER_ID:
                    data["user_model"], data["user_settings"] = await _get_user_model(
                        db_pool=data["db_pool"],
                        redis=data["redis"],
                        user=user,
                        chat=chat,
                    )

            case _:
                pass

        return await handler(event, data)

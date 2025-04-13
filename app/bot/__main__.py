from __future__ import annotations

import asyncio
import logging
from asyncio import CancelledError
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, cast

import errors
import handlers
import msgspec
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import PRODUCTION, TEST
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, ip_filter_middleware, setup_application
from aiogram.webhook.security import DEFAULT_TELEGRAM_NETWORKS, IPFilter
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores import FluentRuntimeCore
from aiohttp import web
from aiohttp.typedefs import Middleware
from middlewares.check_chat_middleware import CheckChatMiddleware
from middlewares.check_user_middleware import CheckUserMiddleware
from middlewares.throttling_middleware import ThrottlingMiddleware
from settings import Settings
from storages.psql.base import close_db, create_db_session_pool, init_db
from utils.fsm_manager import FSMManager

if TYPE_CHECKING:
    from redis.asyncio import Redis

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def startup(dispatcher: Dispatcher, bot: Bot, settings: Settings, redis: Redis) -> None:
    await bot.delete_webhook(drop_pending_updates=True)

    if settings.dev is False:
        await bot.set_webhook(
            url=settings.webhook_url.get_secret_value(),
            allowed_updates=dispatcher.resolve_used_update_types(),
            secret_token=settings.webhook_secret_token.get_secret_value(),
        )

    engine, db_session = await create_db_session_pool(settings)

    await init_db(engine)

    dispatcher.workflow_data.update(
        {"db_session": db_session, "db_session_closer": partial(close_db, engine)},
    )

    dispatcher.message.middleware(ThrottlingMiddleware(redis))
    dispatcher.callback_query.middleware(ThrottlingMiddleware(redis))

    dispatcher.update.outer_middleware(CheckChatMiddleware())
    dispatcher.update.outer_middleware(CheckUserMiddleware())

    i18n_middleware = I18nMiddleware(
        core=FluentRuntimeCore(path=Path(__file__).parent / "locales" / "{locale}"),
        manager=FSMManager(),
    )
    i18n_middleware.setup(dispatcher=dispatcher)
    await i18n_middleware.core.startup()

    logger.info("Bot started")


async def shutdown(dispatcher: Dispatcher) -> None:
    await dispatcher["db_session_closer"]()
    logger.info("Bot stopped")


async def main() -> None:
    settings = Settings()

    # TelegramLocalBotAPIServer
    # api = TelegramAPIServer.from_base("http://telegram-bot-api:8081")
    # api = TelegramAPIServer.from_base("http://localhost:8081")
    api = TEST if settings.test_server is True else PRODUCTION

    bot = Bot(
        token=settings.bot_token.get_secret_value(),
        session=AiohttpSession(api=api),
        default=DefaultBotProperties(parse_mode="HTML"),
    )

    storage = RedisStorage(
        redis=await settings.redis_dsn(),
        key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        json_loads=msgspec.json.decode,
        json_dumps=partial(lambda obj: str(msgspec.json.encode(obj), encoding="utf-8")),
    )

    dp = Dispatcher(
        storage=storage,
        events_isolation=SimpleEventIsolation(),
        settings=settings,
        redis=storage.redis,
        developer_id=settings.developer_id,
    )
    dp.include_routers(handlers.router, errors.router)
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)

    if settings.webhooks is True:
        app = web.Application(
            middlewares=[cast(Middleware, ip_filter_middleware(IPFilter(DEFAULT_TELEGRAM_NETWORKS)))],
        )

        SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=settings.webhook_secret_token.get_secret_value(),
        ).register(app, "/webhook")
        setup_application(app, dp, bot=bot)

        await web._run_app(app, host="0.0.0.0", port=8080)  # noqa: S104, SLF001

    else:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        uvloop = __import__("uvloop")
        loop_factory = uvloop.new_event_loop

    except ModuleNotFoundError:
        loop_factory = asyncio.new_event_loop
        logger.info("uvloop not found, using default event loop")

    try:
        with asyncio.Runner(loop_factory=loop_factory) as runner:
            runner.run(main())

    except (CancelledError, KeyboardInterrupt):
        __import__("sys").exit(0)

import asyncio
from logging.config import fileConfig

import alembic_postgresql_enum
from alembic import context
from db.psql.base import Base, create_db_pool
from sqlalchemy.engine import Connection

from settings import Settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations(settings: Settings) -> None:
    alembic_postgresql_enum.set_configuration(alembic_postgresql_enum.Config())

    engine, _async_session_maker = await create_db_pool(settings)

    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await engine.dispose()


def run_migrations_online() -> None:
    settings = Settings()
    asyncio.run(run_async_migrations(settings))


def run_migrations_offline() -> None:
    """Nah, just run online migrations in async mode."""
    settings = Settings()
    asyncio.run(run_async_migrations(settings))


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

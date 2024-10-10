import urllib.parse

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from redis.asyncio import Redis
from sqlalchemy import URL


class PostgresSettings(BaseSettings):
    host: str
    port: int
    user: str
    password: SecretStr
    db: str


class RedisSettings(BaseSettings):
    host: str
    port: int
    user: str
    password: SecretStr
    db: int


class Settings(BaseSettings):
    model_config = SettingsConfigDict()
    dev: bool = False
    developer_id: int
    webhooks: bool = False
    bot_token: SecretStr
    webhook_url: SecretStr
    webhook_secret_token: SecretStr

    psql: PostgresSettings = PostgresSettings(_env_prefix="PSQL_")
    redis: RedisSettings = RedisSettings(_env_prefix="REDIS_")

    def psql_dsn(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.psql.user,
            password=self.psql.password.get_secret_value(),
            host=self.psql.host,
            port=self.psql.port,
            database=self.psql.db,
        )

    async def redis_dsn(self) -> Redis:
        return Redis.from_url(
            "redis://{username}:{password}@{host}:{port}/{db}".format(  # noqa: UP032
                username=self.redis.user,
                # password=self.redis.password.get_secret_value(),
                password=urllib.parse.quote(self.redis.password.get_secret_value()),
                host=self.redis.host,
                port=self.redis.port,
                db=self.redis.db,
            ),
        )

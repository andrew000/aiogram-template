from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import expression

from bot.storages.psql.base import Base


class DBChatSettingsModel(Base):
    __tablename__ = "chats_settings"

    id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("chats.id", onupdate="CASCADE", deferrable=True),
        primary_key=True,
        autoincrement=False,
    )
    language_code: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        server_default=expression.text("'en'"),
    )  # language_code is set from User.language_code, which add bot to group
    timezone: Mapped[str] = mapped_column(String, nullable=True)

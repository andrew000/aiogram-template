from datetime import datetime

from aiogram.enums import ChatType
from db.psql import Base
from sqlalchemy import BigInteger, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import CITEXT, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression


class ChatSettingsModel(Base):
    __tablename__ = "chats_settings"

    id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("chats.id", onupdate="CASCADE", deferrable=True),
        primary_key=True,
        autoincrement=False,
    )
    language_code: Mapped[str] = mapped_column(
        String(2),
        server_default=expression.text("'en'"),
    )  # language_code is set from User.language_code, which add bot to group
    timezone: Mapped[str | None] = mapped_column(String)


class ChatModel(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    chat_type: Mapped[ChatType] = mapped_column()
    title: Mapped[str | None] = mapped_column(server_default=expression.null())
    username: Mapped[str | None] = mapped_column(CITEXT, server_default=expression.null())
    member_count: Mapped[int] = mapped_column(BigInteger, server_default=expression.text("0"))
    invite_link: Mapped[str | None] = mapped_column(String, server_default=expression.null())
    registration_datetime: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False, precision=0),
        server_default=expression.text("(now() AT TIME ZONE 'UTC'::text)"),
    )
    migrate_from_chat_id: Mapped[int | None] = mapped_column(
        BigInteger, server_default=expression.null()
    )
    migrate_datetime: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=False, precision=0), server_default=expression.null()
    )

    settings: Mapped[ChatSettingsModel] = relationship()

    __table_args__ = (Index(None, username, unique=True),)

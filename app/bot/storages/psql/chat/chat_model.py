from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import expression

from bot.storages.psql.base import Base


class DBChatModel(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    chat_type: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=True, default=None, server_default=expression.null())
    username: Mapped[str] = mapped_column(CITEXT, nullable=True, default=None, server_default=expression.null())
    registration_datetime: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=expression.text("(now() AT TIME ZONE 'UTC'::text)"),
    )
    migrate_from_chat_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=True,
        default=None,
        server_default=expression.null(),
    )
    migrate_datetime: Mapped[datetime] = mapped_column(nullable=True, default=None, server_default=expression.null())

    __table_args__ = ()

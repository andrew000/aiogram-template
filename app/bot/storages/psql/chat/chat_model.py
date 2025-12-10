from datetime import datetime

from aiogram.enums import ChatType
from sqlalchemy import BigInteger, Index, String
from sqlalchemy.dialects.postgresql import CITEXT, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import expression

from storages.psql.base import Base


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

    __table_args__ = (Index(None, username, unique=True),)

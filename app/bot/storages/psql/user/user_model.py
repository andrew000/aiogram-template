from datetime import datetime

from sqlalchemy import BigInteger, Index
from sqlalchemy.dialects.postgresql import CITEXT, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import expression

from bot.storages.psql.base import Base


class DBUserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[str] = mapped_column(CITEXT, nullable=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=True, server_default=expression.null())
    registration_datetime: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False, precision=0),
        nullable=False,
        server_default=expression.text("(now() AT TIME ZONE 'UTC'::text)"),
    )
    pm_active: Mapped[bool] = mapped_column(nullable=False, server_default=expression.false())

    __table_args__ = (Index(None, "username", unique=True),)

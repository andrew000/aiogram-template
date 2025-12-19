from datetime import datetime
from enum import StrEnum, auto

from db.psql import Base
from sqlalchemy import BigInteger, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import CITEXT, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression


class Gender(StrEnum):
    m = auto()
    f = auto()


class UserSettingsModel(Base):
    __tablename__ = "users_settings"

    id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )
    language_code: Mapped[str] = mapped_column(String(2), server_default=expression.text("'en'"))
    gender: Mapped[Gender] = mapped_column(server_default=expression.text(f"'{Gender.m}'"))
    is_banned: Mapped[bool] = mapped_column(server_default=expression.false())


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[str | None] = mapped_column(CITEXT)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str | None] = mapped_column(server_default=expression.null())
    registration_datetime: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False, precision=0),
        server_default=expression.text("(now() AT TIME ZONE 'UTC'::text)"),
    )
    pm_active: Mapped[bool] = mapped_column(server_default=expression.false())
    last_active: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False, precision=0),
        server_default=expression.text("(now() AT TIME ZONE 'UTC'::text)"),
    )

    settings: Mapped[UserSettingsModel] = relationship()

    __table_args__ = (Index(None, "username", unique=True), Index(None, "last_active"))

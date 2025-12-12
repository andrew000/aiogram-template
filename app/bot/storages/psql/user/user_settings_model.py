from enum import StrEnum, auto

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import expression

from storages.psql.base import Base


class Gender(StrEnum):
    M = auto()
    F = auto()


class UserSettingsModel(Base):
    __tablename__ = "users_settings"

    id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )
    language_code: Mapped[str] = mapped_column(String(2), server_default=expression.text("'en'"))
    gender: Mapped[Gender] = mapped_column(
        server_default=expression.text(f"{Gender.M.value.upper()}")
    )
    is_banned: Mapped[bool] = mapped_column(server_default=expression.false())

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import expression

from storages.psql.base import Base


class DBUserSettingsModel(Base):
    __tablename__ = "users_settings"

    id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )
    language_code: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        server_default=expression.text("'en'"),
    )
    gender: Mapped[str] = mapped_column(
        String(1),
        nullable=False,
        server_default=expression.text("'m'"),
    )
    is_banned: Mapped[bool] = mapped_column(nullable=False, server_default=expression.false())

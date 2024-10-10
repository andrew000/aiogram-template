from __future__ import annotations

from typing import TYPE_CHECKING

import msgspec

if TYPE_CHECKING:
    from sqlalchemy.orm import DeclarativeBase


class AlchemyStruct[T]:
    @classmethod
    def from_orm(cls: type[T], obj: DeclarativeBase) -> T:
        return msgspec.convert(obj, cls, from_attributes=True)

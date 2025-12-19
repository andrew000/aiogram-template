from __future__ import annotations

from typing import TYPE_CHECKING, Any

import msgspec

if TYPE_CHECKING:
    from collections.abc import Hashable

    from sqlalchemy.orm import DeclarativeBase


class BaseStruct(msgspec.Struct):
    def to_dict(self) -> dict[Hashable, Any]:
        return {
            f: getattr(self, f)
            for f in self.__struct_fields__
            if getattr(self, f, None) != msgspec.UNSET
        }


class AlchemyStruct[T]:
    @classmethod
    def from_orm(cls: type[T], obj: DeclarativeBase) -> T:
        return msgspec.convert(obj, cls, from_attributes=True)

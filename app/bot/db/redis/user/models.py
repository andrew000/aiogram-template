from datetime import datetime

from db.psql.user.models import Gender
from msgspec import Struct, field


class CachedUserRD(Struct, kw_only=True, array_like=True):
    id: int
    username: str | None = field(default=None)
    first_name: str
    last_name: str | None = field(default=None)
    registration_datetime: datetime
    pm_active: bool
    last_active: datetime


class CachedUserSettingsRD(Struct, kw_only=True, array_like=True):
    id: int
    language_code: str = field(default="en")
    gender: Gender = field(default=Gender.m)
    is_banned: bool = field(default=False)

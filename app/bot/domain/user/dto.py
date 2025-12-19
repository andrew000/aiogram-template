from datetime import datetime
from typing import Self

from db.psql.user.models import Gender
from msgspec import UNSET, UnsetType, field

from utils.alchemy_struct import BaseStruct


class UserCreateDTO(BaseStruct, kw_only=True):
    id: int
    username: str | None = field(default=None)
    first_name: str
    last_name: str | None = field(default=None)
    pm_active: bool


class UserReadDTO(UserCreateDTO, kw_only=True):
    registration_datetime: datetime
    last_active: datetime


class UserUpdateDTO(BaseStruct, kw_only=True):
    id: int  # to identify which user to update
    username: str | UnsetType | None = field(default=UNSET)
    first_name: str | UnsetType = field(default=UNSET)
    last_name: str | UnsetType | None = field(default=UNSET)
    pm_active: bool | UnsetType = field(default=UNSET)

    @classmethod
    def from_create_dto(cls, user_create_dto: UserCreateDTO) -> Self:
        return cls(
            id=user_create_dto.id,
            username=user_create_dto.username,
            first_name=user_create_dto.first_name,
            last_name=user_create_dto.last_name,
            pm_active=user_create_dto.pm_active,
        )


class UserSettingsCreateDTO(BaseStruct, kw_only=True):
    id: int
    language_code: str = field(default="en")
    gender: Gender = field(default=Gender.m)
    is_banned: bool = field(default=False)


class UserSettingsReadDTO(UserSettingsCreateDTO, kw_only=True):
    pass


class UserSettingsUpdateDTO(BaseStruct, kw_only=True):
    id: int  # to identify which user settings to update
    language_code: str | UnsetType = field(default=UNSET)
    gender: Gender | UnsetType = field(default=UNSET)
    is_banned: bool | UnsetType = field(default=UNSET)

    @classmethod
    def from_create_dto(cls, user_settings_create_dto: UserSettingsCreateDTO) -> Self:
        return cls(
            id=user_settings_create_dto.id,
            language_code=user_settings_create_dto.language_code,
            gender=user_settings_create_dto.gender,
            is_banned=user_settings_create_dto.is_banned,
        )

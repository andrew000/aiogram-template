# mypy: ignore-errors
# This is auto-generated file, do not edit!
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, Literal

from aiogram_i18n import LazyProxy

class I18nContext(I18nStub):
    def get(self, key: str, /, **kwargs: Any) -> str: ...
    async def set_locale(self, locale: str, **kwargs: Any) -> None: ...
    @contextmanager
    def use_locale(self, locale: str) -> Generator[I18nContext]: ...
    @contextmanager
    def use_context(self, **kwargs: Any) -> Generator[I18nContext]: ...
    def set_context(self, **kwargs: Any) -> None: ...

class LazyFactory(I18nStub):
    key_separator: str

    def set_separator(self, key_separator: str) -> None: ...
    def __call__(self, key: str, /, **kwargs: dict[str, Any]) -> LazyProxy: ...

L: LazyFactory

class I18nStub:
    class __ChangeLanguage:
        @staticmethod
        def button(**kwargs: Any) -> Literal["🌐 Change language"]: ...

    change_language = __ChangeLanguage
    class __ChatMember:
        @staticmethod
        def join_transition(*, mention: Any, **kwargs: Any) -> Literal["Welcome, { $mention }"]: ...
        @staticmethod
        def leave_transition(*, mention: Any, **kwargs: Any) -> Literal["Bye, { $mention }"]: ...

    chat_member = __ChatMember
    class __Close:
        @staticmethod
        def windows(**kwargs: Any) -> Literal["❌ Close"]: ...

    close = __Close
    class __Message:
        @staticmethod
        def deprecated(**kwargs: Any) -> Literal["🗑 Message deprecated."]: ...

    message = __Message
    class __MyChatMember:
        @staticmethod
        def demoted_transition(
            **kwargs: Any,
        ) -> Literal["My administrator rights have been revoked."]: ...
        @staticmethod
        def join_transition(
            *,
            can_delete_messages: Any,
            can_restrict_members: Any,
            can_invite_users: Any,
            **kwargs: Any,
        ) -> Literal["❤️ Thank you for adding me to the chat."]: ...
        @staticmethod
        def promoted_transition(
            *,
            can_delete_messages: Any,
            can_restrict_members: Any,
            can_invite_users: Any,
            **kwargs: Any,
        ) -> Literal["❤️ Thank you for promoting me to an administrator!"]: ...

    my_chat_member = __MyChatMember
    class __Settings:
        @staticmethod
        def lang(**kwargs: Any) -> Literal["lang"]: ...
        @staticmethod
        def language(**kwargs: Any) -> Literal["language"]: ...

        class __SelectLanguage:
            @staticmethod
            def changed(
                *, language_code: Any, **kwargs: Any
            ) -> Literal["✅ Language changed to: {...}"]: ...
            @staticmethod
            def code(*, language_code: Any, **kwargs: Any) -> Literal["{...}"]: ...
            @staticmethod
            def goto_start(**kwargs: Any) -> Literal["↪️ Go to start"]: ...
            @staticmethod
            def text(**kwargs: Any) -> Literal["💁‍♂️ Choose a language:"]: ...

        select_language = __SelectLanguage

    settings = __Settings
    class __Start:
        @staticmethod
        def start_text(
            *, user_mention: Any, **kwargs: Any
        ) -> Literal["👋 Hi, { $user_mention }"]: ...

    start = __Start
    class __Window:
        @staticmethod
        def closed(**kwargs: Any) -> Literal["✅ Closed"]: ...

    window = __Window

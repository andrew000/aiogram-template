from enum import StrEnum


class CallbackDataPrefix(StrEnum):
    language_window = "language_window"  # LanguageWindowCB: language_window
    select_language = "select_language"  # SelectLanguageCB: select_language
    goto_start = "goto_start"  # GOTOStartCB: start
    universal_close = "universal_close"  # UniversalCloseCB: universal_close

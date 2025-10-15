from dataclasses import dataclass
from typing import Literal


@dataclass
class __CallbackDataPrefix:
    language_window: Literal["language_window"] = "lang_w"
    select_language: Literal["select_language"] = "sel_lng"
    goto_start: Literal["goto_start"] = "go_st"
    universal_close: Literal["universal_close"] = "u_cls"


CallbackDataPrefix = __CallbackDataPrefix()

__all__ = ("CallbackDataPrefix",)

from dataclasses import dataclass
from hashlib import blake2s


def _hide(data: str) -> str:
    """Hashes the callback data using blake2s to create a short unique prefix."""
    return blake2s(data.encode(), digest_size=4).hexdigest()


@dataclass
class __CallbackDataPrefix:
    language_window: str = "LanguageWindowCB"
    select_language: str = "SelectLanguageCB"
    goto_start: str = "GOTOStartCB"
    universal_close: str = "UniversalWindowCloseCB"

    def __post_init__(self) -> None:
        # Hash all attributes to ensure uniqueness
        for attr in dir(self):
            if not attr.startswith("_"):
                setattr(self, attr, _hide(getattr(self, attr)))

        # Check for collisions after hashing
        seen = set()
        for attr in dir(self):
            if not attr.startswith("_"):
                value = getattr(self, attr)
                if value in seen:
                    msg = f"Collision detected for callback data: {attr} - {value}"
                    raise ValueError(msg)
                seen.add(value)


CallbackDataPrefix = __CallbackDataPrefix()

__all__ = ("CallbackDataPrefix",)

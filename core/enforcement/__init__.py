from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = ["calculate_genius", "floors_to_dials", "APEXDials"]


def __getattr__(name: str) -> Any:
    if name in __all__:
        module = import_module(".genius", __name__)
        value = getattr(module, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))

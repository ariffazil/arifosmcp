"""
arifosmcp.intelligence/tools/aclip_base.py — ACLIP Shared Foundation

Provides:
  - Standard return-shape factories: ok(), partial(), void()
  - Single psutil availability guard: psutil_available() / PSUTIL_OK
  - AclipResult TypedDict for type annotations

All tools MUST import from here instead of reimplementing boilerplate.
F4 Clarity: One source of truth for dependency management and return shapes.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Psutil Guard — One check, imported everywhere
# ---------------------------------------------------------------------------
try:
    import psutil as _psutil

    if not hasattr(_psutil, "net_connections") or not hasattr(_psutil, "AccessDenied"):
        raise ImportError("Broken psutil: missing required attributes")

    PSUTIL_OK: bool = True
    psutil = _psutil  # Re-export for tools that need the module directly

except (ImportError, AttributeError):
    _psutil = None
    PSUTIL_OK: bool = False
    psutil = None  # type: ignore[assignment]


def psutil_available() -> bool:
    """Returns True if psutil is installed and fully functional."""
    return PSUTIL_OK


# ---------------------------------------------------------------------------
# Return Shape Factories — F4 Clarity (consistent contract)
# ---------------------------------------------------------------------------


def ok(data: dict[str, Any] | None = None, **meta: Any) -> dict[str, Any]:
    """Successful result. status=SEAL."""
    result: dict[str, Any] = {"status": "SEAL"}
    if data:
        result.update(data)
    if meta:
        result.update(meta)
    return result


def partial(
    data: dict[str, Any] | None = None,
    warning: str = "",
    **meta: Any,
) -> dict[str, Any]:
    """Partial result — degraded but functional. status=PARTIAL."""
    result: dict[str, Any] = {"status": "PARTIAL"}
    if warning:
        result["warning"] = warning
    if data:
        result.update(data)
    if meta:
        result.update(meta)
    return result


def void(error: str, hint: str = "", **meta: Any) -> dict[str, Any]:
    """Failed result — tool could not complete. status=VOID."""
    result: dict[str, Any] = {"status": "VOID", "error": error}
    if hint:
        result["hint"] = hint
    if meta:
        result.update(meta)
    return result

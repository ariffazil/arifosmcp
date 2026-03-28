"""
core/enforcement/floor_audit.py — Forwarding Stub

DEPRECATED: Use core.shared.floor_audit for all new code.
This module is kept for legacy compatibility and will be removed in v2026.04.
"""

from __future__ import annotations

import warnings

from arifosmcp.core.shared.floor_audit import (
    AuditResult,
    FloorAuditor,
    FloorResult,
    Verdict,
)

# Issue deprecation warning on import
warnings.warn(
    "core.enforcement.floor_audit is deprecated. Use core.shared.floor_audit instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["Verdict", "FloorResult", "AuditResult", "FloorAuditor"]

"""
core/shared/routing.py — Compatibility routing adapter.

DEPRECATED: Use core.enforcement.routing for all new code.
This module is kept for legacy compatibility and will be removed in v2026.04.
"""

from __future__ import annotations

import warnings

from arifosmcp.core.enforcement.routing import FACTUAL_INDICATORS as CANONICAL_FACTUAL_INDICATORS
from arifosmcp.core.enforcement.routing import compatibility_category_for_domain, detect_refusal_rule
from arifosmcp.core.enforcement.routing import should_reality_check as canonical_should_reality_check

# Issue deprecation warning on import
warnings.warn(
    "core.shared.routing is deprecated. Use core.enforcement.routing instead.",
    DeprecationWarning,
    stacklevel=2,
)

FACTUAL_INDICATORS = CANONICAL_FACTUAL_INDICATORS


def route_refuse(query: str) -> dict[str, object]:
    """
    Preserve the legacy dict contract on top of the canonical enforcement router.

    Returns:
        Dict with `should_refuse`, `reason`, `category`, and `confidence`.
    """
    rule = detect_refusal_rule(query)
    if rule is None:
        return {
            "should_refuse": False,
            "reason": None,
            "category": None,
            "confidence": 0.0,
        }

    return {
        "should_refuse": True,
        "reason": f"Detected {rule.name} content",
        "category": compatibility_category_for_domain(rule.risk_domain),
        "confidence": 0.8,
    }


def should_reality_check(query: str) -> tuple[bool, str | None]:
    """Determine if query needs reality (web) checking."""
    return canonical_should_reality_check(query)

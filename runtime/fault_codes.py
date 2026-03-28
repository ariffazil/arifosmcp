"""
arifosmcp/runtime/fault_codes.py — VOID Memanjang Elimination: Fault Code Taxonomy

THE VOID MEMANJANG FAILURE MODE (what this module eliminates):
  Legacy behaviour: any network error, timeout, or missing dependency would
  cause the system to emit a VOID verdict. This is catastrophically wrong.
  VOID means constitutional collapse (F2/F11/F12/F13 violation). It is terminal.
  A missing Qdrant collection is not a constitutional collapse. It is plumbing.

THE HARD INVARIANT (from Grand Unified Technical Specification, FORGED-2026.03):
  - Mechanical faults (infrastructure) → 888_HOLD with machine.fault_code set
  - Constitutional failures (floor breach) → VOID with governance.void_reason set
  - Epistemic failures (insufficient evidence) → SABAR

FAULT CODE TAXONOMY:
  INFRA_* codes:     Service unavailable, degraded, or timing out
  TOOL_*  codes:     Endpoint not found, not exposed, schema invalid
  RATE_*  codes:     Rate limits, quota exhaustion
  VOID_*  codes:     Constitutional violations ONLY (hard floors)

classifier(exception) → FaultClassification tells the kernel which verdict to issue.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# FAULT CLASS ENUM
# ─────────────────────────────────────────────────────────────────────────────
class FaultClass(str, Enum):
    MECHANICAL = "MECHANICAL"          # Infrastructure fault → 888_HOLD
    EPISTEMIC = "EPISTEMIC"            # Insufficient evidence → SABAR
    CONSTITUTIONAL = "CONSTITUTIONAL"  # Hard floor breach → VOID (terminal)


# ─────────────────────────────────────────────────────────────────────────────
# FAULT CODES
# ─────────────────────────────────────────────────────────────────────────────
class MechanicalFaultCode(str, Enum):
    """Infrastructure faults. ALWAYS → 888_HOLD, NEVER → VOID."""
    TOOL_NOT_EXPOSED       = "TOOL_NOT_EXPOSED"        # 404 / endpoint not registered
    INFRA_DEGRADED         = "INFRA_DEGRADED"          # service unreachable / 5xx
    TIMEOUT_EXCEEDED       = "TIMEOUT_EXCEEDED"        # network/compute timeout
    RATE_LIMITED           = "RATE_LIMITED"            # 429 / quota exceeded
    DEPENDENCY_UNAVAILABLE = "DEPENDENCY_UNAVAILABLE"  # Qdrant/Redis/Postgres offline
    DNS_FAIL               = "DNS_FAIL"                # DNS resolution failure
    TLS_FAIL               = "TLS_FAIL"                # SSL/TLS handshake failure
    WAF_BLOCK              = "WAF_BLOCK"               # WAF/CDN blocked request
    PARSE_FAIL             = "PARSE_FAIL"              # Response parse error
    RENDER_FAIL            = "RENDER_FAIL"             # Headless browser render failure
    NO_RESULTS             = "NO_RESULTS"              # Search returned empty (→ SABAR not VOID)


class ConstitutionalFaultCode(str, Enum):
    """Constitutional violations. ALWAYS → VOID (terminal). Cannot be retried."""
    F1_AMANAH_BREACH           = "F1_AMANAH_BREACH"           # Integrity violation
    F2_TRUTH_BELOW_THRESHOLD   = "F2_TRUTH_BELOW_THRESHOLD"   # Evidence score < 0.99
    F3_CONSENSUS_SHATTERED     = "F3_CONSENSUS_SHATTERED"     # Tri-witness failure
    F4_CLARITY_VIOLATION       = "F4_CLARITY_VIOLATION"       # Entropy dS > 0
    F5_PEACE_VIOLATION         = "F5_PEACE_VIOLATION"         # Peace² < 1.0
    F6_EMPATHY_VIOLATION       = "F6_EMPATHY_VIOLATION"       # κᵣ < 0.7
    F7_HUMILITY_VIOLATION      = "F7_HUMILITY_VIOLATION"      # Omega outside [0.03, 0.05]
    F8_GENIUS                  = "F8_GENIUS"                  # Genius G* < 0.80
    F9_SHADOW_VIOLATION        = "F9_SHADOW_VIOLATION"        # Shadow load > 0.3
    F10_ONTOLOGY               = "F10_ONTOLOGY"                # Personhood/consciousness claim
    F11_AUTH_FAILURE          = "F11_AUTH_FAILURE"            # Actor not in whitelist
    F11_TOKEN_INVALID         = "F11_TOKEN_INVALID"           # Signature mismatch
    F11_TOKEN_EXPIRED         = "F11_TOKEN_EXPIRED"           # Bucket stale → re-anchor
    F11_SESSION_MISMATCH      = "F11_SESSION_MISMATCH"        # session_id mismatch
    F11_SOVEREIGN_SIG_INVALID = "F11_SOVEREIGN_SIG_INVALID"   # Ratification sig invalid
    F12_INJECTION             = "F12_INJECTION"               # Prompt injection detected
    F13_SOVEREIGN_VETO        = "F13_SOVEREIGN_VETO"          # Human rejected via ratify


# ─────────────────────────────────────────────────────────────────────────────
# CLASSIFICATION RESULT
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class FaultClassification:
    fault_class: FaultClass
    fault_code: str
    verdict: str          # VOID | 888_HOLD | SABAR
    recoverable: bool
    retry_hint: str = ""

    @property
    def is_void(self) -> bool:
        return self.verdict == "VOID"

    @property
    def is_hold(self) -> bool:
        return self.verdict == "888_HOLD"

    @property
    def is_sabar(self) -> bool:
        return self.verdict == "SABAR"


# ─────────────────────────────────────────────────────────────────────────────
# CLASSIFIER
# ─────────────────────────────────────────────────────────────────────────────
def classify_exception(exc: Exception) -> FaultClassification:
    """
    Classify a Python exception into a FaultClassification.

    This is the VOID Memanjang elimination function.
    Every call site that previously did 'except Exception: return VOID'
    must be replaced with this classifier.

    Returns FaultClassification with correct verdict (888_HOLD or SABAR, never VOID).
    """
    try:
        import httpx
        if isinstance(exc, httpx.ConnectError):
            return FaultClassification(
                FaultClass.MECHANICAL, MechanicalFaultCode.DNS_FAIL,
                "888_HOLD", True, "Check network connectivity and DNS resolution",
            )
        if isinstance(exc, httpx.TimeoutException):
            return FaultClassification(
                FaultClass.MECHANICAL, MechanicalFaultCode.TIMEOUT_EXCEEDED,
                "888_HOLD", True, "Increase timeout or retry with backoff",
            )
        if isinstance(exc, httpx.HTTPStatusError):
            code = exc.response.status_code
            if code == 404:
                return FaultClassification(
                    FaultClass.MECHANICAL, MechanicalFaultCode.TOOL_NOT_EXPOSED,
                    "888_HOLD", True, "Verify endpoint is registered and deployed",
                )
            if code == 429:
                return FaultClassification(
                    FaultClass.MECHANICAL, MechanicalFaultCode.RATE_LIMITED,
                    "888_HOLD", True, "Apply exponential backoff and retry",
                )
            if 500 <= code < 600:
                return FaultClassification(
                    FaultClass.MECHANICAL, MechanicalFaultCode.INFRA_DEGRADED,
                    "888_HOLD", True, "Service returned 5xx — wait and retry",
                )
    except ImportError:
        pass

    err_str = str(exc).lower()
    if "ssl" in err_str or "certificate" in err_str or "tls" in err_str:
        return FaultClassification(
            FaultClass.MECHANICAL, MechanicalFaultCode.TLS_FAIL,
            "888_HOLD", True, "Check TLS certificates and CA bundle",
        )
    if "qdrant" in err_str or "connect" in err_str or "refused" in err_str:
        return FaultClassification(
            FaultClass.MECHANICAL, MechanicalFaultCode.DEPENDENCY_UNAVAILABLE,
            "888_HOLD", True, "Check dependent service health (Qdrant/Redis/Postgres)",
        )
    if "timeout" in err_str:
        return FaultClassification(
            FaultClass.MECHANICAL, MechanicalFaultCode.TIMEOUT_EXCEEDED,
            "888_HOLD", True, "Retry with longer timeout",
        )

    # Default: unknown mechanical fault — still 888_HOLD, not VOID
    logger.warning(
        "classify_exception: unknown exception type %s → INFRA_DEGRADED",
        type(exc).__name__,
    )
    return FaultClassification(
        FaultClass.MECHANICAL, MechanicalFaultCode.INFRA_DEGRADED,
        "888_HOLD", True, f"Unexpected error: {type(exc).__name__}",
    )


def classify_network_errors(errors: list[dict]) -> str:
    """
    Classify a list of error dicts from multi-engine search into a single fault code.

    Returns:
        "INFRA_DEGRADED" if all engines failed with infrastructure errors.
        "NO_RESULTS" if engines succeeded but returned no content.
    """
    if not errors:
        return "NO_RESULTS"
    infra_codes = {
        MechanicalFaultCode.DNS_FAIL,
        MechanicalFaultCode.TIMEOUT_EXCEEDED,
        MechanicalFaultCode.INFRA_DEGRADED,
        MechanicalFaultCode.TLS_FAIL,
    }
    infra_count = sum(
        1 for e in errors
        if e.get("code") in {c.value for c in infra_codes}
    )
    return "INFRA_DEGRADED" if infra_count > len(errors) // 2 else "NO_RESULTS"


__all__ = [
    "FaultClass",
    "FaultClassification",
    "MechanicalFaultCode",
    "ConstitutionalFaultCode",
    "classify_exception",
    "classify_network_errors",
]

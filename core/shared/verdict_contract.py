"""
core/shared/verdict_contract.py — Canonical Verdict Contract (v46)

Every stage speaks the same legal language, with stage-specific meaning.

Global Verdict Set (6 verdicts only):
    SEAL        — stage successful           (non-terminal)
    PROVISIONAL — exploratory result         (non-terminal)
    PARTIAL     — incomplete but usable      (non-terminal)
    SABAR       — pause / needs more context (non-terminal)
    HOLD        — waiting for authority/human(non-terminal)
    VOID        — hard rejection             (TERMINAL — must be extremely rare)

Critical Kernel Rule:
    if stage != 0 and stage < 888 and verdict == VOID:
        verdict = SABAR

This single rule prevents premature pipeline death.

Only stage 000 (auth/injection) and 888 JUDGE (constitutional gate) may emit VOID.

Stage Contracts:
    000 INIT     → SEAL, SABAR, VOID          (auth failures only VOID allowed early)
    111 SENSE    → SEAL, PARTIAL, SABAR       (input parsing never kills pipeline)
    222 REALITY  → SEAL, PARTIAL, SABAR       (if search fails → PARTIAL not VOID)
    333 MIND     → PROVISIONAL, PARTIAL, SABAR(lab must be allowed to think wrong)
    555 HEART    → SEAL, HOLD, SABAR          (heart pauses ideas, does not reject them)
    666 CRITIQUE → SEAL, PARTIAL, HOLD        (critique weakens ideas, does not kill them)
    777 FORGE    → SEAL, HOLD, SABAR          (runtime errors → SABAR not VOID)
    888 JUDGE    → SEAL, HOLD, VOID           (first real rejection stage)
    999 VAULT    → SEAL, VOID                 (commit or refuse)

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from arifosmcp.core.shared.types import Verdict

logger = logging.getLogger(__name__)


def _lazy_verdict():
    """Lazy import to avoid circular dependency."""
    from arifosmcp.core.shared.types import Verdict

    return Verdict


# ---------------------------------------------------------------------------
# Stage contracts: stage_number → frozenset of allowed Verdict values
# ---------------------------------------------------------------------------


def _build_contracts() -> dict[int, frozenset]:
    """Build stage contracts lazily to avoid import-time circular deps."""
    from arifosmcp.core.shared.types import Verdict

    return {
        0: frozenset({Verdict.SEAL, Verdict.SABAR, Verdict.VOID}),
        111: frozenset({Verdict.SEAL, Verdict.PARTIAL, Verdict.SABAR}),
        222: frozenset({Verdict.SEAL, Verdict.PARTIAL, Verdict.SABAR}),
        333: frozenset({Verdict.PROVISIONAL, Verdict.PARTIAL, Verdict.SABAR}),
        555: frozenset({Verdict.SEAL, Verdict.HOLD, Verdict.SABAR}),
        666: frozenset({Verdict.SEAL, Verdict.PARTIAL, Verdict.HOLD}),
        777: frozenset({Verdict.SEAL, Verdict.HOLD, Verdict.SABAR}),
        888: frozenset({Verdict.SEAL, Verdict.HOLD_888, Verdict.VOID}),
        999: frozenset({Verdict.SEAL, Verdict.VOID}),
    }


_CONTRACTS: dict[int, frozenset] | None = None


def _get_contracts() -> dict[int, frozenset]:
    global _CONTRACTS
    if _CONTRACTS is None:
        _CONTRACTS = _build_contracts()
    return _CONTRACTS


# ---------------------------------------------------------------------------
# Legacy string → canonical Verdict mapping
# ---------------------------------------------------------------------------

_LEGACY_STRING_MAP: dict[str, str] = {
    "888_HOLD": "HOLD_888",
    "HOLD-888": "HOLD_888",
    "HOLD_888": "HOLD_888",
    "888_hold": "HOLD_888",
    "seal": "SEAL",
    "void": "VOID",
    "partial": "PARTIAL",
    "sabar": "SABAR",
    "hold": "HOLD",
    "provisional": "PROVISIONAL",
}


def _coerce_verdict(raw: str):
    """
    Safely coerce any string to a canonical Verdict.
    Falls back to SABAR for unknown values (never fails the pipeline).
    """
    from arifosmcp.core.shared.types import Verdict

    normalized = _LEGACY_STRING_MAP.get(raw, raw.upper() if raw else "SABAR")
    try:
        return Verdict(normalized)
    except ValueError:
        logger.warning("verdict_contract: unknown verdict string %r — coerced to SABAR", raw)
        return Verdict.SABAR


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def normalize_verdict(stage: int, verdict: Any) -> Verdict:
    """
    Canonical kernel normalization rule.

    Applies the critical contract:
        if stage != 0 and stage < 888 and verdict == VOID → SABAR

    Also normalizes legacy strings ("888_HOLD", "HOLD-888") to canonical Verdict.

    Args:
        stage:   Stage number (0, 111, 222, 333, 555, 666, 777, 888, 999).
                 Use 0 for the 000 INIT stage.
        verdict: A Verdict instance or legacy string.

    Returns:
        Canonical Verdict instance.
    """
    from arifosmcp.core.shared.types import Verdict

    # Coerce string → Verdict
    if isinstance(verdict, str):
        verdict = _coerce_verdict(verdict)

    if stage < 888 and verdict == Verdict.HOLD_888:
        return Verdict.HOLD

    if stage == 888 and verdict == Verdict.HOLD:
        return Verdict.HOLD_888

    # Core normalization rule: only stage 0 (000 INIT) and 888+ may emit VOID
    if stage != 0 and stage < 888 and verdict == Verdict.VOID:
        logger.warning(
            "verdict_contract: stage %03d emitted VOID — normalized to SABAR "
            "(VOID reserved for 000 INIT auth failures and 888 JUDGE)",
            stage,
        )
        return Verdict.SABAR

    return verdict


def validate_stage_verdict(stage: int, verdict) -> tuple[bool, str]:
    """
    Validate that a verdict is allowed for a given stage.

    Returns:
        (is_valid, warning_message)

    Does NOT raise — only warns. The pipeline should log warnings but continue.
    Normalization via normalize_verdict() should be called before this.
    """

    if isinstance(verdict, str):
        verdict = _coerce_verdict(verdict)

    contracts = _get_contracts()
    allowed = contracts.get(stage)
    if allowed is None:
        return True, ""  # Unknown stages pass through without validation

    if verdict not in allowed:
        allowed_str = ", ".join(sorted(v.value for v in allowed))
        msg = (
            f"Stage {stage:03d} emitted verdict '{verdict.value}' which is not in "
            f"contract [{allowed_str}]. Apply normalize_verdict() first."
        )
        return False, msg

    return True, ""


def get_stage_contract(stage: int) -> frozenset:
    """Return the set of allowed verdicts for a given stage number."""
    return _get_contracts().get(stage, frozenset())


__all__ = [
    "normalize_verdict",
    "validate_stage_verdict",
    "get_stage_contract",
]

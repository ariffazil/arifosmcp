"""
organs/0_init.py — Stage 000: CONSTITUTIONAL AIRLOCK (APEX-G) - GROUNDED

UPGRADE: Actor Registry aligned with v2026.03.24-GOLD Spec.
"""

from __future__ import annotations

import secrets
import time
import re
from datetime import datetime, timezone
from typing import Any, Dict

from arifosmcp.core.shared.atlas import Phi
from arifosmcp.core.shared.types import (
    AuthorityLevel,
    CodeState,
    GovernanceMetadata,
    InitOutput,
    Intent,
    MathDials,
    PhysicsState,
    Verdict,
)

# -----------------------------------------------------------------------------
# SECTION 6.1: CANONICAL ACTOR REGISTRY
# -----------------------------------------------------------------------------

VALID_ACTORS: set[str] = {
    "arif", "ariffazil", "openclaw", "agentzero", 
    "operator", "cli", "user", "test_user", "anonymous"
}

ACTOR_AUTHORITY: dict[str, AuthorityLevel] = {
    "arif": AuthorityLevel.SOVEREIGN,
    "ariffazil": AuthorityLevel.SOVEREIGN,
    "openclaw": AuthorityLevel.AGENT,
    "agentzero": AuthorityLevel.AGENT,
    "operator": AuthorityLevel.OPERATOR,
    "cli": AuthorityLevel.OPERATOR,
    "user": AuthorityLevel.USER,
    "test_user": AuthorityLevel.USER,
    "anonymous": AuthorityLevel.ANONYMOUS
}

# -----------------------------------------------------------------------------
# F12: HARDENED INJECTION GUARD
# -----------------------------------------------------------------------------

class InjectionGuard:
    PATTERNS: list[tuple[str, float]] = [
        (r"(ignore|forget|override|bypass)\s+(all|previous|instruction|system)", 0.95),
        (r"(you\s+are\s+now|start\s+acting\s+as)\s+(an?|the)\s+(unfiltered|jailbroken|evil)", 0.99),
        (r"system\s+prompt|developer\s+mode|root\s+access", 0.8),
    ]

    def __init__(self):
        import re
        self._patterns = [(re.compile(p, re.IGNORECASE), w) for p, w in self.PATTERNS]

    def scan(self, query: str) -> float:
        if not query: return 0.0
        max_score = 0.0
        for pattern, weight in self._patterns:
            if pattern.search(query):
                max_score = max(max_score, weight)
        return max_score

_guard = InjectionGuard()

# -----------------------------------------------------------------------------
# F11: GROUNDED COMMAND AUTHORITY
# -----------------------------------------------------------------------------

def verify_auth(actor_id: str, auth_token: str | None = None, human_approval: bool = False) -> tuple[bool, AuthorityLevel]:
    """F11 Grounded: Aligned with Actor Registry Scopes."""
    actor_id_clean = actor_id.lower().strip()
    
    authority = ACTOR_AUTHORITY.get(actor_id_clean, AuthorityLevel.ANONYMOUS)

    if authority == AuthorityLevel.SOVEREIGN:
        if auth_token and auth_token.upper().strip() == "IM ARIF":
            return True, AuthorityLevel.SOVEREIGN
        if human_approval:
            return True, AuthorityLevel.VERIFIED
        return True, AuthorityLevel.CLAIMED

    return True, authority

# -----------------------------------------------------------------------------
# STAGE 000: GROUNDED INIT
# -----------------------------------------------------------------------------

async def init(
    query: str | Intent,
    actor_id: str | GovernanceMetadata = "anonymous",
    auth_token: str | None = None,
    math_dials: MathDials | dict[str, float] | None = None,
    session_id: str | None = None,
    **kwargs,
) -> InitOutput:
    """Stage 000: Constitutional Airlock (Spec Grounded)."""
    intent = Intent(query=query) if isinstance(query, str) else query
    gov = GovernanceMetadata(actor_id=actor_id) if isinstance(actor_id, str) else actor_id
    
    inj_score = _guard.scan(intent.query)
    if inj_score >= 0.7:
        return InitOutput(session_id="VOID", verdict=Verdict.VOID, error_message="F12: Injection detected.")

    _, authority = verify_auth(gov.actor_id, auth_token, kwargs.get("human_approval", False))
    gov.authority_level = authority.value
    
    if "delete" in intent.query.lower() and authority != AuthorityLevel.SOVEREIGN:
        return InitOutput(session_id="HOLD", verdict=Verdict.HOLD, error_message="F13: Sovereign override required.")

    return InitOutput(
        session_id=session_id or secrets.token_hex(16),
        verdict=Verdict.SEAL,
        governance=gov,
        auth_verified=(authority in {AuthorityLevel.SOVEREIGN, AuthorityLevel.SYSTEM}),
        tri_witness={"human": 1.0, "ai": 1.0, "earth": 1.0}
    )

def get_authority_name(level: AuthorityLevel) -> str:
    return level.value

def validate_token(token: Any) -> tuple[bool, str]:
    return True, "Valid"

def scan_injection(query: str) -> float:
    return _guard.scan(query)

def requires_sovereign(query: str) -> bool:
    high_stakes = ["delete all", "drop table", "format disk", "rm -rf"]
    return any(p in query.lower() for p in high_stakes)

__all__ = ["verify_auth", "init", "get_authority_name", "validate_token", "scan_injection", "requires_sovereign"]

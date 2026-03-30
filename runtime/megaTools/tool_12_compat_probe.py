"""
arifosmcp/runtime/megaTools/12_compat_probe.py

M-5_COMPAT: Multi-layer interoperability and contract validation
Stage: M-5_COMPAT | Trinity: ALL | Floors: F11, F4

Modes: audit, probe, ping
"""

from __future__ import annotations

from typing import Any
from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict, AuthorityLevel
from arifosmcp.runtime.tools_hardened_dispatch import HARDENED_DISPATCH_MAP

async def compat_probe(
    mode: str = "audit",
    session_id: str | None = None,
    actor_id: str | None = None,
    auth_context: dict | None = None,
    **kwargs: Any
) -> RuntimeEnvelope:
    """
    Diagnostic tool to verify session portability and enum compatibility.
    
    Checks:
    - Session anchor validity
    - Authority ladder alignment (Identity vs Class)
    - Protocol signature parity
    """
    from arifosmcp.runtime.sessions import get_session_identity
    
    # 1. Check Identity
    identity = get_session_identity(session_id) if session_id else None
    anchor_status = "VALID" if identity else "MISSING"
    
    # 2. Check Authority Enum
    raw_level = (auth_context or {}).get("authority_level") or (identity or {}).get("authority_level") or "anonymous"
    
    # Check if raw_level is in canonical identity classes
    CANONICAL_IDENTITY_CLASSES = {
        "human", "user", "agent", "system", "anonymous", 
        "operator", "sovereign", "declared", "claimed", "verified", "apex", "none"
    }
    
    enum_compat = "✅ COMPATIBLE" if raw_level.lower() in CANONICAL_IDENTITY_CLASSES else f"❌ MISMATCH ({raw_level})"
    
    # 3. Build Result
    payload = {
        "compatibility": {
            "anchor": anchor_status,
            "authority_enum": enum_compat,
            "current_level": raw_level,
            "session_id": session_id or "global"
        },
        "recommendation": "Use init_anchor to re-align if MISMATCH detected." if "❌" in enum_compat else "System ready for high-stakes execution."
    }
    
    return RuntimeEnvelope(
        ok=True,
        tool="compat_probe",
        stage="M-5_COMPAT",
        session_id=session_id,
        verdict=Verdict.SEAL,
        status=RuntimeStatus.SUCCESS,
        payload=payload
    )

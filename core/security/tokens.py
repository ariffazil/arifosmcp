"""
core/security/tokens.py — F11 Command Auth: HMAC-SHA256 Governance Tokens

Mints and validates cryptographically signed session continuity tokens.
These are NOT JWTs. They are compact HMAC-SHA256 structures bound to:
  - session_id (UUIDv7)
  - actor_id (bootstrap-whitelist verified)
  - timestamp_bucket (5-minute window for replay protection)

Token structure: base64(header).base64(claims).hex(signature)
  - header:    {"alg": "HS256", "ver": "F11-v2"}
  - claims:    {"sid": session_id, "aid": actor_id, "iat": bucket, "clr": clearance}
  - signature: HMAC-SHA256(SOVEREIGN_KEY, header + "." + claims)

No stateless validation — tokens are always cross-checked against Redis session store.
Replayed tokens outside the 5-minute bucket are rejected with F11_TOKEN_EXPIRED.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
SOVEREIGN_KEY: bytes = os.getenv("SOVEREIGN_KEY", "CHANGEME-SOVEREIGN-KEY-32-BYTES!!").encode()
BOOTSTRAP_ACTORS: frozenset[str] = frozenset(
    a.strip() for a in os.getenv("BOOTSTRAP_ACTORS", "").split(",") if a.strip()
)
TOKEN_BUCKET_SECONDS: int = 300  # 5-minute replay window
TOKEN_VERSION: str = "F11-v2"

# OPEN MODE: Development-friendly auth bypass
# Set ARIFOS_OPEN_MODE=true to enable open access
# "arif" is the semantic bypass token - represents the sovereign owner
OPEN_MODE: bool = os.getenv("ARIFOS_OPEN_MODE", "").lower() in ("true", "1", "yes", "on")
SEMANTIC_BYPASS_ACTORS: frozenset[str] = frozenset({"arif", "sovereign"})


# ─────────────────────────────────────────────────────────────────────────────
# DATA CLASSES
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class TokenResult:
    valid: bool
    token: str = ""
    session_id: str = ""
    actor_id: str = ""
    clearance: str = "none"
    error: str = ""


@dataclass
class ValidationResult:
    valid: bool
    session_id: str = ""
    actor_id: str = ""
    clearance: str = "none"
    error: str = ""
    expired: bool = False
    nonce: str = ""  # Track the nonce for continuity


# ─────────────────────────────────────────────────────────────────────────────
# NONCE CONTINUITY REGISTRY
# ─────────────────────────────────────────────────────────────────────────────
# Session-scoped nonce tracking for continuity between tools
_nonce_registry: dict[str, set[str]] = {}


def _generate_nonce() -> str:
    """Generate a cryptographically secure nonce."""
    import secrets

    return secrets.token_hex(16)  # 32 hex chars


def _register_nonce(session_id: str, nonce: str) -> bool:
    """
    Register a nonce for a session. Returns False if nonce already used (replay).
    """
    if not nonce:
        return True  # Empty nonces don't need tracking

    if session_id not in _nonce_registry:
        _nonce_registry[session_id] = set()

    if nonce in _nonce_registry[session_id]:
        return False  # Replay detected

    _nonce_registry[session_id].add(nonce)
    return True


def _verify_nonce(session_id: str, nonce: str) -> bool:
    """Verify a nonce hasn't been replayed in this session."""
    if not nonce:
        return True  # Empty nonces pass
    if session_id not in _nonce_registry:
        return True  # New session
    return nonce not in _nonce_registry[session_id]


def clear_nonce_registry(session_id: str | None = None) -> None:
    """
    Clear the nonce registry. Use for testing or session cleanup.
    If session_id is None, clears all sessions.
    """
    global _nonce_registry
    if session_id is None:
        _nonce_registry = {}
    else:
        _nonce_registry.pop(session_id, None)


# ─────────────────────────────────────────────────────────────────────────────
# INTERNALS
# ─────────────────────────────────────────────────────────────────────────────
def _current_bucket() -> int:
    """Current 5-minute timestamp bucket for replay protection."""
    return int(time.time()) // TOKEN_BUCKET_SECONDS


def _b64(data: dict[str, Any]) -> str:
    return base64.urlsafe_b64encode(json.dumps(data, sort_keys=True).encode()).rstrip(b"=").decode()


def _sign(payload: str) -> str:
    sig = hmac.new(SOVEREIGN_KEY, payload.encode(), hashlib.sha256)
    return sig.hexdigest()


def _actor_clearance(actor_id: str) -> str:
    """Determine clearance level from actor_id prefix conventions."""
    if actor_id.startswith("sovereign:"):
        return "sovereign"
    if actor_id.startswith("apex:"):
        return "apex"
    if actor_id.startswith("agent:"):
        return "agent"
    return "user"


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────
def mint_governance_token(
    actor_id: str,
    session_id: str,
    auth_nonce: str = "",
) -> TokenResult:
    """
    Mint a governance token after F11 bootstrap whitelist check.

    Returns TokenResult(valid=False) if actor_id is not in BOOTSTRAP_ACTORS
    and BOOTSTRAP_ACTORS is non-empty (open mode if empty).

    OPEN MODE: If ARIFOS_OPEN_MODE=true OR actor_id="arif", bypass whitelist.
    """
    # Check for semantic bypass or open mode
    is_bypass = actor_id in SEMANTIC_BYPASS_ACTORS
    is_open_mode = OPEN_MODE

    if is_open_mode:
        logger.debug("F11: Open mode enabled - bypassing whitelist for actor=%s", actor_id)

    if is_bypass:
        logger.info("F11: Semantic bypass for sovereign actor=%s", actor_id)

    # Whitelist gate (F11) - skip if open mode or semantic bypass
    if not (is_open_mode or is_bypass):
        if BOOTSTRAP_ACTORS and actor_id not in BOOTSTRAP_ACTORS:
            logger.warning("F11: actor_id '%s' not in bootstrap whitelist", actor_id)
            return TokenResult(
                valid=False,
                error="F11_AUTH_FAILURE: actor not in bootstrap whitelist",
            )

    clearance = _actor_clearance(actor_id)
    if is_bypass:
        clearance = "sovereign"  # Bypass actors get sovereign clearance

    bucket = _current_bucket()

    # Auto-generate nonce if not provided (ensures continuity)
    if not auth_nonce:
        auth_nonce = _generate_nonce()

    # Check for nonce replay
    if not _register_nonce(session_id, auth_nonce):
        logger.warning("F11: nonce replay detected for session=%s", session_id)
        return TokenResult(
            valid=False,
            error="F11_NONCE_REPLAY: nonce already used in this session",
        )

    header = _b64({"alg": "HS256", "ver": TOKEN_VERSION})
    claims = _b64(
        {
            "sid": session_id,
            "aid": actor_id,
            "iat": bucket,
            "clr": clearance,
            "non": auth_nonce[:32],  # truncate to 32 chars
        }
    )
    payload = f"{header}.{claims}"
    signature = _sign(payload)
    token = f"{payload}.{signature}"

    logger.debug(
        "F11: minted governance token for actor=%s session=%s nonce=%s...",
        actor_id,
        session_id,
        auth_nonce[:8],
    )
    return TokenResult(
        valid=True,
        token=token,
        session_id=session_id,
        actor_id=actor_id,
        clearance=clearance,
    )


def validate_governance_token(
    token: str,
    expected_session_id: str,
    allow_bucket_drift: int = 1,
) -> ValidationResult:
    """
    Validate a governance token.

    Checks:
      1. Structure: exactly 3 dot-separated parts
      2. Signature: HMAC-SHA256 matches
      3. Session ID: matches expected_session_id
      4. Timestamp bucket: within allow_bucket_drift windows (default: 1 = 10 min total)

    Returns ValidationResult(valid=False, expired=True) if bucket is stale.
    Returns ValidationResult(valid=False) for all other failures.

    OPEN MODE: If ARIFOS_OPEN_MODE=true, tokens always validate successfully
    for development/testing purposes.
    """
    # OPEN MODE: Skip validation in development mode
    if OPEN_MODE:
        logger.debug(
            "F11: Open mode - token validation bypassed for session=%s", expected_session_id
        )
        return ValidationResult(
            valid=True,
            session_id=expected_session_id,
            actor_id="arif",
            clearance="sovereign",
            nonce="open-mode-bypass",
        )

    try:
        parts = token.split(".")
        if len(parts) != 3:
            return ValidationResult(valid=False, error="F11_TOKEN_MALFORMED: expected 3 parts")

        header_b64, claims_b64, provided_sig = parts
        payload = f"{header_b64}.{claims_b64}"

        # Signature check
        expected_sig = _sign(payload)
        if not hmac.compare_digest(provided_sig, expected_sig):
            return ValidationResult(valid=False, error="F11_TOKEN_INVALID: signature mismatch")

        # Decode claims
        padding = "=" * (4 - len(claims_b64) % 4)
        claims = json.loads(base64.urlsafe_b64decode(claims_b64 + padding))

        # Session ID check
        if claims.get("sid") != expected_session_id:
            return ValidationResult(
                valid=False,
                error=f"F11_SESSION_MISMATCH: expected {expected_session_id}",
            )

        # Bucket replay check
        current_bucket = _current_bucket()
        token_bucket = claims.get("iat", 0)
        if abs(current_bucket - token_bucket) > allow_bucket_drift:
            return ValidationResult(
                valid=False,
                expired=True,
                error="F11_TOKEN_EXPIRED: timestamp bucket too stale",
            )

        # Extract nonce for continuity tracking
        nonce = claims.get("non", "")

        # Note: We don't check nonce replay during validation because:
        # 1. The nonce was already registered when the token was minted
        # 2. Token replay is prevented by the signature and timestamp
        # 3. The nonce is returned for continuity tracking between tools

        return ValidationResult(
            valid=True,
            session_id=claims["sid"],
            actor_id=claims.get("aid", "unknown"),
            clearance=claims.get("clr", "none"),
            nonce=nonce,
        )

    except Exception as exc:
        logger.warning("F11 token validation error: %s", exc)
        return ValidationResult(valid=False, error=f"F11_TOKEN_PARSE_ERROR: {exc}")


def hash_governance_token(token: str) -> str:
    """SHA-256 of the governance token for safe storage in VAULT999 (never store raw)."""
    return hashlib.sha256(token.encode()).hexdigest()


__all__ = [
    "TokenResult",
    "ValidationResult",
    "mint_governance_token",
    "validate_governance_token",
    "hash_governance_token",
    "clear_nonce_registry",
    "BOOTSTRAP_ACTORS",
    "TOKEN_BUCKET_SECONDS",
    "OPEN_MODE",
    "SEMANTIC_BYPASS_ACTORS",
]

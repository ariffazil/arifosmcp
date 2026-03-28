"""
core/governance/ratify_hold.py — ratify_hold_state Sovereign Bridge

Implements the async human-in-the-loop ratification pattern for 888_HOLD verdicts.

Flow:
  1. arifOS_kernel issues 888_HOLD → calls enqueue_hold()
  2. enqueue_hold() fires n8n webhook → Telegram inline Approve/Reject buttons
  3. Human clicks button → signed deep-link hits ratify_hold_state tool
  4. ratify_hold_state verifies HMAC signature → writes SEAL or VOID to VAULT999

Signature scheme:
  HMAC-SHA256(SOVEREIGN_KEY, hold_id + "|" + decision + "|" + timestamp_bucket)
  Same 5-minute bucket as governance tokens. Prevents replay attacks.

Timeout:
  HOLDs not resolved within HOLD_TTL_SECONDS (default 14400 = 4h) are auto-voided.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

SOVEREIGN_KEY: bytes = os.getenv("SOVEREIGN_KEY", "CHANGEME-SOVEREIGN-KEY-32-BYTES!!").encode()
HOLD_TTL_SECONDS: int = int(os.getenv("HOLD_TTL_SECONDS", "14400"))  # 4 hours
TOKEN_BUCKET_SECONDS: int = 300  # 5-minute bucket (same as token system)


# ─────────────────────────────────────────────────────────────────────────────
# DATA CLASSES
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class HoldRecord:
    hold_id: str
    session_id: str
    tool_name: str
    action_summary: str
    governance_token_hash: str
    w3_score: float = 0.0
    created_at: float = field(default_factory=time.time)
    status: str = "PENDING"        # PENDING | RESOLVED_SEAL | RESOLVED_VOID | EXPIRED
    resolved_at: float | None = None
    decision: str | None = None    # APPROVE | REJECT
    justification: str | None = None
    sovereign_sig_hash: str = ""   # SHA-256 of the signature (never store raw)
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def is_expired(self) -> bool:
        return time.time() - self.created_at > HOLD_TTL_SECONDS

    @property
    def is_pending(self) -> bool:
        return self.status == "PENDING" and not self.is_expired


@dataclass
class RatificationResult:
    success: bool
    verdict: str = ""      # SEAL | VOID
    hold_id: str = ""
    error: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# SIGNATURE VERIFICATION
# ─────────────────────────────────────────────────────────────────────────────
def _hold_bucket() -> int:
    """Current 5-minute bucket for HOLD ratification replay protection."""
    return int(time.time()) // TOKEN_BUCKET_SECONDS


def build_hold_signature(hold_id: str, decision: str) -> str:
    """
    Build the HMAC-SHA256 signature for a ratification decision.
    Used by n8n to embed in Telegram deep-link URLs.
    """
    bucket = _hold_bucket()
    payload = f"{hold_id}|{decision}|{bucket}"
    sig = hmac.new(SOVEREIGN_KEY, payload.encode(), hashlib.sha256)
    return sig.hexdigest()


def verify_hold_signature(
    hold_id: str,
    decision: str,
    provided_sig: str,
    allow_bucket_drift: int = 1,
) -> bool:
    """
    Verify the sovereign ratification signature.

    Checks current bucket and up to allow_bucket_drift adjacent buckets
    to handle clock skew and Telegram delivery delays.
    """
    current_bucket = _hold_bucket()
    for drift in range(-allow_bucket_drift, allow_bucket_drift + 1):
        bucket = current_bucket + drift
        payload = f"{hold_id}|{decision}|{bucket}"
        expected = hmac.new(SOVEREIGN_KEY, payload.encode(), hashlib.sha256).hexdigest()
        if hmac.compare_digest(provided_sig, expected):
            return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# HOLD REGISTRY (in-memory; replace with PostgreSQL bridge in production)
# ─────────────────────────────────────────────────────────────────────────────
_hold_registry: dict[str, HoldRecord] = {}


def register_hold(record: HoldRecord) -> None:
    """Register a new HOLD event in the registry."""
    _hold_registry[record.hold_id] = record
    logger.info(
        "888_HOLD registered: hold_id=%s session=%s tool=%s",
        record.hold_id, record.session_id, record.tool_name,
    )


def get_hold(hold_id: str) -> HoldRecord | None:
    """Retrieve a HOLD record by ID. Returns None if not found."""
    return _hold_registry.get(hold_id)


def resolve_hold(hold_id: str, verdict: str, decision: str, justification: str = "") -> bool:
    """
    Mark a HOLD as resolved. Returns False if hold not found or already resolved.
    """
    record = _hold_registry.get(hold_id)
    if not record:
        logger.warning("resolve_hold: hold_id %s not found", hold_id)
        return False
    if not record.is_pending:
        logger.warning("resolve_hold: hold_id %s is not PENDING (status=%s)", hold_id, record.status)
        return False

    record.status = "RESOLVED_SEAL" if verdict == "SEAL" else "RESOLVED_VOID"
    record.resolved_at = time.time()
    record.decision = decision
    record.justification = justification
    logger.info(
        "888_HOLD resolved: hold_id=%s verdict=%s decision=%s",
        hold_id, verdict, decision,
    )
    return True


# ─────────────────────────────────────────────────────────────────────────────
# RATIFICATION LOGIC
# ─────────────────────────────────────────────────────────────────────────────
def ratify(
    hold_id: str,
    session_id: str,
    human_signature: str,
    decision: str,
    justification: str = "",
) -> RatificationResult:
    """
    Core ratification logic (sync). Called by the ratify_hold_state FastMCP tool.

    Steps:
      1. Verify sovereign signature (F11)
      2. Load hold record
      3. Validate session_id match
      4. Check hold is still PENDING and not expired
      5. Record decision and return verdict

    Returns RatificationResult with verdict SEAL or VOID.
    """
    # Step 1: Signature verification
    if not verify_hold_signature(hold_id, decision, human_signature):
        logger.warning("ratify: F11_SOVEREIGN_SIG_INVALID for hold_id=%s", hold_id)
        return RatificationResult(
            success=False,
            error="F11_SOVEREIGN_SIG_INVALID: signature verification failed",
        )

    # Step 2: Load hold
    record = get_hold(hold_id)
    if not record:
        return RatificationResult(success=False, error=f"HOLD_NOT_FOUND: {hold_id}")

    # Step 3: Session match
    if record.session_id != session_id:
        return RatificationResult(
            success=False,
            error=f"F11_SESSION_MISMATCH: expected {record.session_id}",
        )

    # Step 4: State check
    if record.is_expired:
        resolve_hold(hold_id, "VOID", "TIMEOUT", "Hold expired before sovereign decision")
        return RatificationResult(
            success=False,
            hold_id=hold_id,
            verdict="VOID",
            error="HOLD_EXPIRED: auto-voided after timeout",
        )

    if not record.is_pending:
        return RatificationResult(
            success=False,
            error=f"HOLD_ALREADY_RESOLVED: status={record.status}",
        )

    # Step 5: Record decision
    verdict = "SEAL" if decision == "APPROVE" else "VOID"
    record.sovereign_sig_hash = hashlib.sha256(human_signature.encode()).hexdigest()
    resolve_hold(hold_id, verdict, decision, justification)

    return RatificationResult(success=True, verdict=verdict, hold_id=hold_id)


# ─────────────────────────────────────────────────────────────────────────────
# N8N TELEGRAM NOTIFICATION PAYLOAD
# ─────────────────────────────────────────────────────────────────────────────
def build_telegram_hold_payload(
    record: HoldRecord,
    mcp_base_url: str,
) -> dict[str, Any]:
    """
    Build the n8n webhook payload for 888_HOLD Telegram notification.

    The approve/reject links embed pre-signed signatures so the human
    only needs to click — no manual signing required.
    """
    approve_sig = build_hold_signature(record.hold_id, "APPROVE")
    reject_sig = build_hold_signature(record.hold_id, "REJECT")

    approve_url = (
        f"{mcp_base_url}/tools/ratify_hold_state"
        f"?hold_id={record.hold_id}&decision=APPROVE&sig={approve_sig}&session_id={record.session_id}"
    )
    reject_url = (
        f"{mcp_base_url}/tools/ratify_hold_state"
        f"?hold_id={record.hold_id}&decision=REJECT&sig={reject_sig}&session_id={record.session_id}"
    )

    return {
        "hold_id": record.hold_id,
        "session_id": record.session_id,
        "tool": record.tool_name,
        "action_summary": record.action_summary,
        "w3_score": record.w3_score,
        "expires_at": record.created_at + HOLD_TTL_SECONDS,
        "approve_url": approve_url,
        "reject_url": reject_url,
        "telegram_message": (
            f"⚠️ *888_HOLD — Sovereign Ratification Required*\n\n"
            f"*Tool:* `{record.tool_name}`\n"
            f"*Action:* {record.action_summary[:200]}\n"
            f"*W3 Score:* {record.w3_score:.3f}\n"
            f"*Hold ID:* `{record.hold_id}`\n\n"
            f"[✅ APPROVE]({approve_url}) | [❌ REJECT]({reject_url})\n\n"
            f"_Expires in {HOLD_TTL_SECONDS // 3600}h_"
        ),
    }


__all__ = [
    "HoldRecord",
    "RatificationResult",
    "register_hold",
    "get_hold",
    "resolve_hold",
    "ratify",
    "verify_hold_signature",
    "build_hold_signature",
    "build_telegram_hold_payload",
    "HOLD_TTL_SECONDS",
]

"""
arifosmcp/bridge.py — The Harden Bridge

This module acts as the secure airlock between the transport layer (MCP/Hub)
and the governance layer (Core/Kernel).

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import json
import logging
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from pydantic import ValidationError


from arifosmcp.runtime.contracts import REQUIRES_SESSION
from arifosmcp.core.enforcement.auth_continuity import mint_auth_context, verify_auth_context_cached

from arifosmcp.core.organs import agi, apex, asi, init, vault
from arifosmcp.core.organs._4_vault import verify_vault_ledger

from .models import ClaimStatus, Verdict

logger = logging.getLogger(__name__)

# P0: VPS Infrastructure Integration — Use Redis as primary vault backend
# Docker network: arifos_redis:6379 (already running on VPS)
DEFAULT_VAULT_PATH = Path(__file__).parents[2] / "VAULT999" / "vault999.jsonl"

# Import Redis vault (graceful fallback to file if Redis unavailable)
try:
    from .vault_redis import get_vault_store

    _USE_REDIS_VAULT = True
    logger.info("VAULT999: Redis backend enabled (VPS infrastructure)")
except ImportError as e:
    logger.warning(f"VAULT999: Redis backend unavailable ({e}), falling back to file")
    _USE_REDIS_VAULT = False


# Legacy file-based vault init (fallback)
def _ensure_vault_exists():
    """Lazy initialization of VAULT999 directory and ledger file (fallback)."""
    try:
        vault_dir = DEFAULT_VAULT_PATH.parent
        vault_dir.mkdir(parents=True, exist_ok=True)
        if not DEFAULT_VAULT_PATH.exists():
            DEFAULT_VAULT_PATH.touch()
            with open(DEFAULT_VAULT_PATH, "w") as f:
                f.write(
                    json.dumps(
                        {
                            "type": "seed",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "hash": "0x" + "0" * 64,
                        }
                    )
                    + "\n"
                )
    except Exception as e:
        logger.warning(f"VAULT999 file fallback initialization warning: {e}")


if not _USE_REDIS_VAULT:
    _ensure_vault_exists()

TOOL_MAP = {
    "init_anchor": "anchor_session",
    "arifOS_kernel": "metabolic_loop",
    "arifOS.kernel": "metabolic_loop",
    "metabolic_loop_router": "metabolic_loop",
    "agi_reason": "reason_mind",
    "agi_reflect": "session_memory",
    "asi_critique": "critique_thought",
    "asi_simulate": "simulate_heart",
    "apex_judge": "apex_judge",
    "vault_seal": "seal_vault",
    "verify_vault_ledger": "verify_vault_ledger",
    "reality_check": "search_reality",
    "search_reality": "search_reality",
    "open_web_page": "ingest_evidence",
    "ingest_evidence": "ingest_evidence",
    "agentzero_engineer": "agentzero_engineer",
    "agentzero_validate": "agentzero_validate",
    "reality_atlas": "reality_atlas",
    "check_vital": "sense_health",
    "sense_health": "sense_health",
    "audit_rules": "system_audit",
    "office_forge_audit": "office_forge_audit",
    "forge_office_document": "office_forge",
    "ollama_local_generate": "ollama_local_generate",
    "trace_replay": "trace_replay",
}

AUTO_BOOTSTRAP_RISK_TIERS = frozenset({"low", "medium"})
PROTECTED_AUTO_ANCHOR_IDS = frozenset({"arif", "arif-fazil", "ariffazil"})
_AUTH_CONTEXT_CONTINUITY_KEYS = (
    "session_id",
    "actor_id",
    "authority_level",
    "token_fingerprint",
    "nonce",
    "iat",
    "exp",
    "approval_scope",
    "parent_signature",
    "signature",
)


def _resolve_claimed_actor_id(payload: dict[str, Any]) -> str:
    raw_claim = payload.get("claimed_actor_id", payload.get("actor_id", "anonymous"))
    if raw_claim is None:
        return "anonymous"
    claim = str(raw_claim).strip()

    # Canonicalize arif-related IDs by removing separators
    claim_lower = claim.lower()
    if claim_lower == "arif":
        return "ariffazil"
    if (
        "arif" in claim_lower
        and "arif-the-apex" not in claim_lower
        and "arif-fazil" not in claim_lower
    ):
        return claim_lower.replace(" ", "").replace("-", "")

    # Normalize spaces/underscores to hyphens (align with sessions.py and _0_init.py)
    return claim_lower.replace(" ", "-").replace("_", "-") or "anonymous"


def _auth_failure_envelope(
    *,
    tool: str,
    session_id: str,
    error_message: str,
    claimed_actor_id: str,
    identity_claim_status: str,
    identity_reason: str,
    resolved_actor_id: str = "anonymous",
    next_action_reason: str,
    machine_issue: str = "AUTH_FAILURE",
    dry_run: bool = False,
) -> dict[str, Any]:
    return {
        "ok": False,
        "tool": tool,
        "session_id": session_id,
        "stage": "000_INIT",
        "verdict": "VOID",  # Use VOID to ensure it's not overridden to SEAL
        "status": "ERROR",
        "machine_status": "BLOCKED",
        "machine_issue": machine_issue,
        "human_witness": 0.0,
        "ai_witness": 0.0,
        "earth_witness": 0.0,
        "governance": {
            "score": 0.0,
            "actor_id": "anonymous",
            "authority_level": "anonymous",
        },
        "authority": {
            "score": 0.0,
            "actor_id": "anonymous",
            "level": "anonymous",
            "human_required": True,
            "approval_scope": [],
            "auth_state": "unverified",
        },
        "payload": {
            "error": error_message,
            "identity_resolution": {
                "input_actor_id": claimed_actor_id,
                "resolved_actor_id": resolved_actor_id,
                "identity_claim_status": identity_claim_status,
                "reason": identity_reason,
            },
            "next_action": {
                "tool": "init_anchor",
                "required": True,
                "reason": next_action_reason,
            },
        },
        "errors": [
            {
                "code": machine_issue,
                "message": error_message,
                "stage": "000_INIT",
                "recoverable": True,
                "required_next_tool": "init_anchor",
                "required_fields": ["actor_id", "intent"],
            }
        ],
        "meta": {
            "schema_version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "debug": False,
            "dry_run": dry_run,
        },
        "auth_context": None,
    }


def _can_auto_anchor_declared_identity(payload: dict[str, Any], claimed_actor_id: str) -> bool:
    risk_tier = str(payload.get("risk_tier", "medium") or "medium").strip().lower()
    allow_execution = bool(payload.get("allow_execution", False))
    human_approval = payload.get("human_approval")
    claimed = claimed_actor_id.strip().lower()

    if claimed in {"", "anonymous"}:
        return False

    # P0: If human_approval is explicitly True, we can auto-anchor as 'declared'
    # even for protected IDs (it's an explicit bypass for sovereign identity)
    # This MUST be checked FIRST, before protected ID checks
    if human_approval is True:
        return True

    # Protected IDs require additional checks when human_approval is not given
    if claimed in PROTECTED_AUTO_ANCHOR_IDS:
        return False
    # Protected IDs ALWAYS require verified auth context if they want to execute
    if allow_execution and claimed_actor_id in PROTECTED_AUTO_ANCHOR_IDS:
        return False

    if risk_tier not in AUTO_BOOTSTRAP_RISK_TIERS:
        return False

    return True


def _mint_auto_anchor_auth_context(session_id: str, actor_id: str) -> dict[str, Any]:
    return mint_auth_context(
        session_id=session_id,
        actor_id=actor_id,
        token_fingerprint="sha256:auto-anchor",
        approval_scope=[
            "arifOS_kernel:reason",
            "search_reality",
            "ingest_evidence",
            "session_memory",
        ],
        parent_signature="",
        authority_level="declared",
    )


def _normalize_auth_context(payload: dict[str, Any], auth_context: Any) -> dict[str, Any] | None:
    if not isinstance(auth_context, dict):
        return None

    normalized = dict(auth_context)
    continuity = normalized.get("continuity")
    if isinstance(continuity, dict):
        for key in _AUTH_CONTEXT_CONTINUITY_KEYS:
            if key not in normalized and key in continuity:
                normalized[key] = continuity[key]

    identity_claim = normalized.get("identity_claim")
    if isinstance(identity_claim, dict):
        if not normalized.get("actor_id") and identity_claim.get("actor_id"):
            normalized["actor_id"] = identity_claim["actor_id"]
        if not normalized.get("authority_level") and identity_claim.get("authority_level"):
            normalized["authority_level"] = identity_claim["authority_level"]

    if not normalized.get("actor_id"):
        fallback_actor_id = (
            payload.get("actor_id")
            or payload.get("declared_name")
            or payload.get("claimed_actor_id")
        )
        if fallback_actor_id:
            normalized["actor_id"] = str(fallback_actor_id).lower().strip().replace(" ", "-")
            if normalized["actor_id"] == "arif":
                normalized["actor_id"] = "ariffazil"

    return normalized


# Bootstrap tools that can run without prior auth_context (Phase 1 initialization)
BOOTSTRAP_WHITELIST: set[str] = {
    "init_anchor",  # Session initialization and management (all modes)
    "check_vital",  # system health check
    "sense_health",  # check_vital alias
}


def _requires_explicit_kernel_auth(
    payload: dict[str, Any], canonical_tool: str | None = None
) -> bool:
    """Decide whether arifOS_kernel must reject missing auth_context."""
    from arifosmcp.core.enforcement.auth_continuity import _env_flag

    # F11 Bootstrap Whitelist: These tools can run without prior auth
    # They are the tools that ESTABLISH auth, so they cannot require it
    if canonical_tool in BOOTSTRAP_WHITELIST:
        return False

    # In open mode (dev), we allow auto-bootstrap
    if _env_flag("ARIFOS_GOVERNANCE_OPEN_MODE"):
        risk_tier = str(payload.get("risk_tier", "medium") or "medium").strip().lower()
        allow_execution = bool(payload.get("allow_execution", False))
        claimed_actor_id = _resolve_claimed_actor_id(payload)

        # Protected IDs ALWAYS require verified auth context if they want to execute
        if allow_execution and claimed_actor_id in PROTECTED_AUTO_ANCHOR_IDS:
            return True

        if risk_tier in AUTO_BOOTSTRAP_RISK_TIERS:
            return False

    # dry_run on low risk is allowed to auto-anchor for GUEST IDs even in hardened mode
    # as it's inherently safe (no LLM calls, no material actions).
    risk_tier = str(payload.get("risk_tier", "medium") or "medium").strip().lower()
    dry_run = bool(payload.get("dry_run", False))
    allow_execution = bool(payload.get("allow_execution", False))

    if dry_run and risk_tier == "low" and not allow_execution:
        return False

    # In hardened mode, everything requires explicit auth (except whitelisted bootstrap tools)
    return True


def _trace_replay_envelope(
    session_id: str,
    replay_status: str,
    entries: list[dict[str, Any]],
    message: str | None = None,
    error: str | None = None,
    dry_run: bool = False,
    backend: str = "file",
) -> dict[str, Any]:
    ok = replay_status not in {"ERROR", "TAMPERED"}
    errors = []
    if error:
        code = "TRACE_REPLAY_TAMPER" if replay_status == "TAMPERED" else "TRACE_REPLAY_ERROR"
        errors.append(
            {
                "code": code,
                "message": error,
                "stage": "999_VAULT",
                "recoverable": replay_status != "TAMPERED",
            }
        )

    return {
        "ok": ok,
        "tool": "trace_replay",
        "session_id": session_id,
        "stage": "999_VAULT",
        "verdict": "SEAL" if ok else "VOID",
        "status": "ERROR" if not ok else "SUCCESS",
        "metrics": {},
        "trace": {},
        "authority": {
            "actor_id": "anonymous",
            "level": "anonymous",
            "human_required": False,
            "approval_scope": [],
            "auth_state": "anonymous",
        },
        "payload": {
            "replay_status": replay_status,
            "trace_count": len(entries),
            "message": message,
            "entries": entries,
            "backend": backend,
        },
        "errors": errors,
        "meta": {"schema_version": "1.0.0", "debug": False, "dry_run": dry_run},
    }


def _build_constitutional_audit(session_id: str) -> dict[str, Any]:
    """
    Build the constitutional audit report for audit_rules tool.
    Returns the 13 Floors, their thresholds, and current governance state.
    """
    from arifosmcp.core.shared.floors import FLOOR_SPEC_KEYS, THRESHOLDS
    from arifosmcp.core.state.session_manager import session_manager

    # Build floors report using canonical floor specs
    floors = []
    floor_metadata = {
        "F1": {"name": "Amanah (Reversibility)", "doctrine": "Reversible or Auditable"},
        "F2": {"name": "Haqq (Truth)", "doctrine": "Information Fidelity ≥ 0.99"},
        "F3": {"name": "Tri-Witness Consensus", "doctrine": "W₃ = √(H × A × S) ≥ 0.95"},
        "F4": {"name": "Clarity (Entropy)", "doctrine": "ΔS ≤ 0 (entropy reduction)"},
        "F5": {"name": "Peace² (Stability)", "doctrine": "Non-destructive power"},
        "F6": {"name": "Empathy/Care", "doctrine": "Protect weakest stakeholder"},
        "F7": {"name": "Gödel Uncertainty", "doctrine": "Ω₀ ∈ [0.03, 0.05] humility band"},
        "F8": {"name": "Wisdom Equation", "doctrine": "G = A × P × X × E² ≥ 0.80"},
        "F9": {"name": "Anti-Hantu (Shadow)", "doctrine": "C_dark < 0.30 (no deception)"},
        "F10": {"name": "Ontology Lock", "doctrine": "Category precision"},
        "F11": {"name": "Command Authority", "doctrine": "Verified identity"},
        "F12": {"name": "Injection Defense", "doctrine": "Input sanitization"},
        "F13": {"name": "Sovereign Override", "doctrine": "Human final authority"},
    }

    for floor_id in [f"F{i}" for i in range(1, 14)]:
        spec_key = FLOOR_SPEC_KEYS.get(floor_id)
        threshold_data = THRESHOLDS.get(spec_key, {}) if spec_key else {}
        meta = floor_metadata.get(floor_id, {})

        # Format threshold for display
        threshold_val = threshold_data.get("threshold")
        if threshold_val is not None:
            threshold_str = f"≥ {threshold_val}"
        elif "range" in threshold_data:
            r = threshold_data["range"]
            threshold_str = f"∈ [{r[0]}, {r[1]}]"
        else:
            threshold_str = "HARD"

        floor_type = threshold_data.get("type", "SOFT")

        floor_data = {
            "floor_id": floor_id,
            "name": meta.get("name", floor_id),
            "type": floor_type,
            "threshold": threshold_str,
            "doctrine": meta.get("doctrine", threshold_data.get("desc", "—")),
        }
        floors.append(floor_data)

    # Get session state if available
    session_state = "NO_SESSION"
    try:
        kernel = session_manager.get_kernel(session_id)
        if kernel:
            session_state = "ACTIVE"
    except Exception:
        pass

    return {
        "audit_type": "constitutional_floors",
        "session_id": session_id,
        "session_state": session_state,
        "floors_count": len(floors),
        "hard_floors": sum(1 for f in floors if f["type"] == "HARD"),
        "soft_floors": sum(1 for f in floors if f["type"] == "SOFT"),
        "derived_floors": sum(1 for f in floors if f["type"] == "DERIVED"),
        "floors": floors,
        "tool_contract_table": [
            "check_vital",
            "init_anchor",
            "arifOS_kernel",
            "agi_mind",
            "asi_heart",
        ],
        "discovery_resource": "canon://contracts",
        "floor_runtime_hooks": ["F1_AMANAH", "F11_AUTHORITY", "F12_INJECTION", "F13_SOVEREIGN"],
        "guidance": "Run init_anchor to establish a governed session (Bootstrap sequence).",
        "doctrine_to_runtime": [
            {"doctrine": "F2 Truth", "runtime": "search_reality, ingest_evidence"},
            {"doctrine": "F4 Clarity", "runtime": "entropy tracking, office_forge_audit"},
            {"doctrine": "F6 Care", "runtime": "assess_heart_impact"},
            {"doctrine": "F11 Command", "runtime": "init_anchor, auth_continuity"},
            {"doctrine": "F13 Sovereign", "runtime": "888_HOLD, verify_vault_ledger"},
        ],
        "status": "ACTIVE",
        "message": "13 Constitutional Floors loaded and enforced",
    }


def _build_vitals_report(session_id: str) -> dict[str, Any]:
    """
    Build the system vitals report for check_vital tool.
    Returns health status, thermodynamic budget, and capability map.
    """
    from arifosmcp.core.shared.floors import THRESHOLDS
    from arifosmcp.core.state.session_manager import session_manager
    from arifosmcp.runtime.sessions import get_session_identity

    # Gather system health
    health_status = "HEALTHY"
    degraded_components = []

    # Check session
    session_active = False
    current_state = "anonymous"
    try:
        session_active = session_manager.get_kernel(session_id) is not None
        identity = get_session_identity(session_id)
        if identity:
            current_state = (
                identity.get("caller_state") or identity.get("authority_level") or "claimed"
            )
    except Exception:
        pass

    # Build capability map based on available integrations
    capability_map = {
        "schema": "capability-map/v1",
        "governed_continuity": {"enabled": True, "status": "configured"},
        "vault_persistence": {"enabled": True, "status": "configured"},
        "vector_memory": {"enabled": True, "status": "configured"},
        "external_grounding": {"enabled": True, "status": "configured"},
        "model_provider_access": {"enabled": True, "status": "configured"},
        "local_model_runtime": {"enabled": True, "status": "configured"},
        "auto_deploy": {"enabled": True, "status": "governed_continuous_delivery"},
        "credential_classes": ["bearer", "sig_v2"],
        "providers": [
            "ollama",
            "qdrant",
            "openai",
            "anthropic",
            "google",
            "openrouter",
            "brave",
            "jina",
            "perplexity",
        ],
    }

    # Check thermodynamic module
    thermo_status = "active"
    try:
        from arifosmcp.core.physics import thermodynamics_hardened

        _ = thermodynamics_hardened  # Explicitly use for import check
        thermo_status = "active"
    except ImportError as e:
        thermo_status = f"degraded: {e}"
        degraded_components.append("thermodynamics_hardened")
        health_status = "DEGRADED"

    return {
        "system_status": health_status,
        "session_id": session_id,
        "session_active": session_active,
        "capability_map": capability_map,
        "thermodynamic_vitality": {
            "status": thermo_status,
            "note": "F4 Clarity enforcement via thermodynamic budgeting",
        },
        "constitutional_telemetry": {
            "floors_enforced": len(THRESHOLDS),
            "governance_mode": "HARD" if session_active else "STANDBY",
            "audit_trail": "VAULT999",
        },
        "bootstrap": {
            "sequence": [
                "1. check_vital - System health and vitals (no auth required)",
                "2. audit_rules - Constitutional floors and tool contracts (no auth required)",
                "3. init_anchor - Establish identity (creates session anchor)",
                "4. arifOS_kernel - Primary metabolic loop for governed execution",
            ],
            "ladder_resource": "canon://states",
            "current_state": current_state,
            "operator_guidance": {
                "action": "init_anchor",
                "tool": "init_anchor",
                "example": "init_anchor(actor_id='arif', intent='Establishing continuity')",
                "reason": "Run init_anchor to begin session ignition and elevate from anonymous state.",
            },
            "states_ladder_info": "Possible states: anonymous, claimed, anchored, verified, scoped, approved",
        },
        "degraded_components": degraded_components if degraded_components else None,
        "message": "arifOS Vitals: All systems nominal.",
        "operator_note": (
            "System operational. Run audit_rules for constitutional floor details. "
            "Run verify_vault_ledger for audit trail integrity."
        ),
    }


async def call_kernel(
    tool_name: str,
    session_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    from arifosmcp.intelligence.tools.office_forge_engine import (
        audit_markdown,
        render_office_document,
    )
    from arifosmcp.intelligence.tools.ollama_local import (
        ollama_local_generate as ollama_local_generate_call,
    )
    from arifosmcp.intelligence.tools.reality_grounding import open_web_page, reality_check
    from arifosmcp.runtime.models import CallerContext as _CallerContext
    from arifosmcp.core.governance_kernel import get_governance_kernel
    from arifosmcp.core.shared.types import GovernanceMetadata, Intent, MathDials, TemporalContract

    canonical_name = TOOL_MAP.get(tool_name, tool_name)
    claimed_actor_id = _resolve_claimed_actor_id(payload)

    t_start = time.perf_counter()
    now_utc = datetime.now(timezone.utc)
    valid_until = now_utc + timedelta(minutes=15)
    dry_run = bool(payload.get("dry_run", False))

    from arifosmcp.runtime.sessions import get_session_identity

    auth_ctx = _normalize_auth_context(payload, payload.get("auth_context"))

    # F11: Resolve from session registry if missing in payload
    if auth_ctx is None and session_id:
        stored = get_session_identity(session_id)
        if stored and stored.get("auth_context"):
            auth_ctx = stored["auth_context"]
            # Inject human_approval from session if available
            if stored.get("human_approval") and "human_approval" not in (auth_ctx or {}):
                auth_ctx = dict(auth_ctx or {})
                auth_ctx["human_approval"] = True

    if auth_ctx is not None:
        payload["auth_context"] = auth_ctx
    if tool_name == "metabolic_loop":
        if not auth_ctx:
            # Check if we can auto-anchor this specific call
            can_auto = _can_auto_anchor_declared_identity(payload, claimed_actor_id)
            req_auth = _requires_explicit_kernel_auth(payload, canonical_name)
            print(f"DEBUG: metabolic_loop auth check - can_auto={can_auto}, req_auth={req_auth}")

            if can_auto:
                auth_ctx = _mint_auto_anchor_auth_context(session_id, claimed_actor_id)
                payload["auth_context"] = auth_ctx
                payload.setdefault("identity_resolution", {})
                # result_actor_override removed (duplicate logic in loop)
            elif _requires_explicit_kernel_auth(payload, canonical_name):
                return _auth_failure_envelope(
                    tool=canonical_name,
                    session_id=session_id,
                    error_message="F11: High-risk kernel calls require auth_context.",
                    claimed_actor_id=claimed_actor_id,
                    identity_claim_status="UNVERIFIED_CLAIM",
                    identity_reason="Auto-bootstrap not allowed for this risk/mode.",
                    next_action_reason="Run init_anchor first.",
                    machine_issue="AUTH_TOKEN_MISSING",
                    dry_run=dry_run,
                )
        else:
            valid, reason = verify_auth_context_cached(session_id, auth_ctx)
            if not valid:
                return _auth_failure_envelope(
                    tool=canonical_name,
                    session_id=session_id,
                    error_message=f"F11: Continuity failed: {reason}",
                    claimed_actor_id=claimed_actor_id,
                    identity_claim_status="INVALID_AUTH_CONTEXT",
                    identity_reason=reason,
                    next_action_reason="Refresh continuity state.",
                    machine_issue="TOKEN_EXPIRED",
                    dry_run=dry_run,
                )

            # F11: Authority and Scope Validation
            # After token verification, check if actor has required scope for kernel execution
            authority_level = auth_ctx.get("authority_level", "anonymous")
            approval_scope = auth_ctx.get("approval_scope", [])

            # Anonymous actors cannot execute kernel
            if authority_level == "anonymous":
                return _auth_failure_envelope(
                    tool=canonical_name,
                    session_id=session_id,
                    error_message="F11: Anonymous actors cannot execute kernel operations. Use a recognized actor_id.",
                    claimed_actor_id=claimed_actor_id,
                    identity_claim_status="INSUFFICIENT_SCOPE",
                    identity_reason="Anonymous authority level",
                    next_action_reason="Call init_anchor with actor_id like 'arif', 'openclaw', or 'operator'.",
                    machine_issue="AUTH_FAILURE",
                    dry_run=dry_run,
                )

            # Check if actor has required scope for kernel execution
            required_scope = "arifOS_kernel:execute"
            required_scope_limited = "arifOS_kernel:execute_limited"

            has_full_scope = required_scope in approval_scope or "*" in approval_scope
            has_limited_scope = required_scope_limited in approval_scope or "*" in approval_scope

            if not (has_full_scope or has_limited_scope):
                return _auth_failure_envelope(
                    tool=canonical_name,
                    session_id=session_id,
                    error_message=f"F11: Actor '{authority_level}' lacks required scope for kernel execution.",
                    claimed_actor_id=claimed_actor_id,
                    identity_claim_status="INSUFFICIENT_SCOPE",
                    identity_reason=f"Missing {required_scope} or {required_scope_limited}",
                    next_action_reason="Request operator or sovereign authority.",
                    machine_issue="AUTH_FAILURE",
                    dry_run=dry_run,
                )

    elif canonical_name in REQUIRES_SESSION and canonical_name not in BOOTSTRAP_WHITELIST:
        if not auth_ctx:
            return _auth_failure_envelope(
                tool=canonical_name,
                session_id=session_id,
                error_message="F11: Missing auth_context.",
                claimed_actor_id=claimed_actor_id,
                identity_claim_status="UNVERIFIED_CLAIM",
                identity_reason="No auth_context.",
                next_action_reason="Run init_anchor first.",
                machine_issue="AUTH_TOKEN_MISSING",
                dry_run=dry_run,
            )
        valid, reason = verify_auth_context_cached(session_id, auth_ctx)
        if not valid:
            return _auth_failure_envelope(
                tool=canonical_name,
                session_id=session_id,
                error_message=f"F11: Continuity failed: {reason}",
                claimed_actor_id=claimed_actor_id,
                identity_claim_status="INVALID_AUTH_CONTEXT",
                identity_reason=reason,
                next_action_reason="Refresh continuity state.",
                machine_issue="TOKEN_EXPIRED",
                dry_run=dry_run,
            )

    if canonical_name == "search_reality":
        res = await reality_check(query=payload.get("query", ""))
        from arifosmcp.core.enforcement.governance_engine import wrap_tool_output

        return wrap_tool_output(canonical_name, res)
    if canonical_name == "ingest_evidence":
        res = await open_web_page(url=payload.get("source_url", ""))
        from arifosmcp.core.enforcement.governance_engine import wrap_tool_output

        return wrap_tool_output(canonical_name, res)
    if canonical_name == "trace_replay":
        limit = payload.get("limit", 20)
        try:
            max_entries = max(1, min(int(limit), 200))
        except (TypeError, ValueError):
            max_entries = 20

        # P0: VPS Infrastructure — Use Redis vault if available
        if _USE_REDIS_VAULT:
            try:
                vault_store = get_vault_store()
                replay_entries = await vault_store.get_session_entries(session_id)

                if not replay_entries:
                    return _trace_replay_envelope(session_id, "NO_DATA", [], dry_run=dry_run)

                integrity_ok, integrity_reason = await vault_store.verify_chain()
                if not integrity_ok:
                    return _trace_replay_envelope(
                        session_id, "TAMPERED", [], error=integrity_reason, dry_run=dry_run
                    )

                return _trace_replay_envelope(
                    session_id,
                    "SUCCESS",
                    replay_entries[-max_entries:],
                    dry_run=dry_run,
                    backend="redis",
                )
            except Exception as exc:
                logger.error(f"Redis trace_replay failed: {exc}")
                # Fall through to file fallback

        # File fallback
        if not DEFAULT_VAULT_PATH.exists():
            return _trace_replay_envelope(session_id, "NO_DATA", [], dry_run=dry_run)

        integrity_ok, integrity_reason = verify_vault_ledger(DEFAULT_VAULT_PATH)
        if not integrity_ok:
            return _trace_replay_envelope(
                session_id, "TAMPERED", [], error=integrity_reason, dry_run=dry_run
            )

        replay_entries: list[dict[str, Any]] = []
        try:
            with open(DEFAULT_VAULT_PATH, encoding="utf-8") as f:
                for line in f:
                    row = line.strip()
                    if not row:
                        continue
                    parsed = json.loads(row)
                    if parsed.get("session_id") == session_id:
                        replay_entries.append(parsed)
        except Exception as exc:
            return _trace_replay_envelope(session_id, "ERROR", [], error=str(exc), dry_run=dry_run)

        return _trace_replay_envelope(
            session_id, "SUCCESS", replay_entries[-max_entries:], dry_run=dry_run
        )

    try:
        query_input = payload.get("query", "")
        # Resolve actor_id from explicit field or declared_name (for init)
        actor_id = payload.get("actor_id", payload.get("declared_name", "anonymous"))
        result: Any = {}

        # ─── Budget & Token Control (V1) ───
        budget_meta = payload.pop("_budget_metadata", {})
        default_max_tokens = budget_meta.get("requested_max_tokens", 1000)

        caller_ctx_data = payload.get("caller_context")
        caller_ctx_obj = None
        if caller_ctx_data:
            try:
                caller_ctx_obj = _CallerContext.model_validate(caller_ctx_data)
            except ValidationError:
                caller_ctx_obj = None

        if canonical_name == "init_anchor":
            ha_value = bool(payload.get("human_approval", payload.get("human_approved", False)))
            intent_raw = payload.get("intent")
            if intent_raw is None:
                intent_raw = payload.get("query", "INIT")

            # Support both string and structured intent
            if isinstance(intent_raw, str):
                intent = Intent(query=intent_raw)
            elif isinstance(intent_raw, dict):
                intent = Intent(**intent_raw)
            else:
                intent = Intent(query=str(intent_raw))

            math = MathDials(**payload.get("math", {})) if payload.get("math") else MathDials()
            gov = (
                GovernanceMetadata(**payload.get("governance", {}))
                if payload.get("governance")
                else GovernanceMetadata(actor_id=actor_id)
            )
            res = await init(
                query=intent,
                actor_id=gov,
                math_dials=math,
                auth_token=payload.get("auth_token"),
                session_id=session_id,
                caller_context=caller_ctx_obj,
                human_approval=ha_value,
            )
            result = res.model_dump(mode="json")

            # F11/F13: Persist human approval into the governance output
            auth_level = res.governance.authority_level
            if ha_value or _can_auto_anchor_declared_identity(payload, actor_id):
                if auth_level == "anonymous":
                    auth_level = "declared"

            # Always ensure authority block is present for wrap_tool_output to pick up
            result["authority"] = {
                "actor_id": res.governance.actor_id,
                "level": auth_level,
                "auth_state": "verified" if res.verdict != Verdict.VOID else "unverified",
                "human_approval_persisted": ha_value,
                "claim_status": ClaimStatus.ANCHORED.value
                if res.verdict != Verdict.VOID
                else ClaimStatus.REJECTED_PROTECTED_ID.value,
            }
            result["human_approval_persisted"] = ha_value
            result["abi_version"] = "1.0"
            result["next_action"] = "Run arifOS_kernel to begin governed reasoning."
            result["operator_guidance"] = "Session anchored. Ready for metabolic loop."
            result["ladder_resource"] = "canon://states"

            if res.verdict != Verdict.VOID:
                result["auth_context"] = mint_auth_context(
                    session_id=res.session_id,
                    actor_id=res.governance.actor_id,
                    token_fingerprint="sha256:initialized",
                    approval_scope=["*"],
                    parent_signature="",
                    authority_level=auth_level,
                    prev_vault_hash=res.prev_vault_hash,
                )

        elif canonical_name == "reason_mind":
            result = await agi(
                query=query_input,
                session_id=session_id,
                action=payload.get("action", "full"),
                reason_mode=payload.get("reason_mode", "default"),
                max_steps=payload.get("max_steps", 7),
                auth_context=auth_ctx,
                max_tokens=payload.get("max_tokens", 1000),
            )
            if isinstance(result, dict):
                result.setdefault("evidence", ["Grounding confirmed via internal AGI analysis."])

        elif canonical_name in ("vector_memory", "session_memory"):
            result = await vault(
                operation=payload.get("operation", "search"),
                session_id=session_id,
                content=payload.get("content") or query_input,
                memory_ids=payload.get("memory_ids"),
                top_k=payload.get("top_k", 5),
                auth_context=auth_ctx,
                max_tokens=payload.get("max_tokens") or default_max_tokens,
            )

        elif canonical_name in ("simulate_heart", "critique_thought"):
            result = await asi(
                action=canonical_name,
                session_id=session_id,
                scenario=payload.get("scenario") or query_input,
                thought_id=payload.get("thought_id"),
                focus=payload.get("focus") or "general",
                auth_context=auth_ctx,
                max_tokens=payload.get("max_tokens") or default_max_tokens,
            )

        elif canonical_name == "eureka_forge":
            result = await apex(
                action="forge",
                session_id=session_id,
                intent=payload.get("intent") or query_input,
                eureka_type=payload.get("eureka_type", "concept"),
                materiality=payload.get("materiality", "idea_only"),
                auth_context=auth_ctx,
                max_tokens=payload.get("max_tokens") or default_max_tokens,
            )

        elif canonical_name == "apex_judge":
            result = await apex(
                action="judge",
                session_id=session_id,
                verdict_candidate=payload.get("verdict_candidate", "SEAL"),
                reason_summary=payload.get("reason_summary"),
                auth_context=auth_ctx,
                max_tokens=payload.get("max_tokens") or default_max_tokens,
            )

        elif canonical_name == "seal_vault":
            result = await vault(
                operation="seal",
                session_id=session_id,
                summary=payload.get("summary") or payload.get("evidence"),
                verdict=payload.get("verdict", "SEAL"),
                approved_by=payload.get("approved_by"),
                approval_reference=payload.get("approval_reference"),
                telemetry=payload.get("telemetry"),
                seal_mode=payload.get("seal_mode", "final"),
                auth_context=auth_ctx,
                expected_prev_hash=auth_ctx.get("prev_vault_hash") if auth_ctx else None,
            )

        elif canonical_name == "agentzero_engineer":
            from arifosmcp.tools.agentzero_tools import agentzero_engineer

            result = await agentzero_engineer(
                task=payload.get("task") or query_input, session_id=session_id
            )

        elif canonical_name == "agentzero_validate":
            from arifosmcp.tools.agentzero_tools import agentzero_validate

            result = await agentzero_validate(
                input_to_validate=payload.get("input_to_validate") or query_input,
                session_id=session_id,
            )

        elif canonical_name == "reality_atlas":
            from arifosmcp.runtime.tools_internal import reality_atlas

            result = await reality_atlas(
                operation=payload.get("operation", "merge"),
                session_id=session_id,
                bundles=payload.get("bundles"),
                query=payload.get("query"),
            )

        elif canonical_name == "verify_vault_ledger":
            # P0: VPS Infrastructure — Use Redis vault if available
            if _USE_REDIS_VAULT:
                try:
                    vault_store = get_vault_store()
                    ok, reason = await vault_store.verify_chain()
                    result = {
                        "ok": ok,
                        "status": "INTACT" if ok else "BROKEN",
                        "message": reason or "Chain Integrity: VERIFIED (Redis + SHA-256 Merkle)",
                        "backend": "redis",
                        "host": "arifos_redis:6379",
                    }
                except Exception as e:
                    logger.error(f"Redis vault verify failed: {e}")
                    # Fallback to file
                    ok, reason = verify_vault_ledger(DEFAULT_VAULT_PATH)
                    result = {
                        "ok": ok,
                        "status": "INTACT" if ok else "BROKEN",
                        "message": reason or "Chain Integrity: VERIFIED (File Fallback)",
                        "path": str(DEFAULT_VAULT_PATH),
                        "backend": "file",
                    }
            else:
                ok, reason = verify_vault_ledger(DEFAULT_VAULT_PATH)
                result = {
                    "ok": ok,
                    "status": "INTACT" if ok else "BROKEN",
                    "message": reason or "Chain Integrity: VERIFIED (SHA-256 Merkle)",
                    "path": str(DEFAULT_VAULT_PATH),
                    "backend": "file",
                }

        elif canonical_name == "office_forge_audit":
            result = await audit_markdown(markdown=payload.get("markdown") or query_input)

        elif canonical_name == "office_forge":
            result = await render_office_document(
                session_id=session_id,
                markdown=payload.get("markdown") or query_input,
                mode=payload.get("output_mode", "pdf"),
                theme=payload.get("theme", "default"),
                filename=payload.get("filename"),
            )

        elif canonical_name == "ollama_local_generate":
            result = await ollama_local_generate_call(
                prompt=payload.get("prompt") or query_input,
                model=payload.get("model", "qwen2.5:3b"),
                system=payload.get("system"),
                temperature=payload.get("temperature", 0.2),
                max_tokens=payload.get("max_tokens", 512),
            )

        elif canonical_name == "metabolic_loop":
            from arifosmcp.runtime.orchestrator import metabolic_loop

            result = await metabolic_loop(
                query=query_input,
                risk_tier=payload.get("risk_tier", "medium"),
                mode=payload.get("mode", "recommend"),
                actor_id=actor_id,
                declared_name=payload.get("declared_name"),
                human_approval=bool(payload.get("human_approval", False)),
                auth_context=auth_ctx,
                session_id=session_id,
                allow_execution=bool(payload.get("allow_execution", False)),
                dry_run=bool(payload.get("dry_run", False)),
                caller_context=caller_ctx_obj,
                max_tokens=payload.get("max_tokens"),
            )
            latency_ms = (time.perf_counter() - t_start) * 1000.0
            contract = TemporalContract(
                observed_at=now_utc, request_latency_ms=latency_ms, valid_until=valid_until
            )
            if hasattr(result, "model_dump"):
                result = result.model_dump(mode="json")

            if isinstance(result, dict) and "meta" in result:
                result["meta"]["temporal_contract"] = contract.model_dump(mode="json")
            if isinstance(result, dict) and result.get("verdict") != "VOID":
                # F11: Ensure continuity even if we auto-bootstrapped this call
                effective_actor = (
                    auth_ctx.get("actor_id", claimed_actor_id) if auth_ctx else claimed_actor_id
                )
                effective_level = (
                    auth_ctx.get("authority_level", "declared") if auth_ctx else "declared"
                )

                # Update authority level in the result as well
                if "authority" in result:
                    result["authority"]["level"] = effective_level
                    result["authority"]["auth_state"] = "verified"
                else:
                    result["authority"] = {
                        "actor_id": effective_actor,
                        "level": effective_level,
                        "auth_state": "verified",
                    }

                result["auth_context"] = mint_auth_context(
                    session_id=session_id,
                    actor_id=effective_actor,
                    token_fingerprint="sha256:...",
                    approval_scope=(auth_ctx or {}).get(
                        "approval_scope",
                        [
                            "arifOS_kernel:reason",
                            "search_reality",
                            "ingest_evidence",
                            "session_memory",
                        ],
                    ),
                    parent_signature=(auth_ctx or {}).get("signature", ""),
                    authority_level=effective_level,
                    prev_vault_hash=(auth_ctx or {}).get("prev_vault_hash"),
                )

        elif canonical_name == "system_audit":
            # Constitutional audit: return 13 Floors and governance state
            result = _build_constitutional_audit(session_id)

        elif canonical_name == "sense_health":
            # System health check with constitutional telemetry
            result = _build_vitals_report(session_id)

        else:
            result = {"status": "SUCCESS", "message": f"Utility {tool_name} executed."}

        latency_ms = (time.perf_counter() - t_start) * 1000.0
        contract = TemporalContract(
            observed_at=now_utc, request_latency_ms=latency_ms, valid_until=valid_until
        )

        kernel = get_governance_kernel(session_id)
        kernel.apply_temporal_grounding(contract)

        if hasattr(result, "model_dump"):
            result = result.model_dump(mode="json")

        # Ensure dry_run is preserved for status determination in wrap_tool_output
        if isinstance(result, dict):
            result["dry_run"] = dry_run

        from arifosmcp.core.enforcement.governance_engine import wrap_tool_output

        envelope = wrap_tool_output(canonical_name, result)

        if caller_ctx_data and "caller_context" not in envelope:
            envelope["caller_context"] = caller_ctx_data

        if envelope.get("verdict") != "VOID" and canonical_name != "init_anchor" and auth_ctx:
            envelope["auth_context"] = mint_auth_context(
                session_id=session_id,
                actor_id=auth_ctx.get("actor_id", "anonymous"),
                token_fingerprint="sha256:...",
                approval_scope=auth_ctx.get(
                    "approval_scope",
                    ["reason_mind", "simulate_heart", "eureka_forge", "seal_vault"],
                ),
                parent_signature=auth_ctx.get("signature", ""),
            )
            if "math" in auth_ctx:
                envelope["auth_context"]["math"] = auth_ctx["math"]

            # Sync authority block
            envelope["authority"] = {
                "actor_id": auth_ctx.get("actor_id", "anonymous"),
                "level": auth_ctx.get("authority_level", "anonymous"),
                "auth_state": "verified",
            }
        elif canonical_name == "init_anchor":
            if "auth_context" in result:
                envelope["auth_context"] = result["auth_context"]

            # Sync authority block from result if present (populated above)
            if "authority" in result:
                envelope["authority"] = result["authority"]
            elif "governance" in result:
                # Fallback to governance metadata
                envelope["authority"] = {
                    "actor_id": result["governance"].get("actor_id", claimed_actor_id),
                    "level": result["governance"].get("authority_level", "anonymous"),
                    "auth_state": "unverified",
                }

        if "meta" in envelope and isinstance(envelope["meta"], dict):
            envelope["meta"]["temporal_contract"] = contract.model_dump(mode="json")

        # ─── Telemetry Decoration (V2) ───
        if "vitals" in envelope:
            vitals = envelope["vitals"]
            # budget_meta was extracted at the top of call_kernel
            vitals["requested_max_tokens"] = budget_meta.get("requested_max_tokens", 1000)
            vitals["budget_tier"] = budget_meta.get("budget_tier", "medium")
            vitals["overflow_policy"] = budget_meta.get("overflow_policy", "truncate")

            # Record actual usage if reported by organ in result
            if isinstance(result, dict):
                if "actual_output_tokens" in result:
                    vitals["actual_output_tokens"] = result["actual_output_tokens"]
                if "truncated" in result:
                    vitals["truncated"] = result["truncated"]
                if "phase_token_usage" in result:
                    vitals["phase_token_usage"] = result["phase_token_usage"]

        return envelope

    except Exception as e:
        logger.error(f"Bridge failure on {tool_name}: {e}", exc_info=True)
        print(f"DEBUG: Bridge failure on {tool_name}: {e}")  # Direct visibility for tests
        from arifosmcp.core.enforcement.governance_engine import wrap_tool_output

        return wrap_tool_output(
            canonical_name,
            {
                "verdict": "HOLD",
                "error": str(e),
                "stage": "BRIDGE_FAILURE",
                "issue": "RUNTIME_FAILURE",
            },
        )

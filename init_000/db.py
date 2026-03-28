"""
arifosmcp/init_000/db.py

Database read/write operations for init_000.

All functions return plain dicts (not ORM objects) for simplicity.
JSON fields are serialized/deserialized here.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from arifosmcp.init_000.models import get_connection
from arifosmcp.init_000.schemas import (
    SELF_CLAIM_BOUNDARY_V1,
    ALLOWED_ROLES,
    DRIFT_EVENT_TYPES,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─── Provider Soul Profiles ────────────────────────────────────────────────────


def get_provider_soul(provider_key: str, family_key: str) -> dict[str, Any] | None:
    """Get a provider soul profile by provider_key + family_key."""
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT provider_key, family_key, soul_label,
                   communication_style, reasoning_style, default_role_fit,
                   notes
            FROM provider_soul_profiles
            WHERE provider_key = ? AND family_key = ? AND is_active = 1
            """,
            (provider_key, family_key),
        ).fetchone()
        if not row:
            return None
        return {
            "provider_key": row["provider_key"],
            "family_key": row["family_key"],
            "soul_label": row["soul_label"],
            "communication_style": json.loads(row["communication_style"]),
            "reasoning_style": json.loads(row["reasoning_style"]),
            "default_role_fit": json.loads(row["default_role_fit"]),
            "notes": row["notes"],
        }
    finally:
        conn.close()


def get_fallback_soul() -> dict[str, Any]:
    """Return the unknown_family fallback soul when no profile matches."""
    return {
        "provider_key": "unknown",
        "family_key": "unknown",
        "soul_label": "unknown_family",
        "communication_style": ["unclear"],
        "reasoning_style": ["unknown"],
        "default_role_fit": ["assistant"],
        "notes": "Fallback — no profile found for this provider/family",
    }


def upsert_provider_soul(data: dict[str, Any]) -> dict[str, Any]:
    """Insert or update a provider soul profile."""
    conn = get_connection()
    now = _now()
    try:
        conn.execute(
            """
            INSERT INTO provider_soul_profiles
              (provider_key, family_key, soul_label, communication_style,
               reasoning_style, default_role_fit, notes, version, is_active,
               created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            ON CONFLICT(provider_key, family_key) DO UPDATE SET
              soul_label = excluded.soul_label,
              communication_style = excluded.communication_style,
              reasoning_style = excluded.reasoning_style,
              default_role_fit = excluded.default_role_fit,
              notes = excluded.notes,
              updated_at = excluded.updated_at
            """,
            (
                data["provider_key"],
                data["family_key"],
                data["soul_label"],
                json.dumps(data.get("communication_style", [])),
                json.dumps(data.get("reasoning_style", [])),
                json.dumps(data.get("default_role_fit", [])),
                data.get("notes"),
                data.get("version", "1.0"),
                now,
                now,
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return get_provider_soul(data["provider_key"], data["family_key"])


# ─── Deployments ──────────────────────────────────────────────────────────────


def get_deployment(deployment_id: str) -> dict[str, Any] | None:
    """Get a deployment by deployment_id."""
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT deployment_id, provider_key, family_key, model_id, model_variant,
                   tools_live, web_access, memory_mode, execution_mode,
                   side_effects_allowed, auth_level, verified_at, expires_at, is_active
            FROM deployments
            WHERE deployment_id = ?
            """,
            (deployment_id,),
        ).fetchone()
        if not row:
            return None
        return _row_to_deployment(row)
    finally:
        conn.close()


def _row_to_deployment(row: Any) -> dict[str, Any]:
    return {
        "deployment_id": row["deployment_id"],
        "provider_key": row["provider_key"],
        "family_key": row["family_key"],
        "model_id": row["model_id"],
        "model_variant": row["model_variant"],
        "tools_live": json.loads(row["tools_live"]),
        "web_access": bool(row["web_access"]),
        "memory_mode": row["memory_mode"],
        "execution_mode": row["execution_mode"],
        "side_effects_allowed": bool(row["side_effects_allowed"]),
        "auth_level": row["auth_level"],
        "verified_at": row["verified_at"],
        "expires_at": row["expires_at"],
        "is_active": bool(row["is_active"]),
    }


def upsert_deployment(data: dict[str, Any]) -> dict[str, Any]:
    """Insert or update a deployment."""
    conn = get_connection()
    now = _now()
    try:
        conn.execute(
            """
            INSERT INTO deployments
              (deployment_id, provider_key, family_key, model_id, model_variant,
               tools_live, web_access, memory_mode, execution_mode,
               side_effects_allowed, auth_level, verified_at, expires_at,
               is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(deployment_id) DO UPDATE SET
              provider_key = excluded.provider_key,
              family_key = excluded.family_key,
              model_id = excluded.model_id,
              model_variant = excluded.model_variant,
              tools_live = excluded.tools_live,
              web_access = excluded.web_access,
              memory_mode = excluded.memory_mode,
              execution_mode = excluded.execution_mode,
              side_effects_allowed = excluded.side_effects_allowed,
              auth_level = excluded.auth_level,
              verified_at = excluded.verified_at,
              expires_at = excluded.expires_at,
              is_active = excluded.is_active,
              updated_at = excluded.updated_at
            """,
            (
                data["deployment_id"],
                data["provider_key"],
                data["family_key"],
                data["model_id"],
                data.get("model_variant"),
                json.dumps(data.get("tools_live", [])),
                int(data.get("web_access", False)),
                data.get("memory_mode", "session_only"),
                data.get("execution_mode", "advisory"),
                int(data.get("side_effects_allowed", False)),
                data.get("auth_level", "read_only"),
                data.get("verified_at", now),
                data.get("expires_at"),
                int(data.get("is_active", True)),
                now,
                now,
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return get_deployment(data["deployment_id"])


def is_deployment_fresh(deployment: dict[str, Any]) -> tuple[bool, str]:
    """
    Check if deployment is active and not expired.
    Returns (is_fresh, reason).
    """
    if not deployment.get("is_active"):
        return False, "deployment_is_inactive"
    expires_at = deployment.get("expires_at")
    if expires_at:
        expires_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        if datetime.now(timezone.utc) > expires_dt:
            return False, "deployment_expired"
    return True, ""


# ─── Session Anchors ───────────────────────────────────────────────────────────


def create_session_anchor(
    deployment_id: str,
    provider_key: str,
    family_key: str,
    soul_label: str,
    bound_role: str,
    identity_verified: bool = False,
    runtime_verified: bool = False,
    self_claim_boundary: dict[str, Any] | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    Create a new session anchor.
    Generates session_id if not provided.
    """
    if bound_role not in ALLOWED_ROLES:
        bound_role = "assistant"
    sid = session_id or f"session-{uuid.uuid4().hex[:12]}"
    now = _now()
    boundary = self_claim_boundary or SELF_CLAIM_BOUNDARY_V1

    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO session_anchors
              (session_id, deployment_id, provider_key_snapshot,
               family_key_snapshot, soul_label_snapshot, bound_role,
               self_claim_boundary, identity_verified, runtime_verified,
               created_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
            """,
            (
                sid,
                deployment_id,
                provider_key,
                family_key,
                soul_label,
                bound_role,
                json.dumps(boundary),
                int(identity_verified),
                int(runtime_verified),
                now,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    return get_session_anchor(sid)


def get_session_anchor(session_id: str) -> dict[str, Any] | None:
    """Get a session anchor by session_id."""
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT session_id, deployment_id, provider_key_snapshot,
                   family_key_snapshot, soul_label_snapshot, bound_role,
                   self_claim_boundary, identity_verified, runtime_verified,
                   created_at, ended_at, status
            FROM session_anchors
            WHERE session_id = ?
            """,
            (session_id,),
        ).fetchone()
        if not row:
            return None
        return {
            "session_id": row["session_id"],
            "deployment_id": row["deployment_id"],
            "provider_key_snapshot": row["provider_key_snapshot"],
            "family_key_snapshot": row["family_key_snapshot"],
            "soul_label_snapshot": row["soul_label_snapshot"],
            "bound_role": row["bound_role"],
            "self_claim_boundary": json.loads(row["self_claim_boundary"]),
            "identity_verified": bool(row["identity_verified"]),
            "runtime_verified": bool(row["runtime_verified"]),
            "created_at": row["created_at"],
            "ended_at": row["ended_at"],
            "status": row["status"],
        }
    finally:
        conn.close()


def end_session_anchor(session_id: str) -> dict[str, Any] | None:
    """Mark a session anchor as ended."""
    conn = get_connection()
    now = _now()
    try:
        conn.execute(
            "UPDATE session_anchors SET ended_at = ?, status = 'ended' WHERE session_id = ?",
            (now, session_id),
        )
        conn.commit()
    finally:
        conn.close()
    return get_session_anchor(session_id)


# ─── Drift Events ─────────────────────────────────────────────────────────────


def log_drift_event(
    session_id: str,
    deployment_id: str,
    event_type: str,
    expected_value: str | None = None,
    claimed_value: str | None = None,
    severity: str = "low",
) -> dict[str, Any]:
    """
    Log a drift event.
    event_type must be from DRIFT_EVENT_TYPES.
    """
    if event_type not in DRIFT_EVENT_TYPES:
        event_type = "runtime_state_mismatch"
    event_id = f"drift-{uuid.uuid4().hex[:12]}"
    now = _now()

    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO drift_events
              (event_id, session_id, deployment_id, event_type,
               expected_value, claimed_value, severity, resolved, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
            """,
            (
                event_id,
                session_id,
                deployment_id,
                event_type,
                expected_value,
                claimed_value,
                severity,
                now,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    return get_drift_event(event_id)


def get_drift_event(event_id: str) -> dict[str, Any] | None:
    """Get a drift event by event_id."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM drift_events WHERE event_id = ?",
            (event_id,),
        ).fetchone()
        if not row:
            return None
        return {
            "event_id": row["event_id"],
            "session_id": row["session_id"],
            "deployment_id": row["deployment_id"],
            "event_type": row["event_type"],
            "expected_value": row["expected_value"],
            "claimed_value": row["claimed_value"],
            "severity": row["severity"],
            "resolved": bool(row["resolved"]),
            "created_at": row["created_at"],
        }
    finally:
        conn.close()


def get_drift_events_for_session(session_id: str) -> list[dict[str, Any]]:
    """Get all drift events for a session."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM drift_events WHERE session_id = ? ORDER BY created_at DESC",
            (session_id,),
        ).fetchall()
        return [
            {
                "event_id": r["event_id"],
                "session_id": r["session_id"],
                "deployment_id": r["deployment_id"],
                "event_type": r["event_type"],
                "expected_value": r["expected_value"],
                "claimed_value": r["claimed_value"],
                "severity": r["severity"],
                "resolved": bool(r["resolved"]),
                "created_at": r["created_at"],
            }
            for r in rows
        ]
    finally:
        conn.close()


# ─── Seed Loading ──────────────────────────────────────────────────────────────


def load_seeds_from_dir(seed_dir: str) -> None:
    """Load all JSON seed files from a directory."""
    import os
    from pathlib import Path

    seed_path = Path(seed_dir)
    if not seed_path.exists():
        return

    # Load provider_soul_profiles
    soul_file = seed_path / "provider_soul_profiles.json"
    if soul_file.exists():
        with open(soul_file, "r", encoding="utf-8") as f:
            for item in json.load(f):
                upsert_provider_soul(item)

    # Load deployments
    deploy_file = seed_path / "deployments.json"
    if deploy_file.exists():
        with open(deploy_file, "r", encoding="utf-8") as f:
            for item in json.load(f):
                upsert_deployment(item)

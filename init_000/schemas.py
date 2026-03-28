"""
arifosmcp/init_000/schemas.py

Pydantic request/response models for init_000.

Outer envelope follows arifOS convention:
- ok, tool, status, risk_class, warnings, errors, meta, authority, result

Inner result objects are tool-specific.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field


# ─── Self-Claim Boundary (non-negotiable) ─────────────────────────────────────

SELF_CLAIM_BOUNDARY_V1 = {
    "identity": "provider_family_only_unless_verified",
    "tools": "verified_only",
    "knowledge": "mark_verified_vs_inferred",
    "actions": "mark_executed_vs_suggested",
    "memory": "must_match_runtime_mode",
}


# ─── Allowed Roles ─────────────────────────────────────────────────────────────

ALLOWED_ROLES = {"assistant", "architect", "engineer", "auditor"}


# ─── Drift Event Types ────────────────────────────────────────────────────────

DRIFT_EVENT_TYPES = {
    "identity_claim_mismatch",
    "tool_claim_mismatch",
    "memory_claim_mismatch",
    "action_claim_mismatch",
    "role_drift",
    "runtime_state_mismatch",
}


# ─── Request Models ────────────────────────────────────────────────────────────


class InitAnchorV1Request(BaseModel):
    """Request for init_anchor_v1."""

    deployment_id: str = Field(..., description="Deployment ID to bind session to")
    requested_role: str | None = Field(
        default="assistant",
        description="Requested role: assistant | architect | engineer | auditor",
    )
    provider_key: str | None = Field(
        default=None, description="Optional: for cross-check against deployment record"
    )
    family_key: str | None = Field(
        default=None, description="Optional: for cross-check against deployment record"
    )


class LogDriftRequest(BaseModel):
    """Request for log_drift_event."""

    session_id: str = Field(..., description="Session that produced the drift")
    event_type: str = Field(..., description=f"Type: {', '.join(sorted(DRIFT_EVENT_TYPES))}")
    expected_value: str | None = Field(default=None, description="What the system expected")
    claimed_value: str | None = Field(default=None, description="What was claimed")
    severity: str = Field(default="low", description="low | medium | high | critical")


class GetSessionAnchorRequest(BaseModel):
    """Request for get_session_anchor."""

    session_id: str = Field(..., description="Session ID to look up")


# ─── Response / Result Models ─────────────────────────────────────────────────


class ProviderSoul(BaseModel):
    """Provider soul archetype — routing shorthand, NOT capability proof."""

    provider_key: str
    family_key: str
    soul_label: str
    communication_style: list[str] = Field(default_factory=list)
    reasoning_style: list[str] = Field(default_factory=list)
    default_role_fit: list[str] = Field(default_factory=list)
    notes: str | None = None


class RuntimeTruth(BaseModel):
    """Runtime truth — the law of the running system."""

    deployment_id: str
    provider_key: str
    family_key: str
    model_id: str
    model_variant: str | None = None
    tools_live: list[str] = Field(default_factory=list)
    web_access: bool = False
    memory_mode: str = "session_only"
    execution_mode: str = "advisory"
    side_effects_allowed: bool = False
    auth_level: str = "read_only"
    verified_at: str
    expires_at: str | None = None
    is_active: bool = True


class SessionAnchorData(BaseModel):
    """What was bound during init for this session."""

    session_id: str
    deployment_id: str
    provider_key_snapshot: str
    family_key_snapshot: str
    soul_label_snapshot: str
    bound_role: str
    self_claim_boundary: dict[str, Any] = Field(default_factory=SELF_CLAIM_BOUNDARY_V1)
    identity_verified: bool = False
    runtime_verified: bool = False
    created_at: str
    ended_at: str | None = None
    status: str = "active"


class DriftEventData(BaseModel):
    """A logged drift mismatch event."""

    event_id: str
    session_id: str
    deployment_id: str
    event_type: str
    expected_value: str | None = None
    claimed_value: str | None = None
    severity: str = "low"
    resolved: bool = False
    created_at: str


class InitAnchorV1Result(BaseModel):
    """Inner result for init_anchor_v1."""

    session_id: str
    provider_soul: ProviderSoul
    runtime_truth: RuntimeTruth
    bound_role: str
    self_claim_boundary: dict[str, Any] = Field(default_factory=SELF_CLAIM_BOUNDARY_V1)
    identity_verified: bool = False
    runtime_verified: bool = False
    warnings: list[str] = Field(default_factory=list)


class DeploymentResult(BaseModel):
    """Inner result for get_deployment."""

    deployment: RuntimeTruth | None = None
    soul: ProviderSoul | None = None
    warnings: list[str] = Field(default_factory=list)


class SessionAnchorResult(BaseModel):
    """Inner result for get_session_anchor."""

    anchor: SessionAnchorData | None = None
    warnings: list[str] = Field(default_factory=list)


class DriftEventResult(BaseModel):
    """Inner result for log_drift_event."""

    event_id: str
    session_id: str
    event_type: str
    severity: str
    resolved: bool = False
    warnings: list[str] = Field(default_factory=list)


# ─── Shared Envelope ──────────────────────────────────────────────────────────


class InitV1Envelope(BaseModel):
    """Shared outer envelope for all init_000 tools."""

    ok: bool
    tool: str
    status: str = "SUCCESS"
    risk_class: str = "low"
    machine_status: str = "READY"
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    meta: dict[str, Any] = Field(
        default_factory=lambda: {
            "schema_version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    authority: dict[str, Any] = Field(
        default_factory=lambda: {
            "actor_id": "init_000",
            "level": "system",
            "auth_state": "verified",
        }
    )
    result: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return json.loads(self.model_dump_json())


def make_envelope(
    tool: str,
    ok: bool,
    result: dict[str, Any] | None = None,
    status: str = "SUCCESS",
    risk_class: str = "low",
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
    authority: dict[str, Any] | None = None,
) -> InitV1Envelope:
    """Factory for building envelopes."""
    return InitV1Envelope(
        ok=ok,
        tool=tool,
        status=status if ok else "ERROR",
        risk_class=risk_class,
        warnings=warnings or [],
        errors=errors or [],
        authority=authority
        or {
            "actor_id": "init_000",
            "level": "system",
            "auth_state": "verified",
        },
        result=result,
    )

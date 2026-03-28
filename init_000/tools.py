"""
arifosmcp/init_000/tools.py

FastMCP tool implementations for init_000.

5 tools:
- init_anchor_v1     : bind a session to a deployment
- get_deployment     : look up runtime truth
- get_provider_soul  : look up soul archetype
- get_session_anchor  : look up session anchor
- log_drift_event    : log a mismatch event

All tools follow the shared envelope:
- ok, tool, status, risk_class, warnings, errors, meta, authority, result
"""

from __future__ import annotations

from typing import Any

from arifosmcp.init_000 import db
from arifosmcp.init_000.schemas import (
    InitV1Envelope,
    make_envelope,
    ALLOWED_ROLES,
    SELF_CLAIM_BOUNDARY_V1,
    InitAnchorV1Result,
    DeploymentResult,
    SessionAnchorResult,
    DriftEventResult,
    ProviderSoul,
    RuntimeTruth,
    SessionAnchorData,
    DriftEventData,
)


# ─── Tool Implementations ───────────────────────────────────────────────────────


def init_anchor_v1_impl(
    deployment_id: str,
    requested_role: str | None = None,
    provider_key: str | None = None,
    family_key: str | None = None,
    session_id: str | None = None,
) -> InitV1Envelope:
    """
    Bind a session to a deployment.

    Flow:
    1. Load deployment row
    2. Verify deployment exists and is fresh
    3. Load matching provider_soul_profile (fallback if not found)
    4. Cross-check provider_key/family_key if provided
    5. Bind session anchor
    6. Return envelope with session_id, soul, runtime_truth, boundary
    """
    warnings: list[str] = []
    errors: list[str] = []

    # 1. Load deployment
    deployment = db.get_deployment(deployment_id)
    if not deployment:
        return _error_envelope(
            tool="init_anchor_v1",
            errors=[f"Deployment '{deployment_id}' not found"],
        )

    # 2. Check freshness
    is_fresh, fresh_reason = db.is_deployment_fresh(deployment)
    if not is_fresh:
        return _error_envelope(
            tool="init_anchor_v1",
            errors=[f"Deployment not available: {fresh_reason}"],
        )

    # 3. Load soul (with fallback)
    pk = provider_key or deployment["provider_key"]
    fk = family_key or deployment["family_key"]
    soul = db.get_provider_soul(pk, fk)
    if not soul:
        soul = db.get_fallback_soul()
        warnings.append(f"No soul profile for {pk}/{fk} — using fallback")

    # 4. Optional cross-check
    if provider_key and provider_key != deployment["provider_key"]:
        warnings.append(
            f"provider_key mismatch: requested '{provider_key}' "
            f"but deployment has '{deployment['provider_key']}'"
        )
    if family_key and family_key != deployment["family_key"]:
        warnings.append(
            f"family_key mismatch: requested '{family_key}' "
            f"but deployment has '{deployment['family_key']}'"
        )

    # 5. Bind role
    bound_role = requested_role if requested_role in ALLOWED_ROLES else "assistant"

    # 6. Create session anchor
    anchor = db.create_session_anchor(
        deployment_id=deployment_id,
        provider_key=deployment["provider_key"],
        family_key=deployment["family_key"],
        soul_label=soul["soul_label"],
        bound_role=bound_role,
        session_id=session_id,
    )

    # 7. Build result
    result = {
        "session_id": anchor["session_id"],
        "provider_soul": ProviderSoul(**soul).model_dump(),
        "runtime_truth": RuntimeTruth(**deployment).model_dump(),
        "bound_role": bound_role,
        "self_claim_boundary": SELF_CLAIM_BOUNDARY_V1,
        "identity_verified": anchor["identity_verified"],
        "runtime_verified": anchor["runtime_verified"],
        "warnings": warnings,
    }

    return make_envelope(
        tool="init_anchor_v1",
        ok=True,
        result=result,
        warnings=warnings,
    )


def get_deployment_impl(deployment_id: str) -> InitV1Envelope:
    """Look up runtime truth for a deployment."""
    deployment = db.get_deployment(deployment_id)
    if not deployment:
        return _error_envelope(
            tool="get_deployment",
            errors=[f"Deployment '{deployment_id}' not found"],
        )

    soul = db.get_provider_soul(deployment["provider_key"], deployment["family_key"])
    if not soul:
        soul = db.get_fallback_soul()

    is_fresh, reason = db.is_deployment_fresh(deployment)
    warnings = []
    if not is_fresh:
        warnings.append(f"Deployment may be stale: {reason}")

    result = {
        "deployment": RuntimeTruth(**deployment).model_dump(),
        "soul": ProviderSoul(**soul).model_dump(),
        "warnings": warnings,
    }

    return make_envelope(
        tool="get_deployment",
        ok=True,
        result=result,
        warnings=warnings,
    )


def get_provider_soul_impl(provider_key: str, family_key: str) -> InitV1Envelope:
    """Look up soul archetype for a provider/family."""
    soul = db.get_provider_soul(provider_key, family_key)
    if not soul:
        soul = db.get_fallback_soul()
        return make_envelope(
            tool="get_provider_soul",
            ok=True,
            result={"soul": ProviderSoul(**soul).model_dump()},
            warnings=[f"No soul profile for {provider_key}/{family_key} — returned fallback"],
        )

    return make_envelope(
        tool="get_provider_soul",
        ok=True,
        result={"soul": ProviderSoul(**soul).model_dump()},
    )


def get_session_anchor_impl(session_id: str) -> InitV1Envelope:
    """Look up the session anchor for an active session."""
    anchor = db.get_session_anchor(session_id)
    if not anchor:
        return _error_envelope(
            tool="get_session_anchor",
            errors=[f"Session '{session_id}' not found or has ended"],
        )

    # Get associated drift events
    drift_events = db.get_drift_events_for_session(session_id)

    result = {
        "anchor": SessionAnchorData(**anchor).model_dump(),
        "drift_events": [DriftEventData(**e).model_dump() for e in drift_events],
    }

    return make_envelope(
        tool="get_session_anchor",
        ok=True,
        result=result,
    )


def log_drift_event_impl(
    session_id: str,
    event_type: str,
    expected_value: str | None = None,
    claimed_value: str | None = None,
    severity: str = "low",
) -> InitV1Envelope:
    """Log a drift mismatch event for a session."""
    errors = []

    # Verify session exists
    anchor = db.get_session_anchor(session_id)
    if not anchor:
        errors.append(f"Session '{session_id}' not found — cannot log drift")

    # Validate severity
    valid_severities = {"low", "medium", "high", "critical"}
    if severity not in valid_severities:
        errors.append(f"Invalid severity '{severity}' — must be one of {valid_severities}")

    if errors:
        return _error_envelope(tool="log_drift_event", errors=errors)

    deployment_id = anchor["deployment_id"] if anchor else "unknown"

    event = db.log_drift_event(
        session_id=session_id,
        deployment_id=deployment_id,
        event_type=event_type,
        expected_value=expected_value,
        claimed_value=claimed_value,
        severity=severity,
    )

    result = {
        "event": DriftEventData(**event).model_dump(),
        "message": f"Drift event logged for session {session_id}",
    }

    return make_envelope(
        tool="log_drift_event",
        ok=True,
        result=result,
        warnings=[f"Severity={severity} — review if threshold exceeded"],
    )


# ─── Helper ───────────────────────────────────────────────────────────────────


def _error_envelope(tool: str, errors: list[str]) -> InitV1Envelope:
    return make_envelope(
        tool=tool,
        ok=False,
        errors=errors,
        status="ERROR",
        risk_class="medium",
    )


# ─── FastMCP-compatible wrappers ───────────────────────────────────────────────


def init_anchor_v1(
    deployment_id: str,
    requested_role: str | None = "assistant",
    provider_key: str | None = None,
    family_key: str | None = None,
    session_id: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """FastMCP wrapper — accepts flat kwargs, returns dict."""
    result = init_anchor_v1_impl(
        deployment_id=deployment_id,
        requested_role=requested_role,
        provider_key=provider_key,
        family_key=family_key,
        session_id=session_id,
    )
    return result.to_dict()


def get_deployment(
    deployment_id: str,
    **kwargs: Any,
) -> dict[str, Any]:
    result = get_deployment_impl(deployment_id=deployment_id)
    return result.to_dict()


def get_provider_soul(
    provider_key: str,
    family_key: str,
    **kwargs: Any,
) -> dict[str, Any]:
    result = get_provider_soul_impl(provider_key=provider_key, family_key=family_key)
    return result.to_dict()


def get_session_anchor(
    session_id: str,
    **kwargs: Any,
) -> dict[str, Any]:
    result = get_session_anchor_impl(session_id=session_id)
    return result.to_dict()


def log_drift_event(
    session_id: str,
    event_type: str,
    expected_value: str | None = None,
    claimed_value: str | None = None,
    severity: str = "low",
    **kwargs: Any,
) -> dict[str, Any]:
    result = log_drift_event_impl(
        session_id=session_id,
        event_type=event_type,
        expected_value=expected_value,
        claimed_value=claimed_value,
        severity=severity,
    )
    return result.to_dict()

"""
arifosmcp/runtime/schemas.py — Pydantic Schemas for ABI v1.0

Defines canonical input/output schemas for all 11 mega-tools.
Ensures FastMCP generates correct JSON Schema from type hints.
"""

from __future__ import annotations

from typing import Any, Dict, Literal, Union
from pydantic import BaseModel, Field


# =============================================================================
# P0: Intent Schema (Structured vs Legacy)
# =============================================================================


class IntentSpec(BaseModel):
    """Structured intent specification for governed workflows."""

    query: str = Field(
        ...,  # Required
        description="The primary query or objective",
        min_length=1,
        max_length=20000,
    )
    task_type: str = Field(
        default="general",
        description="Category of task: ask, analyze, design, decide, audit, execute",
        max_length=64,
    )
    domain: str | None = Field(
        default=None,
        description="Domain context: engineering, research, governance, etc.",
        max_length=64,
    )
    desired_output: str | None = Field(
        default=None,
        description="Expected output format: text, json, table, code, report",
        max_length=64,
    )


# P0: Intent can be string (legacy) or object (structured)
IntentType = Union[str, Dict[str, Any], None]


# =============================================================================
# P0: Init Anchor Input Schema
# =============================================================================


class InitAnchorInput(BaseModel):
    """Canonical input schema for init_anchor tool (ABI v1.0)."""

    actor_id: str = Field(
        default="anonymous",
        description="Identity claimed by the caller",
        min_length=2,
        max_length=64,
    )
    declared_name: str | None = Field(
        default=None,
        description="Human-readable display name",
        max_length=64,
    )
    # P0: Intent accepts string (legacy) OR IntentSpec (structured)
    intent: IntentType = Field(
        default=None,
        description="User intent - string (legacy) or structured object with query, task_type, domain",
    )
    session_id: str | None = Field(
        default=None,
        description="Optional session ID for continuity",
        min_length=8,
        max_length=128,
    )
    # P0: Human approval flag (F13 Sovereign override)
    human_approval: bool = Field(
        default=False,
        description="Whether human has pre-approved this action (F13 Sovereign override for protected IDs)",
    )
    reason: str | None = Field(
        default=None,
        description="Reason for action (used with revoke mode)",
        max_length=1000,
    )


# =============================================================================
# P0: Init Anchor Output Schema
# =============================================================================


class IdentityResolution(BaseModel):
    """Identity claim resolution details."""

    claimed_actor_id: str = Field(description="What the caller claimed")
    resolved_actor_id: str | None = Field(description="What the system accepted")
    claim_status: Literal[
        "anonymous", "claimed", "anchored", "verified", "rejected", "demoted", "rejected_protected_id"
    ] = Field(
description="Resolution status of identity claim")
    why_demoted: str | None = Field(
        default=None,
        description="Explanation if identity was demoted",
    )


class InitAnchorOutput(BaseModel):
    """Canonical output schema for init_anchor tool."""

    ok: bool
    session_id: str
    auth_state: Literal["unverified", "anchored", "verified", "rejected"] = Field(
        description="Current authentication state"
    )
    identity: IdentityResolution
    abi_version: str = Field(default="1.0", description="ABI version used")
    # P0: Human approval state
    approval_state: Literal["not_required", "pending", "approved"] = Field(
        default="not_required",
        description="Human approval status",
    )


# =============================================================================
# Mega-Tool Input Schemas (ABI v1.0 Unified Envelope)
# =============================================================================


class MegaToolInput(BaseModel):
    """Unified input envelope for all mega-tools (Item 2)."""

    mode: str = Field(
        ...,  # Required
        description="Operation mode for this mega-tool",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Mode-specific payload data",
    )
    auth_context: dict[str, Any] | None = Field(
        default=None,
        description="Authentication context for continuity (F11)",
    )
    caller_context: dict[str, Any] | None = Field(
        default=None,
        description="Caller metadata",
    )
    risk_tier: Literal["low", "medium", "high", "critical"] = Field(
        default="medium",
        description="Requested risk posture",
    )
    dry_run: bool = Field(
        default=True,
        description="If true, validate only without execution",
    )
    allow_execution: bool = Field(
        default=False,
        description="If true, execution permitted if floors pass",
    )
    abi_version: str = Field(
        default="1.0",
        description="ABI version requested by client",
    )


# =============================================================================
# Error Schemas (Item 8: Standard Error Taxonomy)
# =============================================================================


class CanonicalErrorDetail(BaseModel):
    """Standard error detail structure."""

    code: str = Field(description="Machine-readable error code (AUTH_*, SESSION_*, ABI_*, etc.)")
    message: str = Field(description="Human-readable error message")
    recoverable: bool = Field(default=True, description="Whether client can retry/recover")
    remediation: str | None = Field(default=None, description="Suggested fix or next action")
    required_next_tool: str | None = Field(default=None, description="Tool to call to resolve")


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    ok: bool = Field(default=False)
    errors: list[CanonicalErrorDetail]
    abi_version: str = Field(default="1.0")

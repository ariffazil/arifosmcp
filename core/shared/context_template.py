"""Canonical full-context template contract for arifOS MCP orchestration."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ContextFieldSpec(BaseModel):
    """Field contract for required inputs."""

    type: str
    required: bool
    description: str


class OutputContract(BaseModel):
    """Stable output fields for constitutional responses."""

    verdict: str = "SEAL|PARTIAL|SABAR|VOID|888_HOLD"
    confidence: str = "number"
    receipts: str = "object"
    next_action: str = "string"


class FailureContract(BaseModel):
    """Remediation rules when hard floors fail."""

    on_f2: str = "Return VOID with missing-evidence remediation."
    on_f11: str = "Return VOID with auth/session remediation."
    on_f12: str = "Return VOID and isolate request context."


class FullContextTemplate(BaseModel):
    """Constitutional full-context template exposed as an MCP resource."""

    template_id: str = "arifos.full_context.v1"
    schema_version: str = "1.0.0"
    intent: str = "constitutional_tool_orchestration"
    stage_spine: list[str] = Field(
        default_factory=lambda: [
            "000",
            "111",
            "222",
            "333",
            "444",
            "555",
            "666",
            "777",
            "888",
            "999",
        ]
    )
    floors_required: list[str] = Field(
        default_factory=lambda: [
            "F1",
            "F2",
            "F3",
            "F4",
            "F5",
            "F6",
            "F7",
            "F8",
            "F9",
            "F10",
            "F11",
            "F12",
            "F13",
        ]
    )
    required_inputs: dict[str, ContextFieldSpec] = Field(
        default_factory=lambda: {
            "query": ContextFieldSpec(
                type="string",
                required=True,
                description="Primary user objective to process through constitutional pipeline.",
            ),
            "actor_id": ContextFieldSpec(
                type="string",
                required=True,
                description="Authenticated actor identifier used by F11 authority checks.",
            ),
            "session_id": ContextFieldSpec(
                type="string|null",
                required=False,
                description="Session continuity token from init_session/anchor.",
            ),
            "auth_token": ContextFieldSpec(
                type="string|null",
                required=False,
                description="Optional authority token for strict environments.",
            ),
        }
    )
    output_contract: OutputContract = Field(default_factory=OutputContract)
    failure_contract: FailureContract = Field(default_factory=FailureContract)


def build_full_context_template() -> dict[str, Any]:
    """Return serialized full-context template for MCP resource exposure."""

    return FullContextTemplate().model_dump()


__all__ = ["FullContextTemplate", "build_full_context_template"]

"""
A2A Protocol Models
===================

Pydantic models for Google's A2A protocol specification.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class TaskState(str, Enum):
    """A2A Task lifecycle states."""
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input_required"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class AgentCapability(BaseModel):
    """Capability advertised by an agent."""
    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    required_auth: list[str] = Field(default_factory=list)


class AgentSkill(BaseModel):
    """Skill exposed by an agent (A2A v1.0)."""
    id: str
    name: str
    description: str
    tags: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)
    input_modes: list[str] = Field(default_factory=lambda: ["text"])
    output_modes: list[str] = Field(default_factory=lambda: ["text"])


class AgentCard(BaseModel):
    """
    Agent Card - Core of A2A discovery.
    
    Published at /.well-known/agent.json
    """
    name: str = "arifOS Constitutional Kernel"
    description: str = "AI governance system with 13 constitutional floors (F1-F13). Provides constitutional review, task execution, and multi-agent coordination with thermodynamic governance."
    url: str = "https://arifosmcp.arif-fazil.com"
    version: str = "2026.03.14-VALIDATED"
    
    # Authentication
    authentication: dict[str, Any] = Field(default_factory=lambda: {
        "schemes": ["none", "api_key"],
        "credentials": None
    })
    
    # Capabilities
    capabilities: dict[str, Any] = Field(default_factory=lambda: {
        "streaming": True,
        "pushNotifications": False,
        "stateTransitionHistory": True,
    })
    
    # Skills (what this agent can do)
    skills: list[AgentSkill] = Field(default_factory=lambda: [
        AgentSkill(
            id="constitutional_review",
            name="Constitutional Review",
            description="Review actions against 13 constitutional floors",
            tags=["governance", "safety", "verification"]
        ),
        AgentSkill(
            id="task_execution",
            name="Governed Task Execution",
            description="Execute tasks with full constitutional oversight",
            tags=["execution", "governance"]
        ),
        AgentSkill(
            id="vault_seal",
            name="Immutable Sealing",
            description="Cryptographically seal decisions to VAULT999",
            tags=["audit", "compliance", "crypto"]
        ),
        AgentSkill(
            id="multi_agent_coordination",
            name="Multi-Agent Coordination",
            description="Coordinate with other agents via A2A",
            tags=["coordination", "a2a", "diplomacy"]
        ),
    ])
    
    # A2A Endpoints
    endpoints: dict[str, str] = Field(default_factory=lambda: {
        "task": "/a2a/task",
        "status": "/a2a/status",
        "cancel": "/a2a/cancel",
        "subscribe": "/a2a/subscribe",
    })
    
    # Constitutional metadata
    constitutional_floors: int = 13
    motto: str = "Ditempa Bukan Diberi — Forged, Not Given"
    trinity: str = "ΔΩΨ"


class TaskMessage(BaseModel):
    """Message within a task."""
    role: Literal["system", "user", "agent"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Artifact(BaseModel):
    """Output artifact from task execution."""
    name: str
    content_type: str  # text/plain, application/json, etc.
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class Task(BaseModel):
    """
    A2A Task - Central to A2A protocol.
    
    Tasks have lifecycle: submitted → working → [completed|failed|cancelled]
    """
    id: str
    state: TaskState = TaskState.SUBMITTED
    
    # Agent info
    client_agent_id: str = Field(..., description="Agent that submitted task")
    remote_agent_id: str = "arifos-kernel"
    
    # Task content
    session_id: str | None = None
    messages: list[TaskMessage] = Field(default_factory=list)
    
    # Execution
    skill_id: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    
    # Results
    artifacts: list[Artifact] = Field(default_factory=list)
    error_message: str | None = None
    
    # Constitutional governance
    verdict: str | None = None  # SEAL, VOID, HOLD, SABAR
    floors_checked: list[str] = Field(default_factory=list)
    violations: list[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    
    # Status callback (optional)
    status_callback_url: str | None = None


class TaskStatusUpdate(BaseModel):
    """Status update for SSE streaming."""
    task_id: str
    state: TaskState
    message: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SubmitTaskRequest(BaseModel):
    """Request to submit a new task."""
    client_agent_id: str
    skill_id: str | None = None
    session_id: str | None = None
    messages: list[TaskMessage] = Field(default_factory=list)
    parameters: dict[str, Any] = Field(default_factory=dict)
    status_callback_url: str | None = None


class GetTaskResponse(BaseModel):
    """Response for getting task status."""
    task: Task


class CancelTaskResponse(BaseModel):
    """Response for cancelling a task."""
    success: bool
    message: str
    task: Task | None = None


class A2AError(BaseModel):
    """A2A Error response."""
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)

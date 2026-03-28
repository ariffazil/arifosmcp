"""
core/state/agent_registry.py — Agent Metadata & Lifecycle Tracker

Tracks active agent 'processes' within the arifOS kernel.
Provides the registry for the scheduler and recovery systems.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AgentStatus(Enum):
    READY = "ready"
    RUNNING = "running"
    SUSPENDED = "suspended"
    QUARANTINED = "quarantined"
    TERMINATED = "terminated"


@dataclass
class AgentProcess:
    """A descriptor for an active intelligence unit."""

    pid: str
    owner_session: str
    role: str
    status: AgentStatus = AgentStatus.READY
    priority: int = 5
    created_at: datetime = field(default_factory=datetime.now)
    violation_count: int = 0
    metadata: dict = field(default_factory=dict)


class AgentRegistry:
    """
    The 'Process Table' of the arifOS kernel.
    Enables cross-agent observability and enforcement.
    """

    def __init__(self):
        self._agents: dict[str, AgentProcess] = {}

    def register(self, pid: str, session_id: str, role: str, priority: int = 5) -> AgentProcess:
        """Register a new agent in the kernel table."""
        agent = AgentProcess(pid=pid, owner_session=session_id, role=role, priority=priority)
        self._agents[pid] = agent
        return agent

    def update_status(self, pid: str, status: AgentStatus):
        if pid in self._agents:
            self._agents[pid].status = status

    def get_agent(self, pid: str) -> AgentProcess | None:
        return self._agents.get(pid)

    def list_by_session(self, session_id: str) -> list[AgentProcess]:
        return [a for a in self._agents.values() if a.owner_session == session_id]

    def record_violation(self, pid: str):
        """P0: Increment violation count for threshold-based quarantine."""
        if pid in self._agents:
            self._agents[pid].violation_count += 1


# Global singleton
agent_registry = AgentRegistry()

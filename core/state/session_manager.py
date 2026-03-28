"""
core/state/session_manager.py — Constitutional Session Authority

Manages the lifecycle of GovernanceKernel instances (Ψ), ensuring isolation
and resource sovereignty across multiple concurrent intelligence sessions.
"""

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime

from arifosmcp.core.governance_kernel import GovernanceKernel
from arifosmcp.core.shared.types import ActorIdentity


@dataclass
class SessionMetadata:
    """Active session telemetry and constraints."""

    session_id: str
    owner: str
    actor_identity: ActorIdentity | None = None
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    kernel: GovernanceKernel = field(init=False)


class SessionManager:
    """
    The Central State Authority for arifOS.
    Governs session ignition, isolation, and termination.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._sessions = {}
            return cls._instance

    def create_session(
        self,
        owner: str,
        actor_identity: ActorIdentity | None = None,
        session_id: str | None = None,
    ) -> str:
        """
        Ignite a new governance session.
        F11: Establishes a unique authority boundary.
        """
        if not session_id:
            session_id = str(uuid.uuid4())

        metadata = SessionMetadata(
            session_id=session_id, owner=owner, actor_identity=actor_identity
        )

        # Initialize the Kernel for this session
        kernel = GovernanceKernel(decision_owner=owner, session_id=session_id)
        metadata.kernel = kernel

        self._sessions[session_id] = metadata
        return session_id

    def get_session(self, session_id: str) -> SessionMetadata | None:
        """Retrieve the full session metadata for a specific session."""
        metadata = self._sessions.get(session_id)
        if metadata:
            metadata.last_activity = datetime.now()
            return metadata
        return None

    def get_kernel(self, session_id: str) -> GovernanceKernel | None:
        """Retrieve the Ψ state for a specific session."""
        metadata = self._sessions.get(session_id)
        if metadata:
            metadata.last_activity = datetime.now()
            return metadata.kernel
        return None

    def get_identity(self, session_id: str) -> ActorIdentity | None:
        """Retrieve the ActorIdentity for a specific session."""
        metadata = self._sessions.get(session_id)
        return metadata.actor_identity if metadata else None

    def terminate_session(self, session_id: str):
        """Standard termination. Vault persistence should happen before this."""
        if session_id in self._sessions:
            del self._sessions[session_id]

    def list_active_sessions(self) -> dict[str, str]:
        """Returns a map of session_id to owner."""
        return {sid: meta.owner for sid, meta in self._sessions.items()}


# Global singleton
session_manager = SessionManager()

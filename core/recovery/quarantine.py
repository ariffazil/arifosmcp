"""
core/recovery/quarantine.py — Agent Isolation & Cooling

Integrates with AgentRegistry to isolate agents that breach
critical constitutional floors (F2, F5, F11).
"""

import logging

from arifosmcp.core.state.agent_registry import AgentStatus, agent_registry

logger = logging.getLogger(__name__)

# P0: Violation thresholds-based recovery
VIOLATION_QUARANTINE_THRESHOLD = 3


class QuarantineManager:
    """
    Active Enforcement & Recovery.
    Protects the kernel from repeated constitutional violations.
    """

    def __init__(self):
        self._quarantined_agents: list[str] = []

    def check_and_isolate(self, pid: str) -> bool:
        """
        Evaluate if an agent should be quarantined.
        F5: Maintains system stability by cooling 'heated' agents.
        """
        agent = agent_registry.get_agent(pid)
        if not agent:
            return False

        if agent.violation_count >= VIOLATION_QUARANTINE_THRESHOLD:
            logger.warning(f"CRITICAL: Agent {pid} reached violation threshold. ISOLATING.")
            agent_registry.update_status(pid, AgentStatus.QUARANTINED)
            if pid not in self._quarantined_agents:
                self._quarantined_agents.append(pid)
            return True
        return False

    def release_from_quarantine(self, pid: str, manual_override: bool = False):
        """
        Release agent if cooled or if 888 Judge manually intervenes.
        """
        if manual_override and pid in self._quarantined_agents:
            agent_registry.update_status(pid, AgentStatus.READY)
            self._quarantined_agents.remove(pid)
            logger.info(f"Agent {pid} released from quarantine by manual override.")


# Global singleton
quarantine_manager = QuarantineManager()

"""
AgentZero Escalation Module

Sovereign safety mechanisms:
- 888_HOLD state management
- F13 human approval workflows
- Escalation pathways
"""

from .hold_state import HoldStateManager, EscalationPathway

__all__ = ["HoldStateManager", "EscalationPathway"]

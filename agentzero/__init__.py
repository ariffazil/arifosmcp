"""
arifOS AgentZero Integration Module

Sovereign-grade autonomous engine with constitutional governance.
Version: 2026.03.13-MVP
Author: Muhammad Arif bin Fazil [ΔΩΨ | ARIF]

This module implements the 5-Class Agent Parliament under arifOS v35O:
- ValidatorAgent (Ψ - APEX): Final judge, verdict issuer
- OrchestratorAgent (Δ - MIND): Task decomposition
- EngineerAgent (Ω - HEART): Code execution with F11 gating
- AuditorAgent (Ω - HEART): Compliance review
- ArchitectAgent (Δ - MIND): Strategy design

MVP Scope: ValidatorAgent + EngineerAgent + PromptArmor
"""

__version__ = "2026.03.13-MVP"
__author__ = "Muhammad Arif bin Fazil [ΔΩΨ | ARIF]"

from .agents.base import ConstitutionalAgent, TrinityRole, Verdict
from .agents.validator import ValidatorAgent
from .agents.engineer import EngineerAgent
from .security.prompt_armor import PromptArmor
from .escalation.hold_state import HoldStateManager

__all__ = [
    "ConstitutionalAgent",
    "TrinityRole", 
    "Verdict",
    "ValidatorAgent",
    "EngineerAgent",
    "PromptArmor",
    "HoldStateManager",
]

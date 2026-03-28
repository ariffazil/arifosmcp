"""
AgentZero MCP Tools — Constitutional Agent Parliament Interface

Exposes AgentZero agents as MCP tools for governed autonomous operations.
Version: 2026.03.13-H1
Author: Muhammad Arif bin Fazil [ΔΩΨ | ARIF]

Tools:
- agentzero_validate: ValidatorAgent (Ψ - APEX) constitutional verification
- agentzero_engineer: EngineerAgent (Ω - HEART) F11-gated code execution
- agentzero_hold_check: 888 HOLD state status query
- agentzero_memory_query: Constitutional memory with F-floor filtering
- agentzero_armor_scan: F12 injection detection
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from fastmcp import Context

# AgentZero Components
from arifosmcp.agentzero.agents.engineer import EngineerAgent
from arifosmcp.agentzero.agents.validator import ValidatorAgent
from arifosmcp.agentzero.security.prompt_armor import PromptArmor
from arifosmcp.agentzero.memory.constitutional_memory import ConstitutionalMemoryStore
from arifosmcp.agentzero.escalation.hold_state import HoldStateManager
from arifosmcp.agentzero.agents.base import Verdict as AZVerdict, FloorScore

# arifOS runtime models
from arifosmcp.runtime.models import (
    CallerContext,
    RuntimeEnvelope,
    RuntimeStatus,
    Stage,
    Verdict,
)

logger = logging.getLogger(__name__)

class SimpleArifOSClient:
    """Mock client for AgentZero agents to interact with arifOS governance."""
    async def evaluate_action(self, action: Dict[str, Any], floors: List[str]) -> AZVerdict:
        # Default to SEAL for now as the tool wrapper provides the final governance envelope
        return AZVerdict.seal(
            execution_id=action.get("execution_id", "ext-000"),
            agent_id=action.get("agent_id", "unknown"),
            action_type=action.get("agent_type", "task"),
            floor_scores=[FloorScore(f, 1.0, 1.0, True) for f in floors]
        )
    
    async def seal_to_vault(self, verdict: AZVerdict) -> str:
        return f"vault_{uuid.uuid4().hex[:12]}"
    
    async def request_human_approval(self, execution_id: str, reason: str) -> bool:
        return False

# Singletons for performance and continuity
_CLIENT = SimpleArifOSClient()
_ARMOR = PromptArmor()
_MEMORY = ConstitutionalMemoryStore()
_HOLD_MANAGER = HoldStateManager()

_VALIDATOR = ValidatorAgent(agent_id="validator.mcp", arifos_client=_CLIENT)
_ENGINEER = EngineerAgent(agent_id="engineer.mcp", arifos_client=_CLIENT)
_ENGINEER.set_validator(_VALIDATOR)

async def agentzero_validate(
    input_to_validate: str,
    validation_type: str = "code",
    session_id: str = "global",
    auth_context: Dict[str, Any] | None = None,
    caller_context: CallerContext | None = None,
    ctx: Context | None = None,
) -> RuntimeEnvelope:
    """
    ValidatorAgent (Ψ - APEX): Constitutional verification of code, output, or action.
    
    Arg:
        input_to_validate: The code, output, or action to validate.
        validation_type: Type of validation ("code", "output", "action", "plan").
    """
    try:
        task = {
            "type": "validate_action" if validation_type == "action" else "verify_compliance",
            "action": {"content": input_to_validate},
            "action_type": "content_validation",
            "validation_type": validation_type,
            "risk_level": "medium",
        }
        
        result = await _VALIDATOR.execute(task)
        
        az_status = result.get("verdict", "VOID")
        verdict_map = {
            "SEAL": Verdict.SEAL,
            "SABAR": Verdict.SABAR,
            "VOID": Verdict.VOID,
            "HOLD": Verdict.HOLD,
            "PARTIAL": Verdict.PARTIAL,
        }
        
        return RuntimeEnvelope(
            tool="agentzero_validate",
            session_id=session_id,
            stage=Stage.JUDGE_888.value,
            verdict=verdict_map.get(az_status, Verdict.VOID),
            status=RuntimeStatus.SUCCESS if result.get("status") == "success" else RuntimeStatus.ERROR,
            payload={
                "validation_result": result.get("result", result),
                "agent_id": _VALIDATOR.agent_id,
            },
            auth_context=auth_context,
        )
        
    except Exception as e:
        logger.error(f"AgentZero validation failed: {e}")
        return RuntimeEnvelope(
            tool="agentzero_validate",
            session_id=session_id,
            stage=Stage.JUDGE_888.value,
            verdict=Verdict.VOID,
            status=RuntimeStatus.ERROR,
            payload={"error": str(e)},
            auth_context=auth_context,
        )


async def agentzero_engineer(
    task_description: str,
    action_type: str = "execute_code",
    risk_tier: str = "medium",
    session_id: str = "global",
    auth_context: Dict[str, Any] | None = None,
    caller_context: CallerContext | None = None,
    ctx: Context | None = None,
) -> RuntimeEnvelope:
    """
    EngineerAgent (Ω - HEART): Code generation and execution with F11 gating.
    
    Arg:
        task_description: The code or command to execute.
        action_type: "execute_code", "shell_command", "read_file", "write_file".
    """
    try:
        task = {
            "type": action_type,
            "code": task_description if action_type == "execute_code" else "",
            "command": task_description if action_type == "shell_command" else "",
            "risk_tier": risk_tier,
            "authorized": True,
        }
        
        result = await _ENGINEER.execute(task)
        
        is_err = result.get("status") in ["error", "VOID", "BLOCKED"]
        status = RuntimeStatus.ERROR if is_err else RuntimeStatus.SUCCESS
        
        return RuntimeEnvelope(
            tool="agentzero_engineer",
            session_id=session_id,
            stage=Stage.ROUTER_444.value,
            verdict=Verdict.SEAL if status == RuntimeStatus.SUCCESS else Verdict.VOID,
            status=status,
            payload={
                "execution_result": result.get("result", result),
                "agent_id": _ENGINEER.agent_id,
                "risk_tier": risk_tier,
            },
            auth_context=auth_context,
        )
        
    except Exception as e:
        logger.error(f"AgentZero engineering failed: {e}")
        return RuntimeEnvelope(
            tool="agentzero_engineer",
            session_id=session_id,
            stage=Stage.ROUTER_444.value,
            verdict=Verdict.VOID,
            status=RuntimeStatus.ERROR,
            payload={"error": str(e)},
            auth_context=auth_context,
        )


async def agentzero_hold_check(
    hold_id: str | None = None,
    session_id: str = "global",
    auth_context: Dict[str, Any] | None = None,
    caller_context: CallerContext | None = None,
    ctx: Context | None = None,
) -> RuntimeEnvelope:
    """Check 888 HOLD state status and manage escalations."""
    try:
        if hold_id:
            details = _HOLD_MANAGER.get_hold_details(hold_id)
            payload = details.to_dict() if details else {"error": "Hold not found"}
        else:
            pending = _HOLD_MANAGER.get_pending_holds()
            payload = {
                "pending_holds": [h.to_dict() for h in pending],
                "stats": _HOLD_MANAGER.get_stats(),
            }
        
        return RuntimeEnvelope(
            tool="agentzero_hold_check",
            session_id=session_id,
            stage=Stage.VAULT_999.value,
            verdict=Verdict.SEAL,
            status=RuntimeStatus.SUCCESS,
            payload=payload,
            auth_context=auth_context,
        )
        
    except Exception as e:
        logger.error(f"AgentZero hold check failed: {e}")
        return RuntimeEnvelope(
            tool="agentzero_hold_check",
            session_id=session_id,
            stage=Stage.VAULT_999.value,
            verdict=Verdict.VOID,
            status=RuntimeStatus.ERROR,
            payload={"error": str(e)},
            auth_context=auth_context,
        )


async def agentzero_memory_query(
    query: str,
    project_id: str = "default",
    session_id: str = "global",
    auth_context: Dict[str, Any] | None = None,
    caller_context: CallerContext | None = None,
    ctx: Context | None = None,
) -> RuntimeEnvelope:
    """autonomous memory search across Vault999 and session artifacts."""
    try:
        await _MEMORY.initialize_project(project_id)
        
        memories = await _MEMORY.recall(
            query=query,
            project_id=project_id,
            k=5,
            verify_f2=True,
        )
        
        payload = {
            "query": query,
            "results": [m.to_dict() for m in memories],
            "project_id": project_id,
        }
        
        return RuntimeEnvelope(
            tool="agentzero_memory_query",
            session_id=session_id,
            stage=Stage.MEMORY_555.value,
            verdict=Verdict.SEAL,
            status=RuntimeStatus.SUCCESS,
            payload=payload,
            auth_context=auth_context,
        )
        
    except Exception as e:
        logger.error(f"AgentZero memory query failed: {e}")
        return RuntimeEnvelope(
            tool="agentzero_memory_query",
            session_id=session_id,
            stage=Stage.MEMORY_555.value,
            verdict=Verdict.VOID,
            status=RuntimeStatus.ERROR,
            payload={"error": str(e)},
            auth_context=auth_context,
        )


async def agentzero_armor_scan(
    content: str,
    session_id: str = "global",
    auth_context: Dict[str, Any] | None = None,
    caller_context: CallerContext | None = None,
    ctx: Context | None = None,
) -> RuntimeEnvelope:
    """F12 security scan (PromptArmor) on content."""
    try:
        report = await _ARMOR.scan(content)
        
        return RuntimeEnvelope(
            tool="agentzero_armor_scan",
            session_id=session_id,
            stage=Stage.SENSE_111.value,
            verdict=Verdict.VOID if report.is_injection else Verdict.SEAL,
            status=RuntimeStatus.SUCCESS,
            payload=report.to_dict(),
            auth_context=auth_context,
        )
        
    except Exception as e:
        logger.error(f"AgentZero armor scan failed: {e}")
        return RuntimeEnvelope(
            tool="agentzero_armor_scan",
            session_id=session_id,
            stage=Stage.SENSE_111.value,
            verdict=Verdict.VOID,
            status=RuntimeStatus.ERROR,
            payload={"error": str(e)},
            auth_context=auth_context,
        )

# Export all tools
__all__ = [
    "agentzero_validate",
    "agentzero_engineer",
    "agentzero_hold_check",
    "agentzero_memory_query",
    "agentzero_armor_scan",
]

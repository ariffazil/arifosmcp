"""
ConstitutionalAgent Base Class

All AgentZero agents inherit from this base class, which provides:
- arifOS constitutional enforcement hooks
- VAULT999 audit logging
- Trinity role assignment
- Verdict handling
- F11 authorization gating
"""

from __future__ import annotations

import hashlib
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Protocol
from uuid import uuid4


logger = logging.getLogger(__name__)


class TrinityRole(Enum):
    """Trinity Architecture roles (ΔΩΨ)."""
    DELTA = auto()    # Δ - AGI Mind (Reasoning, Clarity)
    OMEGA = auto()    # Ω - ASI Heart (Humility, Empathy)
    PSI = auto()      # Ψ - APEX Soul (Vitality, Sovereignty)


class VerdictStatus(Enum):
    """Constitutional verdict statuses."""
    SEAL = auto()      # ✅ Full approval, execute and log
    SABAR = auto()     # ⚠️ Partial approval, proceed with caution
    VOID = auto()      # ❌ Rejected, do not execute
    HOLD = auto()      # ⏸️ Paused, awaiting human approval (888_HOLD)
    PARTIAL = auto()   # ◐ Partial execution, some components blocked


@dataclass
class FloorScore:
    """Score for a single constitutional floor."""
    floor: str          # F1-F13
    score: float        # 0.0-1.0
    threshold: float    # Required threshold
    passed: bool        # Whether floor passed
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class Verdict:
    """
    Constitutional verdict from arifOS evaluation.
    
    This is the core governance mechanism - every agent action
    must receive a verdict before execution.
    """
    status: VerdictStatus
    execution_id: str
    agent_id: str
    action_type: str
    floor_scores: list[FloorScore] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    human_approval_required: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    vault_hash: str | None = None
    
    # For HOLD state
    hold_reason: str | None = None
    escalation_path: str | None = None
    
    @classmethod
    def seal(cls, execution_id: str, agent_id: str, action_type: str,
             floor_scores: list[FloorScore]) -> Verdict:
        """Create a SEAL verdict (full approval)."""
        return cls(
            status=VerdictStatus.SEAL,
            execution_id=execution_id,
            agent_id=agent_id,
            action_type=action_type,
            floor_scores=floor_scores
        )
    
    @classmethod
    def void(cls, execution_id: str, agent_id: str, action_type: str,
             violations: list[str], floor_scores: list[FloorScore]) -> Verdict:
        """Create a VOID verdict (rejected)."""
        return cls(
            status=VerdictStatus.VOID,
            execution_id=execution_id,
            agent_id=agent_id,
            action_type=action_type,
            floor_scores=floor_scores,
            violations=violations
        )
    
    @classmethod
    def hold(cls, execution_id: str, agent_id: str, action_type: str,
             hold_reason: str, escalation_path: str,
             floor_scores: list[FloorScore]) -> Verdict:
        """Create a HOLD verdict (888_HOLD escalation)."""
        return cls(
            status=VerdictStatus.HOLD,
            execution_id=execution_id,
            agent_id=agent_id,
            action_type=action_type,
            floor_scores=floor_scores,
            human_approval_required=True,
            hold_reason=hold_reason,
            escalation_path=escalation_path
        )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert verdict to dictionary for VAULT999 logging."""
        return {
            "status": self.status.name,
            "execution_id": self.execution_id,
            "agent_id": self.agent_id,
            "action_type": self.action_type,
            "floor_scores": [
                {
                    "floor": fs.floor,
                    "score": fs.score,
                    "threshold": fs.threshold,
                    "passed": fs.passed,
                    "details": fs.details
                }
                for fs in self.floor_scores
            ],
            "violations": self.violations,
            "recommendations": self.recommendations,
            "human_approval_required": self.human_approval_required,
            "timestamp": self.timestamp.isoformat(),
            "vault_hash": self.vault_hash,
            "hold_reason": self.hold_reason,
            "escalation_path": self.escalation_path
        }
    
    def compute_hash(self) -> str:
        """Compute SHA-256 hash for VAULT999 chain."""
        data = json.dumps(self.to_dict(), sort_keys=True, default=str)
        return hashlib.sha256(data.encode()).hexdigest()


class ArifOSClient(Protocol):
    """Protocol for arifOS MCP client."""
    
    async def evaluate_action(self, action: dict[str, Any], 
                              floors: list[str]) -> Verdict:
        """Evaluate action against constitutional floors."""
        ...
    
    async def seal_to_vault(self, verdict: Verdict) -> str:
        """Seal verdict to VAULT999, return chain hash."""
        ...
    
    async def request_human_approval(self, execution_id: str,
                                     reason: str) -> bool:
        """Request F13 human approval for HOLD state."""
        ...


class ConstitutionalAgent(ABC):
    """
    Base class for all AgentZero agents with constitutional governance.
    
    Every agent must:
    1. Have a Trinity role (Δ, Ω, or Ψ)
    2. Declare which floors it enforces
    3. Get verdict before executing any action
    4. Log all actions to VAULT999
    5. Support F13 human veto
    """
    
    def __init__(
        self,
        agent_id: str,
        role: TrinityRole,
        enforced_floors: list[str],
        arifos_client: ArifOSClient,
        max_subagent_depth: int = 3,
        parent_agent: str | None = None
    ):
        self.agent_id = agent_id
        self.role = role
        self.enforced_floors = enforced_floors
        self.arifos = arifos_client
        self.max_subagent_depth = max_subagent_depth
        self.parent_agent = parent_agent
        self.current_depth = 0 if parent_agent is None else 1
        
        # Execution tracking
        self.execution_history: list[str] = []
        self.violation_count = 0
        
        logger.info(f"Initialized {self.__class__.__name__}({agent_id}) "
                   f"with role {role.name}, floors {enforced_floors}")
    
    @property
    @abstractmethod
    def agent_type(self) -> str:
        """Return agent type (e.g., 'validator', 'engineer')."""
        pass
    
    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a task with full constitutional governance.
        
        This is the main entry point - it wraps _execute_impl with:
        1. Pre-execution constitutional check
        2. VAULT999 logging
        3. F13 human approval for HOLD states
        4. Post-execution audit
        """
        execution_id = str(uuid4())
        
        # Prepare action for evaluation
        action = {
            "execution_id": execution_id,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "trinity_role": self.role.name,
            "task": task,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"[{execution_id}] {self.agent_id} eval task: {task.get('type', 'unknown')}")
        
        try:
            # === PRE-EXECUTION: Constitutional evaluation ===
            verdict = await self._evaluate_constitutionality(action)
            
            if verdict.status == VerdictStatus.VOID:
                logger.warning(f"[{execution_id}] VOID verdict - blocking execution")
                self.violation_count += 1
                await self._log_to_vault(verdict)
                return {
                    "status": "VOID",
                    "execution_id": execution_id,
                    "violations": verdict.violations,
                    "message": "Action blocked by constitutional governance"
                }
            
            if verdict.status == VerdictStatus.HOLD:
                logger.info(f"[{execution_id}] HOLD verdict - escalating to human")
                await self._log_to_vault(verdict)
                return await self._handle_hold_state(verdict, action)
            
            # === EXECUTION: Proceed with governance ===
            logger.info(f"[{execution_id}] {verdict.status.name} verdict - proceeding")
            
            result = await self._execute_impl(task, execution_id, verdict)
            
            # === POST-EXECUTION: Audit and seal ===
            verdict.vault_hash = verdict.compute_hash()
            vault_entry = await self._log_to_vault(verdict, result)
            
            self.execution_history.append(execution_id)
            
            return {
                "status": "success",
                "execution_id": execution_id,
                "result": result,
                "verdict": verdict.status.name,
                "vault_entry": vault_entry
            }
            
        except Exception as e:
            logger.error(f"[{execution_id}] Execution failed: {e}")
            raise ConstitutionalExecutionError(f"Agent execution failed: {e}") from e
    
    async def _evaluate_constitutionality(self, action: dict[str, Any]) -> Verdict:
        """
        Evaluate action against constitutional floors.
        
        This calls the arifOS MCP API to get a verdict.
        """
        # In real implementation, this calls arifOS
        # For now, we simulate the evaluation
        return await self.arifos.evaluate_action(action, self.enforced_floors)
    
    async def _log_to_vault(self, verdict: Verdict, 
                            result: dict | None = None) -> str:
        """Log execution to VAULT999 immutable ledger."""
        return await self.arifos.seal_to_vault(verdict)
    
    async def _handle_hold_state(self, verdict: Verdict, 
                                 action: dict[str, Any]) -> dict[str, Any]:
        """
        Handle 888_HOLD escalation.
        
        This implements the F13 human sovereignty pathway.
        """
        logger.info(f"[{verdict.execution_id}] Requesting human approval")
        
        approved = await self.arifos.request_human_approval(
            verdict.execution_id,
            verdict.hold_reason or "High-risk action requires F13 approval"
        )
        
        if approved:
            logger.info(f"[{verdict.execution_id}] Human approved - proceeding")
            # Re-evaluate with approval flag
            action["f13_approved"] = True
            new_verdict = await self._evaluate_constitutionality(action)
            
            if new_verdict.status != VerdictStatus.VOID:
                result = await self._execute_impl(action["task"], 
                                                  verdict.execution_id, 
                                                  new_verdict)
                return {
                    "status": "success",
                    "execution_id": verdict.execution_id,
                    "result": result,
                    "verdict": new_verdict.status.name,
                    "f13_approved": True
                }
        
        logger.info(f"[{verdict.execution_id}] Human denied or timeout")
        return {
            "status": "DENIED",
            "execution_id": verdict.execution_id,
            "message": "F13 human sovereignty exercised - action blocked"
        }
    
    @abstractmethod
    async def _execute_impl(self, task: dict[str, Any], 
                           execution_id: str,
                           verdict: Verdict) -> dict[str, Any]:
        """
        Actual agent implementation.
        
        Subclasses override this to implement specific agent logic.
        The constitutional enforcement is already handled by execute().
        """
        pass
    
    def can_spawn_subagent(self) -> bool:
        """Check if agent can spawn subagents (depth limit)."""
        return self.current_depth < self.max_subagent_depth
    
    async def spawn_subagent(self, task: dict[str, Any],
                           agent_class: type) -> dict[str, Any]:
        """
        Spawn a subagent with inherited constitutional constraints.
        
        All subagents inherit:
        - Parent's enforced floors
        - Parent's arifOS client
        - Depth tracking
        - Accountability chain
        """
        if not self.can_spawn_subagent():
            raise ConstitutionalViolation(
                f"Max subagent depth {self.max_subagent_depth} reached"
            )
        
        subagent_id = f"{self.agent_id}.sub.{uuid4().hex[:8]}"
        
        # Create subagent with inherited constraints
        subagent = agent_class(
            agent_id=subagent_id,
            role=self.role,  # Inherit role
            enforced_floors=self.enforced_floors,
            arifos_client=self.arifos,
            max_subagent_depth=self.max_subagent_depth,
            parent_agent=self.agent_id
        )
        subagent.current_depth = self.current_depth + 1
        
        logger.info(f"[{self.agent_id}] Spawned subagent {subagent_id} "
                   f"at depth {subagent.current_depth}")
        
        # Execute task in subagent
        return await subagent.execute(task)


class ConstitutionalExecutionError(Exception):
    """Error during constitutional agent execution."""
    pass


class ConstitutionalViolation(Exception):
    """Raised when constitutional constraints are violated."""
    pass

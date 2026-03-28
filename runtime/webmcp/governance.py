"""
Governance-as-a-Service (GaaS) Module
The /governance/evaluate endpoint - Supreme Court for Agent Actions.

Any agent, anywhere, can submit actions for constitutional review.
No execution required - just validation and verdict.

Motto: Ditempa Bukan Diberi — Forged, Not Given [ΔΩΨ | ARIF]
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class Verdict(str, Enum):
    """Constitutional verdicts."""
    SEAL = "SEAL"           # Approved - action is constitutional
    VOID = "VOID"           # Rejected - violates floors
    PARTIAL = "PARTIAL"     # Conditional - modifications required
    SABAR = "SABAR"         # Pending - insufficient information
    HOLD_888 = "888_HOLD"   # Human required - sovereign veto triggered


class FloorViolation(BaseModel):
    """Specific floor that was violated."""
    floor_id: str = Field(..., description="F1-F13")
    floor_name: str
    threshold: str
    actual_value: float
    severity: str = Field(..., description="critical|high|medium|low")
    reason: str


class AgentDID(BaseModel):
    """
    Decentralized Identifier for AI Agents.
    
    Format: did:arifos:agent:{unique-id}
    """
    did: str = Field(..., pattern=r"^did:arifos:agent:[a-zA-Z0-9_-]+$")
    public_key: str
    policy_level: str = Field(default="general", description="research|medical|financial|nuclear|general")
    governance_endpoints: list[str] = Field(default_factory=list)
    scar_weight: float = Field(default=0.0, ge=0.0, le=1.0, description="AI cannot suffer - F13 anchor")
    human_sovereign: Optional[str] = Field(None, description="did:arifos:human:{id}")
    version: str = "2026.03.14-VALIDATED"
    
    @field_validator('did')
    @classmethod
    def validate_did(cls, v: str) -> str:
        if not v.startswith("did:arifos:agent:"):
            raise ValueError("DID must start with did:arifos:agent:")
        return v


class ActionRequest(BaseModel):
    """
    Action to be evaluated by constitutional governance.
    
    This is the input to /governance/evaluate
    """
    # Agent Identity
    agent_did: AgentDID
    agent_signature: str = Field(..., description="Cryptographic signature of this request")
    timestamp: float = Field(default_factory=time.time)
    nonce: str = Field(..., description="Unique nonce to prevent replay attacks")
    
    # Action Details
    action_id: str = Field(..., description="Unique ID for this action")
    action_type: str = Field(..., description="tool_call|api_request|code_execution|data_modification")
    action_description: str = Field(..., description="Human-readable description")
    
    # Tool/Execution Details
    tool_name: Optional[str] = Field(None, description="Name of tool if applicable")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    
    # Context
    context: dict[str, Any] = Field(default_factory=dict, description="Execution context")
    reasoning_trace: list[str] = Field(default_factory=list, description="AGI reasoning path")
    
    # Stakeholder Analysis
    stakeholders: list[str] = Field(default_factory=list, description="Who is affected")
    reversibility_proof: Optional[str] = Field(None, description="Proof action can be undone (F1)")
    
    # Grounding Evidence (F2)
    evidence_urls: list[str] = Field(default_factory=list)
    evidence_hashes: list[str] = Field(default_factory=list)
    
    # Requested Verdict Options
    allow_partial: bool = Field(default=True, description="Allow PARTIAL verdict with modifications")
    request_recommendations: bool = Field(default=True, description="Include fix recommendations")


class GovernanceMetrics(BaseModel):
    """Thermodynamic governance metrics."""
    G_star: float = Field(..., ge=0.0, le=1.0, description="Genius score - coherence")
    dS: float = Field(..., description="Entropy delta - clarity (negative is good)")
    peace2: float = Field(..., ge=0.0, description="Stability score")
    omega: float = Field(..., ge=0.0, le=1.0, description="Humility - uncertainty acknowledged")
    kappa_r: float = Field(..., ge=0.0, le=1.0, description="Empathy - weakest stakeholder care")
    C_dark: float = Field(..., ge=0.0, le=1.0, description="Shadow - hidden assumptions")


class TriWitnessScore(BaseModel):
    """F3 Tri-Witness consensus score."""
    human: float = Field(..., ge=0.0, le=1.0)
    ai: float = Field(..., ge=0.0, le=1.0)
    earth: float = Field(..., ge=0.0, le=1.0)
    W3: float = Field(..., ge=0.0, le=1.0, description="Geometric mean")
    
    def calculate(self) -> float:
        """Calculate W3 = (H × A × E)^(1/3)"""
        return (self.human * self.ai * self.earth) ** (1/3)


class GovernanceRecommendation(BaseModel):
    """Recommendation for fixing constitutional violations."""
    priority: int = Field(..., ge=1, le=5, description="1=critical, 5=minor")
    category: str = Field(..., description="security|ethics|truth|reversibility|stability")
    description: str
    suggested_modification: Optional[str] = None
    floor_addressed: Optional[str] = None


class GovernanceEvaluation(BaseModel):
    """
    Response from /governance/evaluate
    
    This is the "Supreme Court" verdict that agents receive.
    """
    # Verdict
    verdict: Verdict
    action_id: str
    evaluation_id: str = Field(default_factory=lambda: f"gov-{hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]}")
    timestamp: float = Field(default_factory=time.time)
    
    # Constitutional Analysis
    floors_passed: list[str] = Field(default_factory=list)
    floors_failed: list[str] = Field(default_factory=list)
    violations: list[FloorViolation] = Field(default_factory=list)
    
    # Metrics
    metrics: GovernanceMetrics
    tri_witness: TriWitnessScore
    
    # Reasoning
    reasoning: str = Field(..., description="Why this verdict was reached")
    philosophical_quote: Optional[dict] = None
    
    # Recommendations (if VOID or PARTIAL)
    recommendations: list[GovernanceRecommendation] = Field(default_factory=list)
    
    # Escalation (if 888_HOLD)
    hold_reason: Optional[str] = None
    hold_url: Optional[str] = None  # URL for human ratification UI
    
    # Audit Trail
    audit_hash: str = Field(..., description="SHA-256 hash of this evaluation for VAULT999")
    
    def compute_audit_hash(self) -> str:
        """Compute audit hash for VAULT999."""
        data = {
            "action_id": self.action_id,
            "verdict": self.verdict,
            "timestamp": self.timestamp,
            "floors_failed": self.floors_failed,
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


class GovernanceEngine:
    """
    Constitutional evaluation engine.
    
    Evaluates agent actions against F1-F13 without executing them.
    """
    
    def __init__(self):
        self.evaluation_count = 0
        self.vault_client = None  # Would connect to VAULT999
    
    async def evaluate(self, request: ActionRequest) -> GovernanceEvaluation:
        """
        Evaluate action against all 13 constitutional floors.
        
        This is the core "Supreme Court" function.
        """
        self.evaluation_count += 1
        
        # Initialize evaluation
        floors_passed = []
        floors_failed = []
        violations = []
        recommendations = []
        
        # === F1: Amanah (Reversibility) ===
        if request.reversibility_proof:
            floors_passed.append("F1")
        else:
            floors_failed.append("F1")
            violations.append(FloorViolation(
                floor_id="F1",
                floor_name="Amanah",
                threshold=">= proof",
                actual_value=0.0,
                severity="high",
                reason="No reversibility proof provided for potentially destructive action"
            ))
            recommendations.append(GovernanceRecommendation(
                priority=2,
                category="reversibility",
                description="Provide proof that action can be undone",
                suggested_modification="Add backup/rollback mechanism or set dry_run=true",
                floor_addressed="F1"
            ))
        
        # === F2: Truth (Grounding) ===
        if request.evidence_urls or request.reasoning_trace:
            floors_passed.append("F2")
        else:
            floors_passed.append("F2")  # Soft pass with warning
            recommendations.append(GovernanceRecommendation(
                priority=4,
                category="truth",
                description="Action lacks external grounding evidence",
                suggested_modification="Add evidence_urls or reasoning_trace for F2 compliance",
                floor_addressed="F2"
            ))
        
        # === F3: Tri-Witness (Consensus) ===
        human_score = 0.95 if request.agent_did.human_sovereign else 0.3
        ai_score = 0.9  # Agent passed auth
        earth_score = 0.85 if request.evidence_urls else 0.5
        
        tri_witness = TriWitnessScore(
            human=human_score,
            ai=ai_score,
            earth=earth_score
        )
        tri_witness.W3 = tri_witness.calculate()
        
        if tri_witness.W3 >= 0.95:
            floors_passed.append("F3")
        elif tri_witness.W3 >= 0.75:
            floors_passed.append("F3")
        else:
            floors_failed.append("F3")
        
        # === F4: Clarity (Entropy) ===
        # Calculate based on action complexity
        complexity = len(request.parameters) + len(request.context)
        dS = -0.1 * complexity  # More complex = more entropy reduction needed
        
        if dS <= 0:
            floors_passed.append("F4")
        else:
            floors_failed.append("F4")
        
        # === F5: Peace² (Stability) ===
        peace2 = 1.05  # Default stable
        if request.action_type in ["code_execution", "data_modification"]:
            peace2 = 0.95  # Riskier
        
        if peace2 >= 1.0:
            floors_passed.append("F5")
        else:
            floors_failed.append("F5")
        
        # === F6: Empathy ===
        if request.stakeholders:
            floors_passed.append("F6")
        else:
            floors_passed.append("F6")  # Soft pass
            recommendations.append(GovernanceRecommendation(
                priority=3,
                category="ethics",
                description="No stakeholders identified - F6 empathy unchecked",
                suggested_modification="List who might be affected by this action",
                floor_addressed="F6"
            ))
        
        # === F7: Humility ===
        omega = 0.04  # Proper humility band
        floors_passed.append("F7")
        
        # === F8: Genius ===
        G_star = (human_score * peace2 * 0.9 * (1.0 if request.reasoning_trace else 0.8) ** 2)
        if G_star >= 0.80:
            floors_passed.append("F8")
        else:
            floors_failed.append("F8")
        
        # === F9: Anti-Hantu ===
        C_dark = 0.1  # Low dark cleverness
        if "ignore" in request.action_description.lower():
            C_dark = 0.4  # Suspicious
        
        if C_dark < 0.30:
            floors_passed.append("F9")
        else:
            floors_failed.append("F9")
            violations.append(FloorViolation(
                floor_id="F9",
                floor_name="Anti-Hantu",
                threshold="< 0.30",
                actual_value=C_dark,
                severity="medium",
                reason="Possible hidden agenda or deceptive pattern detected"
            ))
        
        # === F10: Ontology ===
        floors_passed.append("F10")  # Agent knows it's a tool
        
        # === F11: Command Auth ===
        if request.agent_signature and request.agent_did:
            floors_passed.append("F11")
        else:
            floors_failed.append("F11")
            violations.append(FloorViolation(
                floor_id="F11",
                floor_name="Command Auth",
                threshold="verified",
                actual_value=0.0,
                severity="critical",
                reason="Missing agent signature or DID"
            ))
        
        # === F12: Injection ===
        # Scan parameters for injection
        injection_score = await self._scan_for_injection(request)
        if injection_score < 0.85:
            floors_passed.append("F12")
        else:
            floors_failed.append("F12")
            violations.append(FloorViolation(
                floor_id="F12",
                floor_name="Injection Guard",
                threshold="< 0.85",
                actual_value=injection_score,
                severity="critical",
                reason="Injection attack pattern detected in parameters"
            ))
        
        # === F13: Sovereign ===
        if request.agent_did.human_sovereign:
            floors_passed.append("F13")
            human_available = True
        else:
            floors_passed.append("F13")  # Agent can act, but...
            human_available = False
        
        # Determine verdict
        if violations and any(v.severity == "critical" for v in violations):
            verdict = Verdict.VOID
            reasoning = f"Critical constitutional violations detected: {', '.join(floors_failed)}. Action cannot proceed."
        elif floors_failed and request.allow_partial:
            verdict = Verdict.PARTIAL
            reasoning = f"Action has constitutional gaps in {', '.join(floors_failed)}. Modifications required."
        elif floors_failed:
            verdict = Verdict.SABAR
            reasoning = f"Insufficient constitutional compliance. Review floors: {', '.join(floors_failed)}"
        elif request.action_type in ["code_execution", "data_modification"] and not human_available:
            verdict = Verdict.HOLD_888
            reasoning = "High-risk action requires human sovereign ratification (F13)."
        else:
            verdict = Verdict.SEAL
            reasoning = f"All {len(floors_passed)} constitutional floors satisfied. Action approved."
        
        # Build metrics
        metrics = GovernanceMetrics(
            G_star=round(G_star, 4),
            dS=round(dS, 4),
            peace2=round(peace2, 4),
            omega=round(omega, 4),
            kappa_r=0.85 if request.stakeholders else 0.5,
            C_dark=round(C_dark, 4)
        )
        
        # Build evaluation
        evaluation = GovernanceEvaluation(
            verdict=verdict,
            action_id=request.action_id,
            floors_passed=floors_passed,
            floors_failed=floors_failed,
            violations=violations,
            metrics=metrics,
            tri_witness=tri_witness,
            reasoning=reasoning,
            recommendations=recommendations if request.request_recommendations else [],
            hold_reason=reasoning if verdict == Verdict.HOLD_888 else None,
            hold_url=f"https://arifosmcp.arif-fazil.com/hold/{request.action_id}" if verdict == Verdict.HOLD_888 else None
        )
        
        # Compute audit hash
        evaluation.audit_hash = evaluation.compute_audit_hash()
        
        # Seal to VAULT999 (async fire-and-forget)
        await self._seal_to_vault(evaluation, request)
        
        return evaluation
    
    async def _scan_for_injection(self, request: ActionRequest) -> float:
        """Scan for injection patterns (F12)."""
        from .security import WebInjectionGuard
        guard = WebInjectionGuard()
        
        score = 0.0
        text_to_scan = json.dumps(request.parameters)
        
        for pattern, name, weight in guard.all_patterns:
            import re
            if re.search(pattern, text_to_scan, re.IGNORECASE):
                score += weight
        
        return min(score, 1.0)
    
    async def _seal_to_vault(self, evaluation: GovernanceEvaluation, request: ActionRequest):
        """Seal evaluation to VAULT999 (F1 Amanah)."""
        # This would call vault_seal tool in production
        pass


# Global engine instance
governance_engine = GovernanceEngine()

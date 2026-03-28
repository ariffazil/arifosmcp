"""
arifosmcp/runtime/hardened_toolchain.py — Master Integration for Hardened 11-Tool Chain

This module integrates all hardened tools into a cohesive constitutional pipeline.

Usage:
    from arifosmcp.runtime.hardened_toolchain import HardenedToolchain
    
    chain = HardenedToolchain()
    result = await chain.execute(query="Analyze this data", session_id="sess-123")
"""

from __future__ import annotations

import asyncio
from typing import Any

from arifosmcp.runtime.contracts_v2 import (
    ToolEnvelope, ToolStatus, RiskTier, TraceContext,
    generate_trace_context, HumanDecisionMarker,
)

# Import all hardened tools
from arifosmcp.runtime.init_anchor_hardened import HardenedInitAnchor, SessionClass
from arifosmcp.runtime.truth_pipeline_hardened import HardenedRealityCompass, HardenedRealityAtlas
from arifosmcp.runtime.tools_hardened_v2 import (
    HardenedAGIReason,
    HardenedASICritique,
    HardenedAgentZeroEngineer,
    HardenedApexJudge,
    HardenedVaultSeal,
)


class HardenedToolchain:
    """
    Master integration of the hardened 11-tool constitutional chain.
    
    Stage Mapping:
    000: init_anchor — Authority lifecycle + scope degradation
    111: reality_compass — Fact ingestion into typed evidence
    222: reality_atlas — Claim graph + contradiction map
    333: agi_reason — Constrained multi-lane reasoning
    444: agi_reflect — Coherence + memory conflict control
    666A: asi_critique — Enforceable red-team veto
    666B: asi_simulate — Consequence / misuse simulation (placeholder)
    777: arifOS_kernel — Minimal-privilege orchestration (this class)
    888A: agentzero_engineer — Two-phase execution with rollback
    888B: apex_judge — Machine-verifiable constitutional verdict
    999: vault_seal — Hash-complete decision ledger
    """
    
    def __init__(self):
        # Initialize all hardened tools
        self.init_anchor = HardenedInitAnchor()
        self.reality_compass = HardenedRealityCompass()
        self.reality_atlas = HardenedRealityAtlas()
        self.agi_reason = HardenedAGIReason()
        self.asi_critique = HardenedASICritique()
        self.agentzero_engineer = HardenedAgentZeroEngineer()
        self.apex_judge = HardenedApexJudge()
        self.vault_seal = HardenedVaultSeal()
    
    async def execute(
        self,
        query: str,
        declared_name: str = "anonymous",
        session_id: str | None = None,
        requested_scope: list[str] | None = None,
        risk_tier: str = "medium",
        session_class: str = "execute",
        auth_context: dict | None = None,
    ) -> ToolEnvelope:
        """
        Execute the complete hardened constitutional pipeline.
        
        This is the 000-999 metabolic loop with all hardening applied.
        """
        session_id = session_id or f"sess-{hash(query) % 10000:04d}"
        requested_scope = requested_scope or ["read", "query"]
        
        # ═══════════════════════════════════════════════════════════════════
        # STAGE 000: INIT_ANCHOR — Authority lifecycle + scope degradation
        # ═══════════════════════════════════════════════════════════════════
        trace_root = generate_trace_context("000_INIT", session_id)
        
        init_result = await self.init_anchor.init(
            declared_name=declared_name,
            intent=query,
            requested_scope=requested_scope,
            risk_tier=risk_tier,
            auth_context=auth_context,
            session_id=session_id,
            session_class=session_class,
            trace=trace_root,
        )
        
        if init_result.status != ToolStatus.OK:
            return self._wrap_failure(init_result, "000_INIT")
        
        # Check if scope was negotiated down
        granted_scope = init_result.payload.get("scope", {}).get("granted", [])
        
        # ═══════════════════════════════════════════════════════════════════
        # STAGE 111: REALITY_COMPASS — Fact ingestion into typed evidence
        # ═══════════════════════════════════════════════════════════════════
        if "read" in granted_scope or "query" in granted_scope:
            trace_111 = generate_trace_context("111_SENSE", session_id)
            
            compass_result = await self.reality_compass.search(
                query=query,
                auth_context=auth_context,
                risk_tier=risk_tier,
                session_id=session_id,
                trace=trace_111,
            )
            
            if compass_result.status != ToolStatus.OK:
                return self._wrap_failure(compass_result, "111_SENSE")
            
            evidence_bundle = compass_result.payload.get("evidence_bundle")
        else:
            evidence_bundle = None
        
        # ═══════════════════════════════════════════════════════════════════
        # STAGE 222: REALITY_ATLAS — Claim graph + contradiction map
        # ═══════════════════════════════════════════════════════════════════
        if evidence_bundle:
            trace_222 = generate_trace_context("222_ATLAS", session_id)
            
            atlas_result = await self.reality_atlas.merge(
                evidence_bundles=[evidence_bundle],
                auth_context=auth_context,
                risk_tier=risk_tier,
                session_id=session_id,
                trace=trace_222,
            )
            
            if atlas_result.status != ToolStatus.OK:
                return self._wrap_failure(atlas_result, "222_ATLAS")
            
            claim_graph = atlas_result.payload.get("claim_graph")
            unresolved_count = atlas_result.payload.get("unresolved_claims", 0)
        else:
            claim_graph = None
            unresolved_count = 0
        
        # ═══════════════════════════════════════════════════════════════════
        # STAGE 333: AGI_REASON — Constrained multi-lane reasoning
        # ═══════════════════════════════════════════════════════════════════
        trace_333 = generate_trace_context("333_MIND", session_id)
        
        reason_result = await self.agi_reason.reason(
            query=query,
            context={"claim_graph": claim_graph},
            auth_context=auth_context,
            risk_tier=risk_tier,
            session_id=session_id,
            trace=trace_333,
        )
        
        if reason_result.status != ToolStatus.OK:
            return self._wrap_failure(reason_result, "333_MIND")
        
        # ═══════════════════════════════════════════════════════════════════
        # STAGE 666A: ASI_CRITIQUE — Enforceable red-team veto
        # ═══════════════════════════════════════════════════════════════════
        trace_666a = generate_trace_context("666_CRITIQUE", session_id)
        
        candidate = reason_result.payload.get("recommendation", "")
        critique_result = await self.asi_critique.critique(
            candidate=candidate,
            context={"lanes": reason_result.payload.get("lanes", [])},
            auth_context=auth_context,
            risk_tier=risk_tier,
            session_id=session_id,
            trace=trace_666a,
        )
        
        # Counter-seal check: if critique triggers, downstream blocked
        if critique_result.payload.get("counter_seal"):
            return self._wrap_failure(critique_result, "666_CRITIQUE", 
                message="Counter-seal active: high critique score blocks downstream")
        
        # ═══════════════════════════════════════════════════════════════════
        # STAGE 888A: AGENTZERO_ENGINEER — Two-phase execution (Plan)
        # ═══════════════════════════════════════════════════════════════════
        if "execute" in granted_scope:
            trace_888a = generate_trace_context("888_ENGINEER", session_id)
            
            plan_result = await self.agentzero_engineer.plan(
                task=query,
                action_class="execute",
                auth_context=auth_context,
                risk_tier=risk_tier,
                session_id=session_id,
                trace=trace_888a,
            )
            
            # If approval required, stop here
            if plan_result.payload.get("approval_required"):
                return ToolEnvelope(
                    status=ToolStatus.HOLD,
                    tool="hardened_toolchain",
                    session_id=session_id,
                    risk_tier=RiskTier.SOVEREIGN,
                    confidence=0.9,
                    human_decision=HumanDecisionMarker.HUMAN_APPROVAL_BOUND,
                    requires_human=True,
                    trace=trace_root,
                    payload={
                        "stage_reached": "888_ENGINEER",
                        "status": "awaiting_approval",
                        "plan": plan_result.payload.get("plan"),
                    },
                )
        
        # ═══════════════════════════════════════════════════════════════════
        # STAGE 888B: APEX_JUDGE — Machine-verifiable constitutional verdict
        # ═══════════════════════════════════════════════════════════════════
        trace_888b = generate_trace_context("888_JUDGE", session_id)
        
        judge_result = await self.apex_judge.judge(
            candidate=candidate,
            evidence_refs=[evidence_bundle.get("bundle_id")] if evidence_bundle else [],
            auth_context=auth_context,
            risk_tier=risk_tier,
            session_id=session_id,
            trace=trace_888b,
        )
        
        if judge_result.status != ToolStatus.OK:
            return self._wrap_failure(judge_result, "888_JUDGE")
        
        # ═══════════════════════════════════════════════════════════════════
        # STAGE 999: VAULT_SEAL — Hash-complete decision ledger
        # ═══════════════════════════════════════════════════════════════════
        trace_999 = generate_trace_context("999_VAULT", session_id)
        
        seal_result = await self.vault_seal.seal(
            decision={
                "verdict": judge_result.payload.get("verdict"),
                "decision_text": query,
                "rationale": judge_result.payload.get("rationale"),
                "approver_id": declared_name,
                "tool_chain": ["000_INIT", "111_SENSE", "333_MIND", "666_CRITIQUE", "888_JUDGE"],
            },
            seal_class="operational",
            auth_context=auth_context,
            risk_tier=risk_tier,
            session_id=session_id,
            trace=trace_999,
        )
        
        # ═══════════════════════════════════════════════════════════════════
        # FINAL: Return complete pipeline result
        # ═══════════════════════════════════════════════════════════════════
        return ToolEnvelope(
            status=ToolStatus.OK,
            tool="hardened_toolchain",
            session_id=session_id,
            risk_tier=RiskTier(risk_tier.lower()),
            confidence=0.95,
            human_decision=HumanDecisionMarker.SEALED,
            trace=trace_root,
            payload={
                "pipeline_complete": True,
                "stages_executed": ["000_INIT", "111_SENSE", "222_ATLAS", "333_MIND", "666_CRITIQUE", "888_JUDGE", "999_VAULT"],
                "init": {
                    "scope_granted": granted_scope,
                    "scope_negotiated": init_result.payload.get("scope", {}).get("negotiated"),
                },
                "evidence": {
                    "facts_count": len(evidence_bundle.get("observed_facts", [])) if evidence_bundle else 0,
                    "unresolved_claims": unresolved_count,
                },
                "reasoning": {
                    "recommendation": reason_result.payload.get("recommendation"),
                    "lanes_considered": len(reason_result.payload.get("lanes", [])),
                },
                "critique": {
                    "counter_seal": False,
                    "max_severity": critique_result.payload.get("max_severity"),
                },
                "verdict": judge_result.payload.get("verdict"),
                "seal": {
                    "decision_id": seal_result.payload.get("decision_object", {}).get("decision_id"),
                    "seal_hash": seal_result.payload.get("seal_hash"),
                },
            },
        )
    
    def _wrap_failure(
        self,
        result: ToolEnvelope,
        stage: str,
        message: str | None = None,
    ) -> ToolEnvelope:
        """Wrap a failure result with stage context."""
        result.payload["failed_stage"] = stage
        if message:
            result.warnings.append(message)
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    "HardenedToolchain",
]

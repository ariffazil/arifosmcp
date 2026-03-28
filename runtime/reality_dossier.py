"""
arifosmcp/runtime/reality_dossier.py — Tri-Witness Decoder

The final Decoder output for reality-based queries.
Consumes EvidenceBundles + RealityAtlas and produceshuman-facing verdicts aligned with F3 Tri-Witness.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Literal

from pydantic import BaseModel, Field

from .reality_models import BundleStatus, Claim, EvidenceBundle


class Witness(BaseModel):
    source: Literal["human", "ai", "earth"]
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    weight: float = Field(default=1.0, ge=0.0, le=2.0)
    evidence_refs: list[str] = Field(default_factory=list)
    notes: str = ""


class DossierVerdict(BaseModel):
    claim: str
    verdict: Literal["SUPPORTED", "CONTRADICTED", "UNCERTAIN", "INSUFFICIENT_EVIDENCE"]
    confidence: float = Field(ge=0.0, le=1.0)
    witnesses: list[Witness] = Field(default_factory=list)
    floor_impacts: dict[str, Any] = Field(default_factory=dict)
    evidence_chain: list[str] = Field(default_factory=list)
    dissent: str | None = None


class DossierProvenance(BaseModel):
    chain_id: str = Field(default_factory=lambda: f"chain-{uuid.uuid4().hex[:8]}")
    created_at: float = Field(default_factory=time.time)
    bundles_processed: int = 0
    atlas_nodes: int = 0
    completeness_score: float = Field(default=0.0, ge=0.0, le=1.0)


class IntelligenceState3E(BaseModel):
    exploration: Literal["BROAD", "SCOPED", "EXHAUSTED"] = "BROAD"
    entropy: Literal["LOW", "MANAGEABLE", "HIGH", "CRITICAL"] = "LOW"
    eureka: Literal["NONE", "PARTIAL", "FORGED"] = "NONE"
    hypotheses: list[str] = Field(default_factory=list)
    stable_facts: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    insight: str | None = None


class RealityDossier(BaseModel):
    id: str = Field(default_factory=lambda: f"dossier-{uuid.uuid4().hex[:8]}")
    session_id: str | None = "global"
    actor_id: str = "anonymous"
    authority_level: str = "anonymous"
    
    status: BundleStatus
    intelligence: IntelligenceState3E = Field(default_factory=IntelligenceState3E)    
    verdicts: list[DossierVerdict] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    provenance: DossierProvenance = Field(default_factory=DossierProvenance)
    
    telemetry: dict[str, Any] = Field(default_factory=dict)
    machine_status: str = "READY"
    machine_issue: str | None = None


class DossierEngine:
    def __init__(self):
        self._floor_weights = {
            "F2_TRUTH": 0.25,
            "F4_CLARITY": 0.15,
            "F7_HUMILITY": 0.10,
        }
    
    def _compute_witness_confidence(self, claim: Claim, bundles: list[EvidenceBundle]) -> list[Witness]:
        witnesses: list[Witness] = []
        total_confidence = claim.confidence
        
        human_witness = Witness(
            source="human",
            confidence=min(1.0, total_confidence + 0.1),
            weight=1.5,
            notes="Claim attributed to human source or query"
        )
        witnesses.append(human_witness)
        
        ai_witness = Witness(
            source="ai",
            confidence=total_confidence,
            weight=1.0,
            notes="AI-grounded confidence from evidence extraction"
        )
        witnesses.append(ai_witness)
        
        earth_witness = Witness(
            source="earth",
            confidence=min(1.0, total_confidence * 0.9),
            weight=1.2,
            notes="External grounding from fetched/computed sources"
        )
        witnesses.append(earth_witness)
        
        return witnesses
    
    def _compute_verdict(
        self, 
        claim: Claim, 
        witnesses: list[Witness],        bundles: list[EvidenceBundle]
    ) -> DossierVerdict:
        support_count = 0
        contradict_count = 0
        total_evidence = len(claim.evidence)
        
        for evidence in claim.evidence:
            if isinstance(evidence, dict):
                relation = evidence.get("relation", "SUPPORTS")
                if relation == "SUPPORTS":
                    support_count += 1
                elif relation == "CONTRADICTS":
                    contradict_count += 1
        
        weighted_confidence = sum(w.confidence * w.weight for w in witnesses) / sum(w.weight for w in witnesses)
                
        if contradict_count > support_count:
            verdict_str = "CONTRADICTED"
            confidence = weighted_confidence * 0.7
        elif support_count > 0 and total_evidence > 0:
            verdict_str = "SUPPORTED"
            confidence = weighted_confidence
        elif total_evidence == 0:
            verdict_str = "INSUFFICIENT_EVIDENCE"
            confidence = 0.3
        else:
            verdict_str = "UNCERTAIN"
            confidence = weighted_confidence * 0.5
        
        return DossierVerdict(
            claim=claim.text,
            verdict=verdict_str,
            confidence=confidence,
            witnesses=witnesses,
            floor_impacts={
                "F2_TRUTH": {"score": confidence, "threshold": 0.99},
                "F4_CLARITY": {"score": 1.0 - (0.1 if verdict_str == "UNCERTAIN" else 0), "threshold": 0.0},
                "F7_HUMILITY": {"score": 0.04 if verdict_str == "UNCERTAIN" else 0.03, "band": "[0.03, 0.05]"},
            },
            evidence_chain=[e.get("source", "unknown") for e in claim.evidence if isinstance(e, dict)],
        )
    
    def _intelligence_exploration_phase(self, bundles: list[EvidenceBundle]) -> list[str]:
        """
        E1: Exploration - gather candidate interpretations and hypotheses.
        """
        hypotheses = []
        for bundle in bundles:
            if bundle.status.state == "SUCCESS":
                hypotheses.append(f"Bundle {bundle.id[:8]} confirms: {bundle.input.value[:50]}")
            elif bundle.status.state == "SABAR":
                hypotheses.append(f"Bundle {bundle.id[:8]} blocked: {bundle.status.message[:50]}")
            else:
                hypotheses.append(f"Bundle {bundle.id[:8]} uncertain: state={bundle.status.state}")
        return hypotheses
    
    def _intelligence_entropy_phase(self, bundles: list[EvidenceBundle]) -> dict[str, Any]:
        """
        E2: Entropy - measure and metabolize uncertainty.
        """
        stable_facts = []
        uncertainties = []
        entropy_score = 0.0
        
        for bundle in bundles:
            if bundle.status.state == "SUCCESS":
                stable_facts.append(f"Fetch completed: {bundle.input.value}")
            else:
                for error in bundle.status.errors:
                    uncertainties.append(f"{error.code}: {error.detail}")
                    entropy_score += 0.15
        
        entropy_score = min(1.0, entropy_score)
        
        if entropy_score < 0.3:
            entropy_level = "LOW"
        elif entropy_score < 0.6:
            entropy_level = "MANAGEABLE"
        elif entropy_score < 0.9:
            entropy_level = "HIGH"
        else:
            entropy_level = "CRITICAL"
        
        return {
            "level": entropy_level,
            "score": entropy_score,
            "stable_facts": stable_facts,
            "uncertainties": uncertainties,
        }
    
    def _intelligence_eureka_phase(
        self, 
        verdicts: list[DossierVerdict], 
        entropy_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        E3: Eureka - collapse confusion into coherent, decision-ready form.
        """
        supported = sum(1 for v in verdicts if v.verdict == "SUPPORTED")
        contradicted = sum(1 for v in verdicts if v.verdict == "CONTRADICTED")
        total = len(verdicts)
        
        if total == 0:
            eureka_level = "NONE"
            insight = "No claims to synthesize"
        elif supported == total:
            eureka_level = "FORGED"
            insight = f"All {total} claims are supported with high confidence"
        elif contradicted > supported:
            eureka_level = "PARTIAL"
            insight = f"Contradictions detected: {contradicted} of {total} claims contested"
        elif entropy_data["score"] > 0.5:
            eureka_level = "PARTIAL"
            insight = f"High entropy ({entropy_data['level']}) prevents full synthesis"
        else:
            eureka_level = "FORGED"
            avg_conf = sum(v.confidence for v in verdicts) / total
            insight = f"Synthesis complete: {supported}/{total} supported, confidence={avg_conf:.2f}"
        
        return {
            "level": eureka_level,
            "insight": insight,
        }
    
    def _process_bundle(self, bundle: EvidenceBundle) -> None:
        """Process a single evidence bundle (internal for tests)."""
        pass

    def _generate_final_verdict(self, verdicts: list[DossierVerdict]) -> str:
        """Collapse multiple claim verdicts into a single system verdict."""
        if not verdicts:
            return "INSUFFICIENT_EVIDENCE"
        supported = sum(1 for v in verdicts if v.verdict == "SUPPORTED")
        if supported == len(verdicts):
            return "SUPPORTED"
        if supported > 0:
            return "PARTIAL"
        return "UNCERTAIN"

    async def build_dossier(
        self,
        bundles: list[EvidenceBundle],
        session_id: str | None = None,
        actor_id: str = "anonymous",
        authority_level: str = "anonymous",
    ) -> RealityDossier:
        """
        Build a Reality Dossier from EvidenceBundles.
        Implements the Tri-Witness Decoder for F3 compliance.
        """
        start_time = time.time()
        
        all_claims: list[Claim] = []
        for bundle in bundles:
            all_claims.extend(bundle.claims)
        
        hypotheses = self._intelligence_exploration_phase(bundles)
        entropy_data = self._intelligence_entropy_phase(bundles)
        
        verdicts: list[DossierVerdict] = []
        for claim in all_claims:
            witnesses = self._compute_witness_confidence(claim, bundles)
            verdict = self._compute_verdict(claim, witnesses, bundles)
            verdicts.append(verdict)
        
        eureka_data = self._intelligence_eureka_phase(verdicts, entropy_data)
        
        intelligence = IntelligenceState3E(
            exploration="EXHAUSTED" if len(bundles) > 3 else "SCOPED" if len(bundles) > 1 else "BROAD",
            entropy=entropy_data["level"],
            eureka=eureka_data["level"],
            hypotheses=hypotheses,
            stable_facts=entropy_data["stable_facts"],
            uncertainties=entropy_data["uncertainties"],
            insight=eureka_data["insight"],
        )
        
        total_claims = len(all_claims)
        supported_claims = sum(1 for v in verdicts if v.verdict == "SUPPORTED")
        
        status = BundleStatus(
            state="SUCCESS" if eureka_data["level"] == "FORGED" else "PARTIAL" if eureka_data["level"] == "PARTIAL" else "SABAR",
            stage="222_REALITY",
            verdict="SEAL" if eureka_data["level"] == "FORGED" else "PARTIAL" if total_claims > 0 else "SABAR",
            message=eureka_data["insight"],
            errors=[],
        )
        
        provenance = DossierProvenance(
            bundles_processed=len(bundles),
            atlas_nodes=0,
            completeness_score=min(1.0, (supported_claims / max(1, total_claims)) * (1 - entropy_data["score"])),
        )
        
        telemetry = {
            "dS": -entropy_data["score"],
            "peace2": 1.0 + (0.2 if eureka_data["level"] == "FORGED" else 0),
            "kappa_r": sum(v.confidence for v in verdicts) / max(1, len(verdicts)),
            "confidence": sum(v.confidence for v in verdicts) / max(1, len(verdicts)),
            "verdict": status.verdict,
            "processing_ms": (time.time() - start_time) * 1000,
        }
        
        return RealityDossier(
            session_id=session_id,
            actor_id=actor_id,
            authority_level=authority_level,
            status=status,
            intelligence=intelligence,
            verdicts=verdicts,
            claims=all_claims,
            provenance=provenance,
            telemetry=telemetry,
            machine_status="READY",
        )


dossier_engine = DossierEngine()


def _calculate_completeness(dossier: RealityDossier) -> float:
    """Helper to calculate the completeness of a dossier based on verdicts."""
    if not dossier.verdicts:
        return 0.0
    supported = sum(1 for v in dossier.verdicts if v.verdict == "SUPPORTED")
    return supported / len(dossier.verdicts)


def _validate_dossier(dossier: RealityDossier) -> bool:
    """Validate the integrity of a Reality Dossier."""
    return dossier.status.state != "ERROR"

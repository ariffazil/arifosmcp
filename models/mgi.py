"""
MGI Envelope Models - Machine -> Governance -> Intelligence

The MGI envelope is the canonical wrapper for all tool outputs in the arifOS system.
Every response flows through three layers:
- Machine: Session continuity, tokens, timestamps
- Governance: Constitutional validation, floor enforcement
- Intelligence: Evidence, reasoning, synthesis
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field, field_validator
import hashlib
import json
import uuid


class TokenType(str, Enum):
    """Types of governance tokens in the Canon-13 regime."""
    ANCHOR = "ANCHOR"          # Session establishment token
    JUDGE = "JUDGE"            # 888 Judge override token
    WITNESS = "WITNESS"        # Tri-Witness attestation token
    KERNEL = "KERNEL"          # 13-Floors execution token
    VAULT = "VAULT"            # Merkle chain verification token


class ContinuityStatus(str, Enum):
    """Session continuity states."""
    FRESH = "FRESH"            # New session
    CONTINUOUS = "CONTINUOUS"  # Ongoing session
    RESUMED = "RESUMED"        # Recovered session
    FRAGMENTED = "FRAGMENTED"  # Potential discontinuity detected


class MachineLayer(BaseModel):
    """
    Machine Layer: Session continuity, token management, timestamps.
    
    The foundation of the MGI envelope. Ensures every operation is anchored
    in time and space with verifiable session continuity.
    """
    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique session identifier (UUIDv4)"
    )
    governance_token: str = Field(
        ...,
        description="Cryptographic token for this operation"
    )
    token_type: TokenType = Field(
        default=TokenType.ANCHOR,
        description="Classification of the governance token"
    )
    timestamp_utc: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp of operation execution"
    )
    continuity_status: ContinuityStatus = Field(
        default=ContinuityStatus.FRESH,
        description="Session continuity state"
    )
    parent_token: Optional[str] = Field(
        default=None,
        description="Reference to parent token in chain"
    )
    merkle_leaf: Optional[str] = Field(
        default=None,
        description="Merkle tree leaf hash for this operation"
    )
    
    def compute_merkle_leaf(self, payload: Dict[str, Any]) -> str:
        """Compute Merkle leaf hash from payload."""
        data = {
            "session_id": self.session_id,
            "token": self.governance_token,
            "timestamp": self.timestamp_utc.isoformat(),
            "payload_hash": hashlib.sha256(
                json.dumps(payload, sort_keys=True, default=str).encode()
            ).hexdigest()
        }
        return hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()


class ConstitutionalArticle(str, Enum):
    """Articles of the Canon-13 Constitution."""
    A1_STEEL = "A1_STEEL"              # Default to transparency
    A2_HOLD = "A2_HOLD"                # Escalate uncertainty
    A3_VOID = "A3_VOID"                # Void on contradiction
    A4_PARTIAL = "A4_PARTIAL"          # Partial truth acknowledgment
    A5_JUDGE = "A5_JUDGE"              # Human-in-the-loop trigger
    A6_TRACE = "A6_TRACE"              # Provenance requirement
    A7_EQUITY = "A7_EQUITY"            # Stakeholder fairness
    A8_MEMORY = "A8_MEMORY"            # Vector persistence
    A9_EPOCH = "A9_EPOCH"              # Temporal anchoring
    A10_ENTROPY = "A10_ENTROPY"        # Uncertainty quantification
    A11_SYNTHESIS = "A11_SYNTHESIS"    # Tri-Witness requirement
    A12_PEACE = "A12_PEACE"            # Stability metric
    A13_G = "A13_G"                    # Efficiency coefficient


class ValidationResult(str, Enum):
    """Constitutional validation outcomes."""
    VALID = "VALID"                    # All articles satisfied
    VIOLATION = "VIOLATION"            # Article violation detected
    WARNING = "WARNING"                # Near-violation condition
    PENDING = "PENDING"                # Validation in progress


class GovernanceLayer(BaseModel):
    """
    Governance Layer: Constitutional validation, floor enforcement.
    
    Ensures all operations comply with the Canon-13 Constitution.
    Tracks active floors, validates articles, enforces regime rules.
    """
    active_floors: List[int] = Field(
        default_factory=list,
        description="Currently active floors (F1-F13)",
        ge=1,
        le=13
    )
    constitutional_articles: List[ConstitutionalArticle] = Field(
        default_factory=lambda: [ConstitutionalArticle.A1_STEEL],
        description="Articles invoked for this operation"
    )
    validation_result: ValidationResult = Field(
        default=ValidationResult.PENDING,
        description="Constitutional validation outcome"
    )
    violations: List[str] = Field(
        default_factory=list,
        description="List of constitutional violations if any"
    )
    judge_override: bool = Field(
        default=False,
        description="Whether 888 Judge override is active"
    )
    hold_state_id: Optional[str] = Field(
        default=None,
        description="Active 888_HOLD state identifier"
    )
    floor_metrics: Dict[str, float] = Field(
        default_factory=dict,
        description="Per-floor execution metrics"
    )
    
    @field_validator('active_floors')
    @classmethod
    def validate_floors(cls, v: List[int]) -> List[int]:
        """Ensure all floor numbers are within valid range."""
        for floor in v:
            if not 1 <= floor <= 13:
                raise ValueError(f"Floor must be between 1-13, got {floor}")
        return v


class EvidenceGrade(str, Enum):
    """Grades of evidence quality."""
    PRIMARY = "PRIMARY"        # Direct observation, authoritative source
    SECONDARY = "SECONDARY"    # Derived, analyzed, or reported
    TERTIARY = "TERTIARY"      # Inferred, modeled, or estimated
    ANECDOTAL = "ANECDOTAL"    # Single source, unverified


class ConfidenceInterval(BaseModel):
    """Statistical confidence interval."""
    lower: float = Field(..., ge=0.0, le=1.0)
    upper: float = Field(..., ge=0.0, le=1.0)
    confidence_level: float = Field(default=0.95, ge=0.0, le=1.0)


class IntelligenceLayer(BaseModel):
    """
    Intelligence Layer: Evidence, reasoning, synthesis.
    
    The cognitive core of the MGI envelope. Contains all evidence,
    reasoning chains, synthesis results, and uncertainty metrics.
    """
    evidence_bundles: List[str] = Field(
        default_factory=list,
        description="References to evidence bundle IDs"
    )
    reasoning_chain: List[str] = Field(
        default_factory=list,
        description="Step-by-step reasoning trace"
    )
    synthesis_hash: Optional[str] = Field(
        default=None,
        description="Hash of synthesis result"
    )
    confidence_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence in result (0-1)"
    )
    confidence_interval: Optional[ConfidenceInterval] = Field(
        default=None,
        description="Statistical confidence interval"
    )
    uncertainty_omega: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Uncertainty coefficient Ω₀ (0=certain, 1=unknown)"
    )
    unstable_assumptions: List[str] = Field(
        default_factory=list,
        description="Assumptions that may affect validity"
    )
    knowledge_gaps: List[str] = Field(
        default_factory=list,
        description="Identified gaps in knowledge"
    )
    evidence_grade: EvidenceGrade = Field(
        default=EvidenceGrade.ANECDOTAL,
        description="Quality grade of evidence"
    )


class MGIEnvelope(BaseModel):
    """
    Complete MGI (Machine -> Governance -> Intelligence) envelope.
    
    This is the canonical wrapper for ALL tool outputs in the arifOS system.
    Every response must include this envelope for full provenance and
    constitutional compliance.
    """
    version: str = Field(
        default="1.0.0",
        description="MGI envelope version"
    )
    machine: MachineLayer = Field(
        ...,
        description="Machine layer: session, tokens, continuity"
    )
    governance: GovernanceLayer = Field(
        ...,
        description="Governance layer: constitution, floors, validation"
    )
    intelligence: IntelligenceLayer = Field(
        ...,
        description="Intelligence layer: evidence, reasoning, synthesis"
    )
    envelope_hash: Optional[str] = Field(
        default=None,
        description="Cryptographic hash of entire envelope"
    )
    
    def compute_hash(self) -> str:
        """Compute cryptographic hash of this envelope."""
        data = self.model_dump(exclude={'envelope_hash'})
        return hashlib.sha256(
            json.dumps(data, sort_keys=True, default=str).encode()
        ).hexdigest()
    
    def seal(self) -> "MGIEnvelope":
        """Seal the envelope by computing and setting its hash."""
        self.envelope_hash = self.compute_hash()
        return self


class MGIBaseResponse(BaseModel):
    """
    Base class for all tool responses in arifOS.
    
    Every tool must return a response that includes the MGI envelope
    and a payload specific to that tool's function.
    """
    envelope: MGIEnvelope = Field(
        ...,
        description="MGI envelope with full provenance"
    )
    status: str = Field(
        default="success",
        description="Operation status"
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if status is not success"
    )
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

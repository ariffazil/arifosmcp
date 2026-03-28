"""
Verdict Enumerations - Seal types, floor states, and thermodynamic budgets.

This module defines the canonical verdict system for the arifOS regime,
including the three primary seals (STEEL, HOLD, VOID) and the 13-floor
state machine.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator


class SealType(str, Enum):
    """
    The three canonical seals of the Canon-13 regime.
    
    Every operation receives one of these seals based on its
    constitutional compliance and confidence metrics.
    """
    STEEL = "STEEL"        # Operation successful, confident, compliant
    HOLD = "HOLD"          # Uncertainty detected, requires escalation
    VOID = "VOID"          # Contradiction or violation, operation invalid
    PARTIAL = "PARTIAL"    # Partial success with acknowledged limitations


class VerdictState(str, Enum):
    """
    Detailed verdict states within the canonical seals.
    """
    # STEEL substates
    STEEL_CERTAIN = "STEEL_CERTAIN"        # High confidence, full compliance
    STEEL_PROBABLE = "STEEL_PROBABLE"      # Good confidence, minor assumptions
    
    # HOLD substates
    HOLD_888 = "HOLD_888"                  # 888 Judge override required
    HOLD_PARTIAL = "HOLD_PARTIAL"          # Partial information
    HOLD_TEMPORAL = "HOLD_TEMPORAL"        # Time-sensitive, needs refresh
    HOLD_SCOPE = "HOLD_SCOPE"              # Scope unclear, needs definition
    
    # VOID substates
    VOID_CONTRADICTION = "VOID_CONTRADICTION"  # Logical contradiction
    VOID_VIOLATION = "VOID_VIOLATION"          # Constitutional violation
    VOID_INSUFFICIENT = "VOID_INSUFFICIENT"    # Insufficient evidence
    VOID_ERROR = "VOID_ERROR"                  # System error (rare)
    
    # PARTIAL substates
    PARTIAL_LIMITED = "PARTIAL_LIMITED"    # Limited scope success
    PARTIAL_ASSUMED = "PARTIAL_ASSUMED"    # Success with key assumptions


class FloorState(str, Enum):
    """
    States for each of the 13 floors in the metabolic loop.
    """
    INACTIVE = "INACTIVE"          # Floor not currently engaged
    ACTIVE = "ACTIVE"              # Floor currently processing
    COMPLETE = "COMPLETE"          # Floor completed successfully
    HOLD = "HOLD"                  # Floor in HOLD state
    ERROR = "ERROR"                # Floor encountered error
    BYPASSED = "BYPASSED"          # Floor bypassed (emergency only)


class FloorName(str, Enum):
    """
    The 13 canonical floors of the arifOS metabolic loop.
    """
    F1_ANCHOR = "F1_ANCHOR"                    # Session anchoring
    F2_QUERY = "F2_QUERY"                      # Query validation
    F3_EXPLORE = "F3_EXPLORE"                  # Evidence exploration
    F4_METABOLIZE = "F4_METABOLIZE"            # Evidence metabolization
    F5_SYNTHESIZE = "F5_SYNTHESIZE"            # Tri-Witness synthesis
    F6_CALCULATE = "F6_CALCULATE"              # Metric calculation
    F7_CONSTITUTE = "F7_CONSTITUTE"            # Constitutional validation
    F8_RATIFY = "F8_RATIFY"                    # Ratification check
    F9_SEAL = "F9_SEAL"                        # Seal assignment
    F10_PERSIST = "F10_PERSIST"                # Vector persistence
    F11_REPORT = "F11_REPORT"                  # Report generation
    F12_MONITOR = "F12_MONITOR"                # Health monitoring
    F13_CLOSE = "F13_CLOSE"                    # Session closure


class ThermodynamicBudget(BaseModel):
    """
    Thermodynamic budget for system operations.
    
    Tracks computational and cognitive resources consumed
    during operations, enforcing limits to prevent runaway.
    """
    max_tokens: int = Field(
        default=100000,
        ge=0,
        description="Maximum token budget"
    )
    used_tokens: int = Field(
        default=0,
        ge=0,
        description="Tokens consumed"
    )
    max_operations: int = Field(
        default=100,
        ge=0,
        description="Maximum operation count"
    )
    used_operations: int = Field(
        default=0,
        ge=0,
        description="Operations performed"
    )
    max_time_seconds: float = Field(
        default=300.0,
        ge=0.0,
        description="Maximum time budget (seconds)"
    )
    used_time_seconds: float = Field(
        default=0.0,
        ge=0.0,
        description="Time consumed (seconds)"
    )
    entropy_limit: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Maximum acceptable entropy"
    )
    current_entropy: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Current system entropy"
    )
    
    @property
    def token_remaining(self) -> int:
        """Remaining token budget."""
        return max(0, self.max_tokens - self.used_tokens)
    
    @property
    def operations_remaining(self) -> int:
        """Remaining operation budget."""
        return max(0, self.max_operations - self.used_operations)
    
    @property
    def time_remaining(self) -> float:
        """Remaining time budget."""
        return max(0.0, self.max_time_seconds - self.used_time_seconds)
    
    @property
    def is_exhausted(self) -> bool:
        """Check if any budget is exhausted."""
        return (
            self.token_remaining <= 0 or
            self.operations_remaining <= 0 or
            self.time_remaining <= 0.0 or
            self.current_entropy > self.entropy_limit
        )
    
    def consume_tokens(self, tokens: int) -> "ThermodynamicBudget":
        """Consume token budget."""
        self.used_tokens += tokens
        return self
    
    def consume_operation(self) -> "ThermodynamicBudget":
        """Consume one operation."""
        self.used_operations += 1
        return self
    
    def consume_time(self, seconds: float) -> "ThermodynamicBudget":
        """Consume time budget."""
        self.used_time_seconds += seconds
        return self
    
    def update_entropy(self, entropy: float) -> "ThermodynamicBudget":
        """Update current entropy."""
        self.current_entropy = entropy
        return self


class FloorMetrics(BaseModel):
    """
    Metrics for a single floor execution.
    """
    floor_number: int = Field(..., ge=1, le=13)
    floor_name: FloorName = Field(...)
    state: FloorState = Field(default=FloorState.INACTIVE)
    entry_time: Optional[str] = Field(default=None)
    exit_time: Optional[str] = Field(default=None)
    duration_ms: Optional[float] = Field(default=None, ge=0)
    tokens_consumed: int = Field(default=0, ge=0)
    sub_operations: int = Field(default=0, ge=0)
    
    @field_validator('floor_number')
    @classmethod
    def validate_floor(cls, v: int) -> int:
        if not 1 <= v <= 13:
            raise ValueError(f"Floor must be 1-13, got {v}")
        return v


class KernelMetrics(BaseModel):
    """
    Complete metrics from 13-floor kernel execution.
    
    Contains the three canonical coefficients:
    - κᵣ (kappa_r): Stakeholder impact coefficient
    - Peace²: Stability/peace metric
    - G: Efficiency/governance coefficient
    """
    floor_metrics: List[FloorMetrics] = Field(default_factory=list)
    
    # Canonical coefficients
    kappa_r: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Stakeholder impact coefficient κᵣ"
    )
    peace_squared: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Stability metric Peace²"
    )
    G_coefficient: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Efficiency coefficient G"
    )
    
    # Derived metrics
    overall_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0
    )
    constitutional_compliance: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0
    )
    
    # Totals
    total_tokens: int = Field(default=0, ge=0)
    total_duration_ms: float = Field(default=0.0, ge=0.0)
    total_sub_operations: int = Field(default=0, ge=0)
    
    def add_floor(self, metrics: FloorMetrics) -> "KernelMetrics":
        """Add floor metrics and update totals."""
        self.floor_metrics.append(metrics)
        self.total_tokens += metrics.tokens_consumed
        self.total_sub_operations += metrics.sub_operations
        if metrics.duration_ms:
            self.total_duration_ms += metrics.duration_ms
        return self
    
    def compute_coefficients(self) -> "KernelMetrics":
        """
        Compute canonical coefficients from floor metrics.
        
        This is a simplified calculation - production would use
        more sophisticated algorithms based on actual data.
        """
        completed_floors = sum(
            1 for f in self.floor_metrics
            if f.state == FloorState.COMPLETE
        )
        
        if self.floor_metrics:
            # κᵣ: Based on floor completion and stakeholder impact
            self.kappa_r = completed_floors / 13.0
            
            # Peace²: Based on compliance and lack of errors
            error_floors = sum(
                1 for f in self.floor_metrics
                if f.state == FloorState.ERROR
            )
            self.peace_squared = 1.0 - (error_floors / 13.0)
            
            # G: Efficiency based on token usage and speed
            efficiency = completed_floors / max(1, len(self.floor_metrics))
            self.G_coefficient = efficiency * self.constitutional_compliance
            
            # Overall confidence
            self.overall_confidence = (
                self.kappa_r * 0.4 +
                self.peace_squared * 0.4 +
                self.G_coefficient * 0.2
            )
        
        return self


class VerdictResult(BaseModel):
    """
    Complete verdict result from kernel execution.
    """
    seal: SealType = Field(default=SealType.STEEL)
    state: VerdictState = Field(default=VerdictState.STEEL_PROBABLE)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    metrics: KernelMetrics = Field(default_factory=KernelMetrics)
    thermodynamic_budget: ThermodynamicBudget = Field(
        default_factory=ThermodynamicBudget
    )
    explanation: str = Field(default="")
    recommendations: List[str] = Field(default_factory=list)
    
    def is_success(self) -> bool:
        """Check if verdict represents successful completion."""
        return self.seal in (SealType.STEEL, SealType.PARTIAL)
    
    def requires_escalation(self) -> bool:
        """Check if verdict requires human escalation."""
        return self.seal == SealType.HOLD or self.state == VerdictState.HOLD_888

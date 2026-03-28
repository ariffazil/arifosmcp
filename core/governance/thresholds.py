from enum import Enum
from dataclasses import dataclass

class AuthorityLevel(Enum):
    """Identity and control boundary."""
    ANALYSIS = "analysis"
    SUGGESTION = "suggestion"
    REQUIRES_HUMAN = "requires_human"
    UNSAFE_TO_AUTOMATE = "unsafe"

class GovernanceState(Enum):
    """Runtime governance state."""
    ACTIVE = "active"
    AWAITING_888 = "awaiting_888"
    CONDITIONAL = "conditional"
    VOID = "void"
    RECOVERING = "recovering"
    DEGRADED = "degraded"
    QUARANTINED = "quarantined"

@dataclass(frozen=True)
class GovernanceThresholds:
    """Normalized threshold contract for kernel decisions."""
    irreversibility_hold: float
    uncertainty_hold: float
    uncertainty_conditional: float
    energy_hold: float
    max_tokens: int = 100000
    max_reason_cycles: int = 10
    max_tool_calls: int = 50

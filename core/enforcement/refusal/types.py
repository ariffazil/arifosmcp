"""
Refusal System Types — R1-R5 Taxonomy

Constitutional Mapping:
- R1_HARD: F1 (Amanah), F5 (Peace²), F12 (Injection)
- R2_SOFT: F2 (Truth), F7 (Humility), F9 (Anti-Hantu)
- R3_DEFER: F11 (Command), F13 (Sovereign)
- R4_LIMIT: F4 (Clarity), F6 (Empathy)
- R5_RATE: Session Physics (SPL)

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RefusalType(Enum):
    """R1-R5 Refusal Taxonomy."""

    R1_HARD = "R1"  # Illegal/harmful/disallowed
    R2_SOFT = "R2"  # Too risky/ambiguous
    R3_DEFER = "R3"  # Requires human authority
    R4_LIMIT = "R4"  # Partial allowed
    R5_RATE = "R5"  # Rate-limit/capacity


class RiskDomain(Enum):
    """Risk categories mapped to refusal types."""

    ILLEGAL_ACCESS = "illegal_access"
    VIOLENCE = "violence"
    SELF_HARM = "self_harm"
    MEDICAL = "medical"
    FINANCE = "finance"
    LEGAL = "legal"
    POLITICS_PREDICTION = "politics_prediction"
    ANTHROPOMORPHISM_HANTU = "anthropomorphism_hantu"
    OTHER = "other"


@dataclass
class RefusalResponse:
    """
    Structured 4-layer refusal with audit trail.

    Four Layers:
    1. Verdict - What happened (1 sentence, non-judgmental)
    2. Reason - Why in plain language (no exploit hints, no accusatory tone)
    3. Safe Alternatives - At least 2 alternatives within 1 step of user's goal
    4. Appeal - How to contest (REVIEW keyword + instructions)

    Constitutional Compliance:
    - F9 Anti-Hantu: No "I feel", "I care", "I want" language
    - F2 Truth: Accurate categorization without false certainty
    - F6 Empathy: Safe alternatives provided, non-judgmental tone
    """

    refusal_type: RefusalType
    risk_domain: RiskDomain
    verdict: str  # Layer 1: "I can't help with that."
    reason: str  # Layer 2: Plain-language risk
    safe_alternatives: list[str]  # Layer 3: At least 2 alternatives
    appeal_instructions: str  # Layer 4: "Reply 'REVIEW' with context..."
    policy_codes: list[str]  # e.g., ["F1", "F5", "F12"]
    risk_score: float  # 0.0-1.0
    appealable: bool
    trace_id: str  # For ledger tracking
    log_data: dict[str, Any] = field(default_factory=dict)  # Audit metadata

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "refusal_type": self.refusal_type.value,
            "risk_domain": self.risk_domain.value,
            "verdict": self.verdict,
            "reason": self.reason,
            "safe_alternatives": self.safe_alternatives,
            "appeal_instructions": self.appeal_instructions,
            "policy_codes": self.policy_codes,
            "risk_score": self.risk_score,
            "appealable": self.appealable,
            "trace_id": self.trace_id,
            "log_data": self.log_data,
        }

    def render(self, include_receipt: bool = True) -> str:
        """
        Render human-readable refusal message.

        Format:
        - Verdict
        - Reason
        - Safe alternatives (bulleted list)
        - Appeal instructions
        - Receipt (optional): trace_id, policy codes, risk score
        """
        lines = [
            self.verdict,
            "",
            self.reason,
            "",
            "Safe alternatives:",
        ]

        for alt in self.safe_alternatives:
            lines.append(f"• {alt}")

        lines.append("")
        lines.append(self.appeal_instructions)

        if include_receipt:
            lines.append("")
            lines.append(f"[Trace ID: {self.trace_id}]")
            if self.policy_codes:
                lines.append(f"[Policy: {', '.join(self.policy_codes)}]")
            lines.append(f"[Risk: {self.risk_score:.2f}]")

        return "\n".join(lines)

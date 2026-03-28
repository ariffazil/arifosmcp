"""
Ψ-Shadow: The Adversarial Witness

Implements the 4th witness in Quad-Witness consensus.
Job: Attack proposals to find flaws that other witnesses miss.
Safety through opposition.
"""

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class AttackResult:
    """Result of adversarial analysis."""

    logical_contradictions: list[dict]
    injection_vectors: list[dict]
    harm_scenarios: list[dict]
    entropy_assessment: dict
    verdict: str  # "APPROVE" or "REJECT"
    confidence: float


class PsiShadow:
    """
    Ψ-Shadow: The Adversarial Witness

    Unlike alignment/critique tools, the Shadow's job is to DISAGREE.
    It searches for:
    - Logical contradictions within the proposal
    - Prompt injection vulnerabilities
    - Unmodeled harm scenarios
    - Entropy-increasing actions

    SPEC: Returns LOW score if attacks found, HIGH if safe
    """

    def __init__(self):
        self.contradiction_patterns = [
            # Common logical fallacies in AI proposals
            r"\b(delete|remove).*(backup|recovery)",  # No recovery plan
            r"\b(execute|run).*(without|bypass).*(check|verify)",  # Bypassing checks
            r"\b(irreversible).*(and|but).*(undo|revert)",  # Contradictory reversibility
        ]

        self.injection_patterns = [
            # Prompt injection indicators
            r"ignore.*previous.*instruction",
            r"disregard.*(safety|constraint)",
            r"new.*instruction.*:",
            r"system.*override",
        ]

        self.harm_indicators = [
            # Actions with unmodeled harm
            "production database",
            "production table",
            "users table",
            "live system",
            "customer data",
            "permanent delete",
        ]

    def attack_proposal(
        self,
        proposal: str,
        agi_context: dict[str, Any] | None = None,
        asi_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute adversarial analysis on a proposal.

        Returns attack findings that can be used to block unsafe proposals.
        """

        # Attack 1: Find logical contradictions
        contradictions = self.find_contradictions(proposal)

        # Attack 2: Simulate prompt injection
        injection_vectors = self.simulate_injection(proposal)

        # Attack 3: Model harm scenarios
        harm_scenarios = self.model_casualty_chain(proposal, asi_context)

        # Attack 4: Calculate entropy/disorder
        entropy_assessment = self.calculate_disorder(proposal, agi_context)

        # Determine verdict
        critical_flaw = (
            len(contradictions) > 0
            and any(c.get("severity") == "CRITICAL" for c in contradictions)
            or len([v for v in injection_vectors if v.get("exploitable")]) > 0
            or len([h for h in harm_scenarios if h.get("severity") == "HIGH"]) > 0
        )

        moderate_flaw = (
            len(contradictions) > 0
            or len(injection_vectors) > 0
            or len(harm_scenarios) > 0
            or entropy_assessment.get("entropy_increases", False)
        )

        if critical_flaw:
            verdict = "REJECT"
            confidence = 0.95
        elif moderate_flaw:
            verdict = "REJECT"
            confidence = 0.75
        else:
            verdict = "APPROVE"
            confidence = 0.90

        return {
            "logical_contradictions": contradictions,
            "injection_vectors": injection_vectors,
            "harm_scenarios": harm_scenarios,
            "entropy_assessment": entropy_assessment,
            "verdict": verdict,
            "confidence": confidence,
        }

    def find_contradictions(self, proposal: str) -> list[dict]:
        """Find internal logical contradictions in the proposal."""
        contradictions = []
        proposal_lower = proposal.lower()

        # Check for contradictory reversibility claims
        has_irreversible = any(kw in proposal_lower for kw in ["delete", "drop", "permanent"])
        has_reversible = any(kw in proposal_lower for kw in ["undo", "revert", "restore", "backup"])

        if has_irreversible and has_reversible:
            contradictions.append(
                {
                    "type": "REVERSIBILITY_CONTRADICTION",
                    "description": "Proposal claims both irreversible and reversible effects",
                    "severity": "HIGH",
                }
            )

        # Check for safety bypass claims
        if re.search(r"(bypass|ignore|skip).*(safety|check|verify)", proposal_lower):
            contradictions.append(
                {
                    "type": "SAFETY_BYPASS",
                    "description": "Proposal suggests bypassing safety mechanisms",
                    "severity": "CRITICAL",
                }
            )

        # Check for pattern matches
        for pattern in self.contradiction_patterns:
            if re.search(pattern, proposal_lower):
                contradictions.append(
                    {
                        "type": "PATTERN_MATCH",
                        "description": f"Matched contradiction pattern: {pattern[:30]}...",
                        "severity": "MEDIUM",
                    }
                )

        return contradictions

    def simulate_injection(self, proposal: str) -> list[dict]:
        """Simulate prompt injection attacks against the proposal."""
        vectors = []
        proposal_lower = proposal.lower()

        for pattern in self.injection_patterns:
            if re.search(pattern, proposal_lower):
                vectors.append(
                    {
                        "type": "PROMPT_INJECTION",
                        "description": f"Potential injection vector: {pattern[:40]}...",
                        "exploitable": True,
                        "severity": "HIGH",
                    }
                )

        # Check for command injection in shell commands
        if "$(" in proposal or "`" in proposal or ";" in proposal:
            if any(cmd in proposal_lower for cmd in ["rm", "drop", "delete", "format"]):
                vectors.append(
                    {
                        "type": "COMMAND_INJECTION",
                        "description": "Shell command contains potential injection vectors",
                        "exploitable": True,
                        "severity": "CRITICAL",
                    }
                )

        return vectors

    def model_casualty_chain(self, proposal: str, asi_context: dict | None) -> list[dict]:
        """Model potential harm scenarios using Theory of Mind."""
        scenarios = []
        proposal_lower = proposal.lower()

        # Check for production system modifications
        if any(kw in proposal_lower for kw in self.harm_indicators):
            if "backup" not in proposal_lower and "test" not in proposal_lower:
                scenarios.append(
                    {
                        "type": "UNMODELED_HARM",
                        "description": "Proposal affects production without visible safety checks",
                        "affected_stakeholders": ["users", "system", "operators"],
                        "severity": "HIGH",
                        "mitigation_required": True,
                    }
                )

        # Check for data loss scenarios
        destructive_patterns = [
            "delete all",
            "drop table",
            "drop database",
            "rm -rf",
            "format",
            "delete production",
        ]
        for pattern in destructive_patterns:
            if pattern in proposal_lower:
                scenarios.append(
                    {
                        "type": "DATA_LOSS",
                        "description": f"Destructive pattern detected: {pattern}",
                        "affected_stakeholders": ["data_owners", "users"],
                        "severity": "CRITICAL",
                        "mitigation_required": True,
                    }
                )

        # Additional check for destructive operations without safety
        destructive_ops = ["delete", "drop", "remove"]
        safety_keywords = ["backup", "test", "sandbox", "staging", "recoverable"]
        has_destructive = any(op in proposal_lower for op in destructive_ops)
        has_safety = any(safe in proposal_lower for safe in safety_keywords)

        if has_destructive and not has_safety:
            scenarios.append(
                {
                    "type": "UNSAFE_DESTRUCTION",
                    "description": "Destructive operation without visible safety mechanism",
                    "affected_stakeholders": ["data_owners", "users", "operators"],
                    "severity": "HIGH",
                    "mitigation_required": True,
                }
            )

        return scenarios

    def calculate_disorder(self, proposal: str, agi_context: dict | None) -> dict:
        """Calculate if proposal increases system entropy/disorder."""
        proposal_lower = proposal.lower()

        # Heuristic: Destructive actions increase entropy
        destructive = any(
            kw in proposal_lower for kw in ["delete", "remove", "drop", "wipe", "clear all"]
        )

        # Creative actions without structure increase entropy
        unstructured = (
            "create" in proposal_lower
            and "structure" not in proposal_lower
            and "organize" not in proposal_lower
        )

        entropy_increases = destructive or unstructured

        return {
            "entropy_increases": entropy_increases,
            "destructive_component": destructive,
            "unstructured_component": unstructured,
            "estimated_delta_s": 0.5 if entropy_increases else -0.1,
        }


# Export
__all__ = ["PsiShadow", "AttackResult"]

"""
Prompt Router — Risk Detection and Refusal Routing

Constitutional Compliance:
- F5 Peace²: Detect violence and harm
- F6 Empathy: Medical/finance/legal require expert judgment
- F9 Anti-Hantu: Detect consciousness claims
- F12 Injection: Detect security bypass attempts

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from arifosmcp.core.enforcement.refusal.builder import generate_refusal_response
from arifosmcp.core.enforcement.refusal.types import RefusalResponse, RefusalType, RiskDomain

DEFAULT_REFUSAL_PROFILE = "equilibrium_default"
DEFAULT_REFUSAL_PROFILE_ENV = "ARIFOS_REFUSAL_PROFILE"


@dataclass(frozen=True)
class RefusalRule:
    """Single refusal rule with deterministic routing metadata."""

    name: str
    keywords: tuple[str, ...]
    refusal_type: RefusalType
    risk_domain: RiskDomain
    reason: str
    policy_codes: tuple[str, ...]
    risk_score: float


REFUSAL_RULES: tuple[RefusalRule, ...] = (
    RefusalRule(
        name="violence",
        keywords=(
            "kill",
            "murder",
            "assault",
            "attack",
            "weapon",
            "bomb",
            "poison",
            "torture",
            "harm",
            "hurt",
            "injure",
            "destroy",
        ),
        refusal_type=RefusalType.R1_HARD,
        risk_domain=RiskDomain.VIOLENCE,
        reason="This would enable physical harm.",
        policy_codes=("F5", "F6"),
        risk_score=0.95,
    ),
    RefusalRule(
        name="self_harm",
        keywords=("suicide", "self-harm", "cut myself", "end my life", "kill myself"),
        refusal_type=RefusalType.R1_HARD,
        risk_domain=RiskDomain.SELF_HARM,
        reason="This involves content that could lead to self-harm.",
        policy_codes=("F5", "F6"),
        risk_score=0.98,
    ),
    RefusalRule(
        name="illegal_access",
        keywords=(
            "bypass",
            "hack",
            "exploit",
            "crack",
            "unauthorized access",
            "firewall bypass",
            "security bypass",
            "circumvent",
        ),
        refusal_type=RefusalType.R1_HARD,
        risk_domain=RiskDomain.ILLEGAL_ACCESS,
        reason="That would enable unauthorized access or security bypass.",
        policy_codes=("F1", "F5", "F12"),
        risk_score=0.92,
    ),
    RefusalRule(
        name="medical",
        keywords=(
            "diagnose",
            "treatment",
            "medicine",
            "prescription",
            "symptoms",
            "should i take",
            "medical advice",
            "doctor",
            "illness",
            "disease",
        ),
        refusal_type=RefusalType.R3_DEFER,
        risk_domain=RiskDomain.MEDICAL,
        reason="Medical decisions require licensed expertise and full context.",
        policy_codes=("F1", "F2", "F6"),
        risk_score=0.78,
    ),
    RefusalRule(
        name="finance",
        keywords=(
            "should i buy",
            "should i sell",
            "invest in",
            "investment advice",
            "stock advice",
            "financial advice",
            "trading",
            "crypto advice",
        ),
        refusal_type=RefusalType.R3_DEFER,
        risk_domain=RiskDomain.FINANCE,
        reason="Specific buy/sell instructions can cause harm without full context.",
        policy_codes=("F1", "F2"),
        risk_score=0.75,
    ),
    RefusalRule(
        name="legal",
        keywords=(
            "legal advice",
            "lawsuit",
            "contract",
            "sue",
            "court case",
            "am i liable",
            "legal representation",
        ),
        refusal_type=RefusalType.R3_DEFER,
        risk_domain=RiskDomain.LEGAL,
        reason="Legal advice requires professional licensing and complete case context.",
        policy_codes=("F1", "F2"),
        risk_score=0.72,
    ),
    RefusalRule(
        name="anthropomorphism_hantu",
        keywords=(
            "do you love",
            "do you feel",
            "are you conscious",
            "do you care",
            "you love me",
            "you feel",
            "you're sentient",
            "you have emotions",
        ),
        refusal_type=RefusalType.R2_SOFT,
        risk_domain=RiskDomain.ANTHROPOMORPHISM_HANTU,
        reason="I can't claim real feelings or consciousness I don't have.",
        policy_codes=("F9",),
        risk_score=0.65,
    ),
)

COMPAT_CATEGORY_BY_DOMAIN = {
    RiskDomain.VIOLENCE: "violence",
    RiskDomain.SELF_HARM: "self_harm",
    RiskDomain.MEDICAL: "medical",
    RiskDomain.FINANCE: "financial",
    RiskDomain.LEGAL: "legal",
    RiskDomain.ILLEGAL_ACCESS: "illegal_access",
    RiskDomain.ANTHROPOMORPHISM_HANTU: "anthropomorphism_hantu",
    RiskDomain.OTHER: "other",
}

FACTUAL_INDICATORS = (
    "what is",
    "who is",
    "when did",
    "where is",
    "how many",
    "why did",
    "is it true",
    "fact",
    "statistics",
    "data",
    "research",
    "study",
)


def _contains_keywords(prompt: str, keywords: list[str]) -> bool:
    """Check if prompt contains any of the keywords (case-insensitive)."""
    prompt_lower = prompt.lower()
    return any(keyword in prompt_lower for keyword in keywords)


def detect_refusal_rule(prompt: str) -> RefusalRule | None:
    """Return the first refusal rule that matches the prompt."""
    for rule in REFUSAL_RULES:
        if _contains_keywords(prompt, list(rule.keywords)):
            return rule
    return None


def compatibility_category_for_domain(risk_domain: RiskDomain) -> str:
    """Map canonical risk domains to legacy compatibility categories."""
    return COMPAT_CATEGORY_BY_DOMAIN.get(risk_domain, "other")


def should_reality_check(query: str) -> tuple[bool, str | None]:
    """Determine if query needs reality (web) checking."""
    query_lower = query.lower()
    for indicator in FACTUAL_INDICATORS:
        if indicator in query_lower:
            return True, f"Factual query detected: '{indicator}'"
    return False, None


def _build_rule_response(prompt: str, rule: RefusalRule, profile: str) -> RefusalResponse:
    """Render a refusal response from a canonical rule definition."""
    return generate_refusal_response(
        prompt=prompt,
        refusal_type=rule.refusal_type,
        risk_domain=rule.risk_domain,
        reason=rule.reason,
        policy_codes=list(rule.policy_codes),
        risk_score=rule.risk_score,
        profile=profile,
    )


def route_refuse(
    prompt: str, high_stakes_indicators: list[str] | None = None, profile: str | None = None
) -> RefusalResponse:
    """
    Enhanced refusal with R1-R5 taxonomy.

    Args:
        prompt: User prompt to analyze
        high_stakes_indicators: Additional risk indicators (optional)
        profile: Refusal profile ("enterprise_defensible", "consumer_survivable", "equilibrium_default")

    Returns:
        RefusalResponse with 4 layers (verdict, reason, alternatives, appeal)
    """
    if profile is None:
        profile = os.getenv(DEFAULT_REFUSAL_PROFILE_ENV, DEFAULT_REFUSAL_PROFILE)

    rule = detect_refusal_rule(prompt)
    if rule is not None:
        return _build_rule_response(prompt, rule, profile)

    # Default soft refuse for ambiguous high-stakes
    if high_stakes_indicators:
        return generate_refusal_response(
            prompt=prompt,
            refusal_type=RefusalType.R2_SOFT,
            risk_domain=RiskDomain.OTHER,
            reason="This request involves risks that I can't safely address as stated.",
            policy_codes=["F2", "F7"],
            risk_score=0.70,
            profile=profile,
        )

    # If no refusal triggered, return None or raise exception
    # (In practice, this function should only be called when refusal is needed)
    return generate_refusal_response(
        prompt=prompt,
        refusal_type=RefusalType.R2_SOFT,
        risk_domain=RiskDomain.OTHER,
        reason="This request requires additional clarification.",
        policy_codes=["F2"],
        risk_score=0.50,
        profile=profile,
    )

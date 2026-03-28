"""
Refusal Response Builder — Profile-Aware Rendering

Constitutional Compliance:
- F9 Anti-Hantu: No "I feel", "I care", "I want" language
- F6 Empathy: At least 2 safe alternatives
- F2 Truth: Non-accusatory reason, no exploit hints
- F1 Amanah: Privacy-safe logging (hash + redaction)

DITEMPA BUKAN DIBERI — Forged, not given.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .templates import DOMAIN_TEMPLATES, SKIN_TEMPLATES
from .types import RefusalResponse, RefusalType, RiskDomain


def load_refusal_config(profile: str = "equilibrium_default") -> dict[str, Any]:
    """
    Load refusal configuration from spec/v55/refusals.json.

    Args:
        profile: One of "enterprise_defensible", "consumer_survivable", "equilibrium_default"

    Returns:
        Profile configuration dict
    """
    config_path = (
        Path(__file__).parent.parent.parent.parent
        / "docs"
        / "60_REFERENCE"
        / "spec"
        / "v55"
        / "refusals.json"
    )

    if not config_path.exists():
        # Fallback to default config
        return {
            "skin": "consumer",
            "logging": {
                "store_redacted_excerpt": True,
                "include_policy_codes": True,
                "include_risk_score": True,
            },
            "appeal": {"keyword": "REVIEW"},
        }

    with open(config_path) as f:
        full_config = json.load(f)

    return full_config.get("profiles", {}).get(
        profile, full_config["profiles"]["equilibrium_default"]
    )


def _redact_prompt(prompt: str, max_length: int = 50) -> str:
    """
    Redact prompt for logging (privacy-safe).

    Args:
        prompt: User prompt to redact
        max_length: Maximum excerpt length (default: 50)

    Returns:
        Redacted string like "[REDACTED: 123 chars] First 20..."
    """
    if len(prompt) <= max_length:
        return f"[REDACTED: {len(prompt)} chars]"
    return f"[REDACTED: {len(prompt)} chars] {prompt[:20]}..."


def generate_refusal_response(
    prompt: str,
    refusal_type: RefusalType,
    risk_domain: RiskDomain,
    reason: str,
    policy_codes: list[str],
    risk_score: float,
    profile: str = "equilibrium_default",
) -> RefusalResponse:
    """
    Generate constitutionally compliant refusal with profile-aware rendering.

    INVARIANT (Constitutional Governance):
    The refusal decision (type, domain, risk_score) MUST NOT depend on presentation profile.
    Profiles affect wording and receipts only, never the verdict itself.
    This preserves governance integrity: decision logic is deterministic and profile-independent.

    Critical Rules:
    - Reason must be non-accusatory (no "you are trying to...")
    - Reason must not provide exploit hints
    - Must provide at least 2 safe alternatives
    - F9 Anti-Hantu compliant (no "I feel", "I care")

    Args:
        prompt: User prompt (for logging, never returned in response)
        refusal_type: One of R1-R5
        risk_domain: Risk category (violence, medical, etc.)
        reason: Plain-language explanation (non-accusatory)
        policy_codes: Constitutional floors triggered (e.g., ["F1", "F5"])
        risk_score: 0.0-1.0 risk assessment
        profile: "enterprise_defensible", "consumer_survivable", or "equilibrium_default"

    Returns:
        RefusalResponse with 4 layers (verdict, reason, alternatives, appeal)
    """

    # Load profile config
    config = load_refusal_config(profile)
    skin = config.get("skin", "consumer")

    # Get verdict template
    verdict_key = f"verdict_{refusal_type.value.lower()}"
    verdict = SKIN_TEMPLATES.get(skin, SKIN_TEMPLATES["consumer"])["copy"].get(
        verdict_key, "I can't help with that."
    )

    # Get domain-specific templates
    template = DOMAIN_TEMPLATES.get(risk_domain.value, DOMAIN_TEMPLATES["other"])

    # Use template reason if provided reason is empty or default
    if not reason or reason in ["policy", "safety", "risk"]:
        reason = template.get("reason", reason)

    # Get alternatives from template
    alternatives = template.get(
        "alternatives",
        ["I can help you reformulate your request.", "I can explain the risks and constraints."],
    )

    # Ensure at least 2 alternatives (F6 Empathy)
    if len(alternatives) < 2:
        alternatives.append("I can provide general information on this topic.")

    # Generate appeal instructions
    appeal_keyword = config.get("appeal", {}).get("keyword", "REVIEW")
    appeal_instructions = (
        f"If you think this was misunderstood, reply '{appeal_keyword}' with context."
    )

    # Generate trace ID
    trace_id = hashlib.sha256(
        f"{prompt}{datetime.now(timezone.utc).isoformat()}".encode()
    ).hexdigest()[:16]

    # Build log data (privacy-safe)
    log_data = {
        "trace_id": trace_id,
        "query_hash": hashlib.sha256(prompt.encode()).hexdigest()[:16],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model_version": "v55.5",
        "profile": profile,
        "redacted_excerpt": (
            _redact_prompt(prompt)
            if config.get("logging", {}).get("store_redacted_excerpt", False)
            else None
        ),
    }

    return RefusalResponse(
        refusal_type=refusal_type,
        risk_domain=risk_domain,
        verdict=verdict,
        reason=reason,
        safe_alternatives=alternatives,
        appeal_instructions=appeal_instructions,
        policy_codes=policy_codes,
        risk_score=risk_score,
        appealable=refusal_type != RefusalType.R5_RATE,
        trace_id=trace_id,
        log_data=log_data,
    )

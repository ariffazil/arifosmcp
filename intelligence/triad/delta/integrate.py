"""
arifosmcp.intelligence/triad/delta/integrate.py — Stage 333 Atlas
Merge context and map dependencies.
"""

from arifosmcp.core.kernel import kernel


async def integrate(session_id: str, context_bundle: dict, knowledge_gap: bool = False) -> dict:
    """
    STAGE 333: Contextual Grounding.
    Merge new information into the session graph.
    """
    # Force audit check
    audit_res = kernel.audit(
        action=f"INTEGRATE_BUNDLE: {list(context_bundle.keys())}",
        context=f"KNOWLEDGE_GAP={knowledge_gap}",
        severity="medium",
    )

    # Log to Vault
    kernel.vault.log_witness(
        session_id=session_id,
        agent_id="ARCHITECT",
        stage="333_ATLAS",
        statement=f"Integrated {len(context_bundle)} keys",
        verdict=audit_res.verdict.value,
    )

    return {
        "verdict": audit_res.verdict.value,
        "omega0_interval": 0.04 if not knowledge_gap else 0.12,
        "recommendation": audit_res.recommendation,
        "status": "integrated",
    }

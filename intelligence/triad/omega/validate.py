"""
arifosmcp.intelligence/triad/omega/validate.py — Stage 555 Empathy
Full constitutional floor audit.
"""

from arifosmcp.core.kernel import kernel


async def validate(session_id: str, action: str, severity: str = "medium") -> dict:
    """
    STAGE 555: The Empathy Gate.
    Full constitutional audit on a proposed action or response.
    """
    audit_res = kernel.audit(action=action, context="EMPATHY_VALIDATION", severity=severity)

    # Update Peace^2 budget
    f5_score = audit_res.floor_results.get("F5").score if "F5" in audit_res.floor_results else 1.0
    kernel.thermo.update_budget(session_id=session_id, peace2=f5_score)

    return {
        "verdict": audit_res.verdict.value,
        "pass_rate": audit_res.pass_rate,
        "floor_results": {f: r.score for f, r in audit_res.floor_results.items()},
        "recommendation": audit_res.recommendation,
    }

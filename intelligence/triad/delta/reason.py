"""
arifosmcp.intelligence/triad/delta/reason.py — Stage 333 Reasoning
Logical causal tracing and structural breakdown.

SAMPLING INTEGRATION (v2026.3):
When FastMCP Context is provided, uses ctx.sample() for governed LLM reasoning.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .._utils import serialize_floor_concerns

if TYPE_CHECKING:
    from fastmcp import Context


_SAMPLING_ENABLED = True

try:
    from arifosmcp.core.constitutional_sampling import ReasonResult, SamplingConfig, sample_reason
except ImportError:
    _SAMPLING_ENABLED = False


async def reason(
    session_id: str,
    hypothesis: str,
    evidence: list[str],
    ctx: Context | None = None,
    use_sampling: bool = True,
    temperature: float = 0.3,
) -> dict[str, Any]:
    """
    STAGE 333: Logical De-entropy.
    Trace the logic from evidence to hypothesis.

    SAMPLING INTEGRATION:
    When ctx is provided, uses constitutional sampling for LLM reasoning.
    """
    if ctx is not None and use_sampling and _SAMPLING_ENABLED:
        return await _reason_with_sampling(session_id, hypothesis, evidence, ctx, temperature)
    return await _reason_with_kernel(session_id, hypothesis, evidence)


async def _reason_with_sampling(
    session_id: str,
    hypothesis: str,
    evidence: list[str],
    ctx: Context,
    temperature: float,
) -> dict[str, Any]:
    """REASON using FastMCP sampling with constitutional governance."""
    try:
        config = SamplingConfig(temperature=temperature, max_tokens=1536)
        result: ReasonResult = await sample_reason(
            ctx=ctx,
            hypothesis=hypothesis,
            evidence=evidence,
            config=config,
        )

        return {
            "verdict": result.verdict.value,
            "truth_score": result.truth_score,
            "f2_threshold": 0.99,
            "delta_s": result.delta_s,
            "evidence_quality": result.evidence_quality,
            "causal_chain": result.causal_chain,
            "sampling_mode": True,
            "recommendation": result.recommendation,
            "status": "metabolized",
            "floor_concerns": serialize_floor_concerns(result.floor_concerns),
        }
    except Exception:
        return await _reason_with_kernel(session_id, hypothesis, evidence)


async def _reason_with_kernel(
    session_id: str,
    hypothesis: str,
    evidence: list[str],
) -> dict[str, Any]:
    """REASON using kernel.audit() structural checks (fallback)."""
    from arifosmcp.core.kernel import kernel

    # Run constitutional audit
    audit_res = kernel.audit(
        action=f"HYPOTHESIS: {hypothesis}\nEVIDENCE: {', '.join(evidence)}",
        context="REASONING_PIPELINE",
        severity="medium",
    )

    # Update Thermo Budget (ΔS reduction)
    kernel.thermo.update_budget(session_id=session_id, delta_s=audit_res.delta_s)

    # Log to Vault
    kernel.vault.log_witness(
        session_id=session_id,
        agent_id="ARCHITECT",
        stage="222_REASON",
        statement=hypothesis,
        verdict=audit_res.verdict.value,
    )

    return {
        "verdict": audit_res.verdict.value,
        "truth_score": audit_res.pass_rate,
        "f2_threshold": 0.99,
        "delta_s": audit_res.delta_s,
        "recommendation": audit_res.recommendation,
        "status": "metabolized",
    }

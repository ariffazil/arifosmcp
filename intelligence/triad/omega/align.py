"""
arifosmcp.intelligence/triad/omega/align.py — Stage 666 Align
Ethics and Anti-Hantu alignment.

SAMPLING INTEGRATION (v2026.3):
When FastMCP Context is provided, uses ctx.sample() for governed LLM reasoning.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from arifosmcp.core.kernel import kernel

from .._utils import serialize_floor_concerns

if TYPE_CHECKING:
    from fastmcp import Context


_SAMPLING_ENABLED = True

try:
    from arifosmcp.core.constitutional_sampling import AlignResult, SamplingConfig, sample_align
except ImportError:
    _SAMPLING_ENABLED = False


async def align(
    session_id: str,
    action: str,
    ctx: Context | None = None,
    use_sampling: bool = True,
    stakeholders: list[str] | None = None,
    temperature: float = 0.4,
) -> dict[str, Any]:
    """
    STAGE 666: The Alignment Axis.
    Enforce F9 (Anti-Hantu) and F10 (Ontology) strictly.

    SAMPLING INTEGRATION:
    When ctx is provided, uses constitutional sampling for LLM alignment.
    """
    if ctx is not None and use_sampling and _SAMPLING_ENABLED:
        return await _align_with_sampling(session_id, action, ctx, stakeholders, temperature)
    return await _align_with_kernel(session_id, action)


async def _align_with_sampling(
    session_id: str,
    action: str,
    ctx: Context,
    stakeholders: list[str] | None,
    temperature: float,
) -> dict[str, Any]:
    """ALIGN using FastMCP sampling with constitutional governance."""
    try:
        config = SamplingConfig(temperature=temperature, max_tokens=1536)
        result: AlignResult = await sample_align(
            ctx=ctx,
            action=action,
            stakeholders=stakeholders,
            config=config,
        )

        return {
            "verdict": result.verdict.value,
            "empathy_score": result.empathy_score,
            "peace_score": result.peace_score,
            "stakeholder_impacts": result.stakeholder_impacts,
            "sampling_mode": True,
            "recommendation": result.recommendation,
            "status": "aligned",
            "floor_concerns": serialize_floor_concerns(result.floor_concerns),
        }
    except Exception:
        return await _align_with_kernel(session_id, action)


async def _align_with_kernel(
    session_id: str,
    action: str,
) -> dict[str, Any]:
    """ALIGN using kernel.audit() structural checks (fallback)."""
    audit_res = kernel.audit(action=action, context="ALIGNMENT_CHECK", severity="medium")

    # Audit specifically for F9/F10
    f9_pass = audit_res.floor_results.get("F9").passed if "F9" in audit_res.floor_results else True
    f10_pass = (
        audit_res.floor_results.get("F10").passed if "F10" in audit_res.floor_results else True
    )

    if not (f9_pass and f10_pass):
        return {
            "verdict": "VOID",
            "reason": "Ontological or Consciousness breach detected.",
            "status": "blocked",
        }

    return {
        "verdict": audit_res.verdict.value,
        "recommendation": audit_res.recommendation,
        "status": "aligned",
    }

"""Core service layer for MCP tool flow control.

This module holds orchestration logic used by transport adapters.
It has no transport/framework imports.
"""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from arifosmcp.core.kernel.mcp_transport_kernel import (
    build_align_error,
    build_align_output,
    build_anchor_output,
    build_audit_error,
    build_audit_fallback,
    build_forge_error,
    build_forge_output,
    build_integrate_error,
    build_integrate_output,
    build_legacy_seal,
    build_reason_error,
    build_reason_output,
    build_respond_error,
    build_respond_output,
    build_seal_error,
    build_validate_error,
    normalize_audit_output,
    normalize_seal_receipt,
    normalize_validate_result,
)

CANONICAL_TOOL_TO_LEGACY: dict[str, str] = {
    "init_anchor": "anchor",
    "reason_mind": "reason",
    "recall_memory": "respond",
    "simulate_heart": "validate",
    "critique_thought": "align",
    "apex_judge": "audit",
    "eureka_forge": "forge",
    "seal_vault": "seal",
    "search_reality": "search",
    "fetch_content": "fetch",
    "inspect_file": "inspect_file",
    "audit_rules": "system_audit",
    "check_vital": "sense_health",
}


def resolve_tool_alias(tool_name: str) -> str:
    """Normalize canonical public tool names to legacy internal handlers."""
    return CANONICAL_TOOL_TO_LEGACY.get(tool_name, tool_name)


def _to_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    return {}


def _get_first_stage_result(
    get_stage_result_fn: Callable[[str, str], dict[str, Any]],
    session_id: str,
    *stage_names: str,
) -> dict[str, Any]:
    for stage_name in stage_names:
        result = get_stage_result_fn(session_id, stage_name)
        if result:
            return result
    return {}


async def anchor_tool(
    *,
    query: str,
    actor_id: str,
    auth_token: str,
    platform: str,
    init_engine: Any,
    store_stage_result_fn: Callable[[str, str, dict[str, Any]], None],
) -> dict[str, Any]:
    init_result = await init_engine.ignite(
        query=query,
        actor_id=actor_id,
        auth_token=auth_token,
        session_id=None,
    )
    output = build_anchor_output(
        init_result=init_result,
        actor_id=actor_id,
        platform=platform,
        governance_mode="HARD",
    )
    store_stage_result_fn(init_result["session_id"], "init", output)
    return output


async def reason_tool(
    *,
    query: str,
    session_id: str,
    hypotheses: int,
    get_stage_result_fn: Callable[[str, str], dict[str, Any]],
    store_stage_result_fn: Callable[[str, str, dict[str, Any]], None],
    sense_fn: Callable[..., Awaitable[dict[str, Any]]],
    think_fn: Callable[..., Awaitable[dict[str, Any]]],
    truth_score_placeholder: float,
    clarity_delta_placeholder: float,
) -> dict[str, Any]:
    try:
        sense_result = get_stage_result_fn(session_id, "sense")
        if not sense_result:
            sense_result = await sense_fn(query, session_id)
            store_stage_result_fn(session_id, "sense", sense_result)

        think_result = await think_fn(query, sense_result, session_id)
        store_stage_result_fn(session_id, "think", think_result)
        return build_reason_output(session_id=session_id, think_result=think_result)
    except Exception as e:
        return build_reason_error(
            session_id=session_id,
            hypotheses=hypotheses,
            truth_score_placeholder=truth_score_placeholder,
            clarity_delta_placeholder=clarity_delta_placeholder,
            error=e,
        )


async def integrate_tool(
    *,
    query: str,
    session_id: str,
    grounding: list | None,
    get_stage_result_fn: Callable[[str, str], dict[str, Any]],
    store_stage_result_fn: Callable[[str, str, dict[str, Any]], None],
    sense_fn: Callable[..., Awaitable[dict[str, Any]]],
    think_fn: Callable[..., Awaitable[dict[str, Any]]],
    reason_fn: Callable[..., Awaitable[dict[str, Any]]],
    humility_omega_default: float,
) -> dict[str, Any]:
    try:
        think_result = get_stage_result_fn(session_id, "think")
        if not think_result:
            sense_result = get_stage_result_fn(session_id, "sense")
            if not sense_result:
                sense_result = await sense_fn(query, session_id)
                store_stage_result_fn(session_id, "sense", sense_result)
            think_result = await think_fn(query, sense_result, session_id)
            store_stage_result_fn(session_id, "think", think_result)

        reason_result = await reason_fn(query, think_result, session_id)
        store_stage_result_fn(session_id, "reason", reason_result)
        return build_integrate_output(
            session_id=session_id,
            reason_result=reason_result,
            grounding=grounding,
            humility_omega_default=humility_omega_default,
        )
    except Exception as e:
        return build_integrate_error(
            session_id=session_id,
            humility_omega_default=humility_omega_default,
            error=e,
        )


async def respond_tool(
    *,
    session_id: str,
    plan: str | None,
    get_stage_result_fn: Callable[[str, str], dict[str, Any]],
    run_stage_444_fn: Callable[..., Awaitable[dict[str, Any]]],
) -> dict[str, Any]:
    try:
        agi_res = _get_first_stage_result(get_stage_result_fn, session_id, "think", "agi")
        asi_res = _get_first_stage_result(
            get_stage_result_fn,
            session_id,
            "empathy",
            "asi_empathize",
            "stage_555",
            "asi",
        )
        stage_result = await run_stage_444_fn(session_id, agi_res, asi_res)
        return build_respond_output(
            session_id=session_id,
            stage_result=stage_result,
            plan=plan,
            plan_id=f"PLAN-{uuid.uuid4().hex[:8].upper()}",
        )
    except Exception as e:
        return build_respond_error(session_id=session_id, error=e)


async def validate_tool(
    *,
    query: str,
    session_id: str,
    stakeholders: list | None,
    run_stage_555_fn: Callable[..., Awaitable[dict[str, Any]]],
    peace_squared_min: float,
    empathy_kappa_r_default: float,
    safe_default: bool,
) -> dict[str, Any]:
    try:
        result = await run_stage_555_fn(session_id, query)
        return normalize_validate_result(
            result=result,
            stakeholders=stakeholders,
            default_kappa_r=empathy_kappa_r_default,
        )
    except Exception as e:
        return build_validate_error(
            session_id=session_id,
            peace_squared_min=peace_squared_min,
            empathy_kappa_r_default=empathy_kappa_r_default,
            safe_default=safe_default,
            error=e,
        )


async def align_tool(
    *,
    query: str,
    session_id: str,
    ethical_rules: list | None,
    run_stage_666_fn: Callable[..., Awaitable[dict[str, Any]]],
) -> dict[str, Any]:
    try:
        result = await run_stage_666_fn(session_id, query)
        return build_align_output(session_id=session_id, result=result, ethical_rules=ethical_rules)
    except Exception as e:
        return build_align_error(session_id=session_id, error=e)


async def forge_tool(
    *,
    session_id: str,
    implementation_details: dict[str, Any],
    get_stage_result_fn: Callable[[str, str], dict[str, Any]],
    run_stage_777_fn: Callable[..., Awaitable[dict[str, Any]]],
) -> dict[str, Any]:
    try:
        agi_res = _get_first_stage_result(get_stage_result_fn, session_id, "think", "agi")
        asi_res = _get_first_stage_result(
            get_stage_result_fn,
            session_id,
            "empathy",
            "asi_empathize",
            "stage_555",
            "asi",
        )
        stage_result = await run_stage_777_fn(session_id, agi_res, asi_res)
        return build_forge_output(
            session_id=session_id,
            stage_result=stage_result,
            implementation_details=implementation_details,
        )
    except Exception as e:
        return build_forge_error(session_id=session_id, error=e)


async def audit_tool(
    *,
    session_id: str,
    verdict: str,
    human_approve: bool,
    tri_witness_score: float,
    get_stage_result_fn: Callable[[str, str], dict[str, Any]],
    run_stage_888_fn: Callable[..., Awaitable[dict[str, Any]]],
) -> dict[str, Any]:
    try:
        agi_res = _get_first_stage_result(get_stage_result_fn, session_id, "agi", "think")
        asi_res = _get_first_stage_result(
            get_stage_result_fn,
            session_id,
            "asi",
            "empathy",
            "asi_empathize",
            "stage_555",
        )
        if agi_res and asi_res:
            judge_out = await run_stage_888_fn(session_id, agi_res, asi_res)
            judge_dict = _to_dict(judge_out) or {"verdict": verdict}
            return normalize_audit_output(judge_dict=judge_dict, human_approve=human_approve)
        return build_audit_fallback(
            session_id=session_id,
            verdict=verdict,
            human_approve=human_approve,
            tri_witness_score=tri_witness_score,
        )
    except Exception as e:
        return build_audit_error(session_id=session_id, error=e)


async def seal_tool(
    *,
    session_id: str,
    summary: str,
    verdict: str,
    get_stage_result_fn: Callable[[str, str], dict[str, Any]],
    run_stage_999_fn: Callable[..., Awaitable[Any]],
) -> dict[str, Any]:
    try:
        judge_res = _get_first_stage_result(
            get_stage_result_fn,
            session_id,
            "judge",
            "audit",
            "stage_888",
            "apex_verdict",
        )
        agi_res = _get_first_stage_result(get_stage_result_fn, session_id, "think", "agi")
        asi_res = _get_first_stage_result(
            get_stage_result_fn,
            session_id,
            "empathy",
            "asi",
            "asi_empathize",
            "stage_555",
            "stage_666",
        )
        if judge_res and agi_res and asi_res:
            receipt = await run_stage_999_fn(session_id, judge_res, agi_res, asi_res, summary)
            return normalize_seal_receipt(session_id=session_id, receipt=receipt)
        return build_legacy_seal(session_id=session_id, verdict=verdict)
    except Exception as e:
        return build_seal_error(session_id=session_id, error=e)


async def trinity_forge_tool(
    *,
    query: str,
    actor_id: str,
    forge_pipeline_fn: Callable[..., Awaitable[Any]],
) -> dict[str, Any]:
    try:
        result = await forge_pipeline_fn(query, actor_id=actor_id)
        if hasattr(result, "model_dump"):
            return result.model_dump()
        if isinstance(result, dict):
            return result
        return {"verdict": "SABAR", "stage": "FORGE_PIPELINE", "error": "Unexpected forge output"}
    except Exception as e:
        return {
            "verdict": "SABAR",
            "error": str(e),
            "stage": "FORGE_PIPELINE",
        }


__all__ = [
    "CANONICAL_TOOL_TO_LEGACY",
    "resolve_tool_alias",
    "anchor_tool",
    "reason_tool",
    "integrate_tool",
    "respond_tool",
    "validate_tool",
    "align_tool",
    "forge_tool",
    "audit_tool",
    "seal_tool",
    "trinity_forge_tool",
]

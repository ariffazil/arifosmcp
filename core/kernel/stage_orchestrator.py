"""Kernel stage orchestration for 444-999 flow.

Pure orchestration logic for constitutional stages.
No transport/storage modules are imported directly; all side effects are injected.
"""

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from arifosmcp.core import organs as core_organs
from arifosmcp.core.shared.physics import Peace2

logger = logging.getLogger("STAGE_ADAPTER")

GetStageResult = Callable[[str, str], dict[str, Any]]
StoreStageResult = Callable[[str, str, dict[str, Any]], None]
LogAsiDecision = Callable[..., Awaitable[None]]


def _default_get_stage_result(_session_id: str, _stage: str) -> dict[str, Any]:
    return {}


def _default_store_stage_result(_session_id: str, _stage: str, _payload: dict[str, Any]) -> None:
    return None


async def _default_log_asi_decision(**_kwargs: Any) -> None:
    return None


def _get_first_stage_result(
    get_stage_result_fn: GetStageResult,
    session_id: str,
    *stage_names: str,
) -> dict[str, Any]:
    for stage_name in stage_names:
        result = get_stage_result_fn(session_id, stage_name)
        if result:
            return result
    return {}


def _store_stage_with_aliases(
    store_stage_result_fn: StoreStageResult,
    session_id: str,
    result: dict[str, Any],
    *stage_names: str,
) -> None:
    for stage_name in stage_names:
        store_stage_result_fn(session_id, stage_name, result)


def _as_dict(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict):
        return payload
    if hasattr(payload, "model_dump"):
        return payload.model_dump()
    if hasattr(payload, "dict"):
        return payload.dict()
    return {}


def _extract_query_from_stage_inputs(
    agi_result: dict[str, Any],
    asi_result: dict[str, Any],
    stage: str,
) -> str:
    query = agi_result.get("query") or asi_result.get("query") or ""
    if not query:
        raise ValueError(f"Missing query for stage {stage}")
    return query


async def _build_agi_tensor(query: str, session_id: str) -> Any:
    await core_organs.sense(query, session_id, action="sense")
    await core_organs.think(query, session_id, action="think")
    agi_tensor = await core_organs.reason(query, session_id, action="reason")
    if hasattr(agi_tensor, "peace") and agi_tensor.peace is None:
        agi_tensor.peace = Peace2({})
    return agi_tensor


def _build_asi_output(asi_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "kappa_r": asi_result.get("kappa_r", asi_result.get("empathy_kappa_r", 0.7)),
        "peace_squared": asi_result.get("peace_squared", 1.0),
        "is_reversible": asi_result.get("is_reversible", True),
        "verdict": asi_result.get("verdict", "SEAL"),
    }


def _collect_floor_failures_from_scores(
    floor_scores: dict[str, Any],
    *,
    threshold: float = 0.5,
) -> list[str]:
    floor_key_map = {
        "f1_amanah": "F1",
        "f5_peace": "F5",
        "f6_empathy": "F6",
        "f9_anti_hantu": "F9",
    }
    failed: list[str] = []
    for raw_key, raw_score in floor_scores.items():
        score = float(raw_score) if isinstance(raw_score, (int, float)) else 1.0
        norm_key = str(raw_key).lower()
        mapped = floor_key_map.get(norm_key)
        if mapped and score < threshold and mapped not in failed:
            failed.append(mapped)
    return failed


def _collect_floor_failures_from_violations(violations: list[Any]) -> list[str]:
    failed: list[str] = []
    for violation in violations:
        text = str(violation)
        for floor_id in ("F1", "F5", "F6", "F9"):
            if text.startswith(f"{floor_id}_") and floor_id not in failed:
                failed.append(floor_id)
    return failed


async def run_stage_444_trinity_sync(
    session_id: str,
    agi_result: dict[str, Any] | None = None,
    asi_result: dict[str, Any] | None = None,
    *,
    get_stage_result_fn: GetStageResult = _default_get_stage_result,
    store_stage_result_fn: StoreStageResult = _default_store_stage_result,
) -> dict[str, Any]:
    """
    Stage 444: Trinity Sync - Merge AGI and ASI outputs.

    Called by: apex_verdict tool (before judgment)
    """
    try:
        agi_result = agi_result or _get_first_stage_result(
            get_stage_result_fn, session_id, "agi", "think"
        )
        asi_result = asi_result or _get_first_stage_result(
            get_stage_result_fn,
            session_id,
            "asi_empathize",
            "stage_555",
            "empathy",
            "asi",
        )
        query = _extract_query_from_stage_inputs(agi_result, asi_result, "444")

        # Unified Call: action="full" is safest for sync
        sync_out = await core_organs.sync(action="full", session_id=session_id, intent=query)

        # Handle Pydantic model output
        if hasattr(sync_out, "verdict"):
            pre_verdict = (
                sync_out.verdict.value
                if hasattr(sync_out.verdict, "value")
                else str(sync_out.verdict)
            )
            w3_score = (
                sync_out.floor_scores.f3_tri_witness if hasattr(sync_out, "floor_scores") else 0.95
            )
        else:
            sync_data = _as_dict(sync_out)
            pre_verdict = sync_data.get("verdict", "SEAL")
            w3_score = sync_data.get("floor_scores", {}).get("f3_tri_witness", 0.95)

        result = {
            "stage": "444",
            "pre_verdict": pre_verdict,
            "consensus_score": w3_score,
            "session_id": session_id,
            "status": "completed",
        }
        _store_stage_with_aliases(store_stage_result_fn, session_id, result, "stage_444", "sync")
        return result

    except Exception as e:
        logger.error(f"[444] Stage execution failed: {e}")
        return {
            "stage": "444",
            "pre_verdict": "VOID",
            "error": str(e),
            "session_id": session_id,
            "status": "failed",
        }


async def run_stage_555_empathy(
    session_id: str,
    query: str,
    *,
    store_stage_result_fn: StoreStageResult = _default_store_stage_result,
    log_asi_decision_fn: LogAsiDecision = _default_log_asi_decision,
) -> dict[str, Any]:
    """
    Stage 555: ASI Empathy - Identify stakeholders and compute κᵣ.
    """
    try:
        emp_out = await core_organs.empathize(
            action="simulate_heart", session_id=session_id, scenario=query
        )

        emp_data = _as_dict(emp_out)
        kappa_r = emp_data.get("floor_scores", {}).get("f6_empathy", 0.96)

        result = {
            "stage": "555",
            "verdict": emp_data.get("verdict", "SEAL"),
            "empathy_kappa_r": kappa_r,
            "stakeholders": emp_data.get("assessment", {}).get("stakeholders", []),
            "session_id": session_id,
            "status": "completed",
        }
        # Ω Incident Logging (Hardening)
        try:
            floor_scores = emp_data.get("floor_scores", {})
            floors_failed = [
                f for f, s in floor_scores.items() if isinstance(s, (int, float)) and s < 0.7
            ]
            await log_asi_decision_fn(
                session_id=session_id,
                stage="555",
                query=query,
                asi_output=emp_data,
                verdict=result["verdict"],
                floors_checked=["F5", "F6", "F9"],
                floors_failed=floors_failed,
            )
        except Exception as e:
            logger.warning(f"[555] Failed to log ASI incident: {e}")

        return result

    except Exception as e:
        logger.error(f"[555] Stage execution failed: {e}")
        return {
            "stage": "555",
            "verdict": "VOID",
            "error": str(e),
            "session_id": session_id,
            "status": "failed",
        }


async def run_stage_666_align(
    session_id: str,
    query: str,
    *,
    store_stage_result_fn: StoreStageResult = _default_store_stage_result,
    log_asi_decision_fn: LogAsiDecision = _default_log_asi_decision,
) -> dict[str, Any]:
    """
    Stage 666: ASI Align - Safety & reversibility check.
    """
    try:
        align_out = await core_organs.align(action="full", session_id=session_id, scenario=query)

        align_data = _as_dict(align_out)
        verdict = align_data.get("verdict", "SEAL")
        if hasattr(verdict, "value"):
            verdict = verdict.value

        result = {
            "stage": "666",
            "verdict": str(verdict),
            "omega_bundle": align_data,
            "session_id": session_id,
            "status": "completed",
        }
        _store_stage_with_aliases(store_stage_result_fn, session_id, result, "stage_666", "align")

        # Ω Incident Logging (Hardening)
        try:
            floor_scores = align_data.get("floor_scores", {})
            floors_failed = [
                f for f, s in floor_scores.items() if isinstance(s, (int, float)) and s < 0.7
            ]
            await log_asi_decision_fn(
                session_id=session_id,
                stage="666",
                query=query,
                asi_output=align_data,
                verdict=result["verdict"],
                floors_checked=["F1", "F5", "F6", "F9"],
                floors_failed=floors_failed,
            )
        except Exception as e:
            logger.warning(f"[666] Failed to log ASI incident: {e}")

        return result

    except Exception as e:
        logger.error(f"[666] Stage execution failed: {e}")
        return {
            "stage": "666",
            "verdict": "VOID",
            "error": str(e),
            "session_id": session_id,
            "status": "failed",
        }


async def run_stage_777_forge(
    session_id: str,
    agi_result: dict[str, Any] | None = None,
    asi_result: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
    *,
    get_stage_result_fn: GetStageResult = _default_get_stage_result,
    store_stage_result_fn: StoreStageResult = _default_store_stage_result,
) -> dict[str, Any]:
    """
    Stage 777: EUREKA FORGE - Phase transition / synthesis.
    """
    try:
        agi_result = agi_result or _get_first_stage_result(
            get_stage_result_fn, session_id, "agi", "think"
        )
        asi_result = asi_result or _get_first_stage_result(
            get_stage_result_fn, session_id, "asi", "empathy"
        )
        query = _extract_query_from_stage_inputs(agi_result, asi_result, "777")

        forge_out = await core_organs.forge(intent=query, session_id=session_id)
        forge_data = _as_dict(forge_out)

        result = {
            "stage": "777",
            "forge_result": forge_data,
            "session_id": session_id,
            "status": "completed",
        }
        _store_stage_with_aliases(store_stage_result_fn, session_id, result, "stage_777", "forge")
        return result

    except Exception as e:
        logger.error(f"[777] Stage execution failed: {e}")
        return {"stage": "777", "error": str(e), "session_id": session_id, "status": "failed"}


async def run_stage_888_judge(
    session_id: str,
    agi_result: dict[str, Any] | None = None,
    asi_result: dict[str, Any] | None = None,
    *,
    get_stage_result_fn: GetStageResult = _default_get_stage_result,
    store_stage_result_fn: StoreStageResult = _default_store_stage_result,
) -> dict[str, Any]:
    """
    Stage 888: APEX Judge Metabolic Layer - Executive veto / final judgment.
    """
    try:
        agi_result = agi_result or _get_first_stage_result(
            get_stage_result_fn, session_id, "agi", "think"
        )
        asi_result = asi_result or _get_first_stage_result(
            get_stage_result_fn, session_id, "asi", "empathy"
        )

        # Derive candidate: pick most restrictive between Mind and Heart
        candidate = "SEAL"
        v1 = str(agi_result.get("verdict", "SEAL")).upper()
        v2 = str(asi_result.get("verdict", "SEAL")).upper()

        # Simple monotone safety priority
        if "VOID" in (v1, v2):
            candidate = "VOID"
        elif "HOLD" in (v1, v2):
            candidate = "HOLD_888"
        elif "SABAR" in (v1, v2):
            candidate = "SABAR"
        elif "PARTIAL" in (v1, v2):
            candidate = "PARTIAL"

        judge_out = await core_organs.judge(session_id=session_id, verdict_candidate=candidate)
        judge_data = _as_dict(judge_out)
        verdict = judge_data.get("verdict", "VOID")
        if hasattr(verdict, "value"):
            verdict = verdict.value

        result = {
            "stage": "888",
            "verdict": str(verdict),
            "judge_result": judge_data,
            "session_id": session_id,
            "status": "completed",
        }
        _store_stage_with_aliases(store_stage_result_fn, session_id, result, "stage_888", "judge")
        return result

    except Exception as e:
        logger.error(f"[888] Stage execution failed: {e}")
        return {
            "stage": "888",
            "verdict": "VOID",
            "error": str(e),
            "session_id": session_id,
            "status": "failed",
        }


async def run_stage_999_seal(
    session_id: str,
    judge_result: dict[str, Any] | None = None,
    agi_result: dict[str, Any] | None = None,
    asi_result: dict[str, Any] | None = None,
    summary: str | None = None,
    *,
    get_stage_result_fn: GetStageResult = _default_get_stage_result,
    store_stage_result_fn: StoreStageResult = _default_store_stage_result,
) -> dict[str, Any]:
    """
    Stage 999: Seal - EUREKA-filtered immutable audit.

    Called by: vault_seal tool
    """
    try:
        agi_result = agi_result or _get_first_stage_result(
            get_stage_result_fn, session_id, "agi", "think"
        )
        query = agi_result.get("query", "Unknown query")

        judge_out = judge_result or _get_first_stage_result(
            get_stage_result_fn, session_id, "stage_888", "judge"
        )

        receipt = await core_organs.seal(
            session_id=session_id,
            summary=summary or query,
            verdict=judge_out.get("verdict", "SEAL"),
            approved_by="system",
        )

        receipt_data = _as_dict(receipt)

        result = {
            "stage": "999",
            "status": receipt_data.get("status", "SUCCESS"),
            "hash": receipt_data.get("hash", receipt_data.get("seal_record", {}).get("hash", "0x")),
            "session_id": session_id,
        }
        _store_stage_with_aliases(store_stage_result_fn, session_id, result, "stage_999", "seal")
        return result

        result = {
            "stage": "999",
            "status": receipt.status,
            "apex_verdict": judge_out.get("verdict"),
            "eureka_verdict": receipt.status,
            "hash": receipt.entry_hash,
            "seal_id": receipt.seal_id,
            "session_id": session_id,
        }
        _store_stage_with_aliases(store_stage_result_fn, session_id, result, "stage_999", "seal")
        return result

    except Exception as e:
        logger.error(f"[999] Stage execution failed: {e}")
        return {
            "stage": "999",
            "status": "VOID",
            "error": str(e),
            "session_id": session_id,
        }


# Convenience function to run full 444-999 pipeline
async def run_metabolic_pipeline(
    session_id: str,
    query: str,
    *,
    get_stage_result_fn: GetStageResult = _default_get_stage_result,
    store_stage_result_fn: StoreStageResult = _default_store_stage_result,
    log_asi_decision_fn: LogAsiDecision = _default_log_asi_decision,
) -> dict[str, Any]:
    """
    Run the full metabolic pipeline (444-999) for a session.

    Returns:
        Dict containing results from all stages.
    """
    results = {"session_id": session_id, "stages": {}}

    # Stage 444: Trinity Sync
    results["stages"]["444"] = await run_stage_444_trinity_sync(
        session_id=session_id,
        get_stage_result_fn=get_stage_result_fn,
        store_stage_result_fn=store_stage_result_fn,
    )

    # Stage 555: Empathy (if not already run)
    if not get_stage_result_fn(session_id, "stage_555"):
        results["stages"]["555"] = await run_stage_555_empathy(
            session_id=session_id,
            query=query,
            store_stage_result_fn=store_stage_result_fn,
            log_asi_decision_fn=log_asi_decision_fn,
        )

    # Stage 666: Align (if not already run)
    if not get_stage_result_fn(session_id, "stage_666"):
        results["stages"]["666"] = await run_stage_666_align(
            session_id=session_id,
            query=query,
            store_stage_result_fn=store_stage_result_fn,
            log_asi_decision_fn=log_asi_decision_fn,
        )

    # Stage 777: Forge
    results["stages"]["777"] = await run_stage_777_forge(
        session_id=session_id,
        get_stage_result_fn=get_stage_result_fn,
        store_stage_result_fn=store_stage_result_fn,
    )

    # Stage 888: Judge
    results["stages"]["888"] = await run_stage_888_judge(
        session_id=session_id,
        get_stage_result_fn=get_stage_result_fn,
        store_stage_result_fn=store_stage_result_fn,
    )

    # Stage 999: Seal
    results["stages"]["999"] = await run_stage_999_seal(
        session_id=session_id,
        get_stage_result_fn=get_stage_result_fn,
        store_stage_result_fn=store_stage_result_fn,
    )

    # Determine final verdict
    final_verdict = results["stages"]["888"].get("verdict", "VOID")
    results["final_verdict"] = final_verdict

    return results


__all__ = [
    "run_stage_444_trinity_sync",
    "run_stage_555_empathy",
    "run_stage_666_align",
    "run_stage_777_forge",
    "run_stage_888_judge",
    "run_stage_999_seal",
    "run_metabolic_pipeline",
]

"""Kernel constitutional decorator logic.

This module contains floor enforcement logic independent of transport frameworks.

P0 HARDENING:
- F4: ΔS <= 0 strict entropy reduction (no exceptions)
- F1: Amanah irreversibility check at decorator level
- Fail-closed: Any ambiguity → VOID
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

from arifosmcp.core.kernel.evaluator import (
    HARD_FLOORS,
    MANDATORY_PRE_FLOORS,
    POST_FLOORS,
    PRE_FLOORS,
    SOFT_FLOORS,
    evaluator,
)

# ═══════════════════════════════════════════════════════
# P0 HARDENING: Strict Constitutional Checks
# ═══════════════════════════════════════════════════════


class EntropyViolationError(Exception):
    """P0: F4 Clarity violation - ΔS > 0 (entropy increased)."""

    pass


class AmanahViolationError(Exception):
    """P0: F1 Amanah violation - irreversible action without mandate."""

    pass


# Backward-compatible aliases for existing imports.
EntropyViolation = EntropyViolationError
AmanahViolation = AmanahViolationError


def check_entropy_reduction(delta_s: float) -> dict[str, Any]:
    """
    P0 HARDENING: Strict ΔS <= 0 enforcement.

    Any output that increases entropy (adds confusion) is VOID.
    No exceptions, no partial credit.

    Args:
        delta_s: Entropy change (must be <= 0)

    Returns:
        Dict with pass/fail status

    Raises:
        EntropyViolation: If delta_s > 0 (strict enforcement)
    """
    # STRICT: Any positive delta_s is a violation
    if delta_s > 0:
        raise EntropyViolation(
            f"F4_CLARITY_VIOLATION: ΔS={delta_s:.4f} > 0. "
            f"Output increases entropy (adds confusion). "
            f"Constitutional requirement: ΔS <= 0."
        )

    return {
        "passed": True,
        "floor": "F4",
        "delta_s": delta_s,
        "threshold": 0.0,
        "strict": True,
    }


def check_amanah(
    action_reversible: bool,
    has_sovereign_mandate: bool,
    action_type: str = "default",
) -> dict[str, Any]:
    """
    P0 HARDENING: F1 Amanah - Irreversibility awareness.

    All tasks must be reversible at governance level OR have sovereign mandate.

    Args:
        action_reversible: Can action be undone/replayed
        has_sovereign_mandate: Does action have 888 Judge authorization
        action_type: Type of action (delete, deploy, modify, etc.)

    Returns:
        Dict with pass/fail status

    Raises:
        AmanahViolation: If irreversible action lacks mandate
    """
    # Critical irreversible actions
    irreversible_actions = ["delete", "deploy", "destroy", "erase", "purge"]

    is_critical = any(action in action_type.lower() for action in irreversible_actions)

    if is_critical and not has_sovereign_mandate:
        raise AmanahViolation(
            f"F1_AMANAH_VIOLATION: Irreversible action '{action_type}' "
            f"without sovereign mandate. 888_HOLD required."
        )

    if not action_reversible and not has_sovereign_mandate:
        raise AmanahViolation(
            "F1_AMANAH_VIOLATION: Action not reversible and lacks mandate. "
            "All actions must be auditable or reversible."
        )

    return {
        "passed": True,
        "floor": "F1",
        "reversible": action_reversible,
        "mandate": has_sovereign_mandate,
    }


logger = logging.getLogger(__name__)

FLOOR_ENFORCEMENT = {
    "anchor": ["F11", "F12"],
    "reason": ["F2", "F4", "F8"],
    "integrate": ["F7", "F10"],
    "respond": ["F4", "F6"],
    "validate": ["F5", "F6", "F1"],
    "align": ["F9"],
    "forge": ["F2", "F4", "F7"],
    "audit": ["F3", "F11", "F13"],
    "seal": ["F1", "F3"],
    "phoenix_recall": ["F4", "F7", "F13"],  # recall_memory - Omega Lane
    "reality_search": ["F2", "F4", "F12"],  # search_reality - Delta Lane
    "fetch": ["F2", "F4", "F12"],  # fetch_content - Delta Lane
    "system_audit": ["F2", "F8", "F10"],  # audit_rules - Delta Lane
    "analyze": ["F1", "F4", "F11"],  # inspect_file - Delta Lane
    "sense_health": ["F4", "F5", "F7"],  # check_vital - Omega Lane
    "trinity_forge": [
        "F1",
        "F2",
        "F3",
        "F4",
        "F5",
        "F6",
        "F7",
        "F8",
        "F9",
        "F10",
        "F11",
        "F12",
        "F13",
    ],
}


def _extract_query(args: tuple, kwargs: dict[str, Any]) -> str:
    query = kwargs.get("query") or kwargs.get("input") or ""
    if not query and args:
        query = args[0] if isinstance(args[0], str) else ""
    return str(query)


def _default_format_tool_output(_tool_name: str, payload: Any, _output_mode: str) -> Any:
    return payload


def _default_resolve_output_mode(_kwargs: dict[str, Any]) -> str:
    return "debug"


def _default_build_hard_floor_block(
    *,
    floor: str,
    score: float,
    threshold: float,
    reason: str,
    session_id: str,
    remediation: dict[str, Any],
) -> dict[str, Any]:
    return {
        "verdict": "VOID",
        "blocked_by_floor": floor,
        "score": score,
        "threshold": threshold,
        "reason": reason,
        "session_id": session_id,
        "remediation": remediation,
    }


def constitutional_floor(
    *floors: str,
    format_tool_output_fn: Callable[[str, Any, str], Any] | None = None,
    resolve_output_mode_fn: Callable[[dict[str, Any]], str] | None = None,
    build_hard_floor_block_fn: Callable[..., dict[str, Any]] | None = None,
):
    """Decorator to enforce constitutional floors on tool callables."""

    format_tool_output = format_tool_output_fn or _default_format_tool_output
    resolve_output_mode = resolve_output_mode_fn or _default_resolve_output_mode
    build_hard_floor_block = build_hard_floor_block_fn or _default_build_hard_floor_block

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start = time.time()
            tool_name = func.__name__
            floor_details: list[dict[str, Any]] = []
            query = _extract_query(args, kwargs)
            output_mode = resolve_output_mode(kwargs)
            session_id = kwargs.get("session_id", "unknown")

            all_floors = list(dict.fromkeys(list(MANDATORY_PRE_FLOORS) + list(floors)))

            pre_ctx = evaluator.build_pre_context(query, kwargs)
            for fid in MANDATORY_PRE_FLOORS:
                if fid not in floors:
                    detail = evaluator.check_floor(fid, pre_ctx)
                    detail["phase"] = "mandatory_pre"
                    floor_details.append(detail)
                    if not detail["passed"] and fid in HARD_FLOORS:
                        elapsed_ms = round((time.time() - start) * 1000, 1)
                        logger.warning(f"VOID [{tool_name}]: MANDATORY {fid} blocked")
                        payload = build_hard_floor_block(
                            floor=fid,
                            score=detail["score"],
                            threshold=detail.get("threshold", 0.0),
                            reason=detail["reason"],
                            session_id=session_id,
                            remediation={
                                "action": "BLOCK",
                                "message": f"Mandatory floor {fid} failed.",
                                "tool": tool_name,
                            },
                        )
                        payload["_constitutional"] = {
                            "floors_enforced": list(all_floors),
                            "details": floor_details,
                            "enforcement_ms": elapsed_ms,
                        }
                        return format_tool_output(tool_name, payload, output_mode)

            pre = [f for f in floors if f in PRE_FLOORS]
            for fid in pre:
                detail = evaluator.check_floor(fid, pre_ctx)
                detail["phase"] = "pre"
                floor_details.append(detail)
                if not detail["passed"] and fid in HARD_FLOORS:
                    elapsed_ms = round((time.time() - start) * 1000, 1)
                    logger.warning(f"VOID [{tool_name}]: {fid} blocked")
                    payload = build_hard_floor_block(
                        floor=fid,
                        score=detail["score"],
                        threshold=detail.get("threshold", 0.0),
                        reason=detail["reason"],
                        session_id=session_id,
                        remediation={
                            "action": "HUMAN_REVIEW",
                            "message": f"Floor {fid} failed.",
                            "tool": tool_name,
                        },
                    )
                    payload["_constitutional"] = {
                        "floors_enforced": list(floors),
                        "details": floor_details,
                        "enforcement_ms": elapsed_ms,
                    }
                    return format_tool_output(tool_name, payload, output_mode)

            result = await func(*args, **kwargs)

            post = [f for f in floors if f in POST_FLOORS]
            if post and isinstance(result, dict):
                post_ctx = evaluator.build_post_context(query, result, kwargs)
                for fid in post:
                    if fid == "F8":
                        post_ctx["_floor_scores"] = evaluator.accumulate_floor_scores(floor_details)
                    detail = evaluator.check_floor(fid, post_ctx)
                    detail["phase"] = "post"
                    floor_details.append(detail)

            verdict = evaluator.evaluate_verdict(floor_details)
            self_audit = evaluator.build_self_audit(floor_details, verdict)
            elapsed_ms = round((time.time() - start) * 1000, 1)

            if isinstance(result, dict):
                result["verdict"] = verdict
                result["_constitutional"] = {
                    "floors_declared": list(floors),
                    "floors_checked": [d["floor"] for d in floor_details],
                    "details": floor_details,
                    "self_audit": self_audit,
                    "arif_test": {
                        "deterministic_kernel": True,
                        "llm_inside_kernel": False,
                    },
                    "enforcement_ms": elapsed_ms,
                    "version": "v64.2-CORE",
                }
                if verdict == "VOID":
                    result["status"] = "BLOCKED"
                    result["blocked_by"] = [
                        d["floor"]
                        for d in floor_details
                        if not d["passed"] and d["floor"] in HARD_FLOORS
                    ]
                elif verdict == "PARTIAL":
                    result["warnings"] = [
                        {"floor": d["floor"], "reason": d["reason"]}
                        for d in floor_details
                        if not d["passed"] and d["floor"] in SOFT_FLOORS
                    ]

            return format_tool_output(tool_name, result, output_mode)

        wrapper._constitutional_floors = floors
        return wrapper

    return decorator


def get_tool_floors(tool_name: str) -> list:
    return FLOOR_ENFORCEMENT.get(tool_name, [])


__all__ = [
    # P0 HARDENING
    "EntropyViolation",
    "AmanahViolation",
    "check_entropy_reduction",
    "check_amanah",
    # Core decorator
    "constitutional_floor",
    "get_tool_floors",
    "FLOOR_ENFORCEMENT",
]

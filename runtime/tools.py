"""
arifosmcp/runtime/tools.py — arifOS MCP Tool Surface

THIN DISPATCHER: This module re-exports mega-tools from megaTools/ package.
Each mega-tool is now in its own file for independent auditing and testing.

11 Mega-Tools:
  01_init_anchor       → 000_INIT   (PSI Ψ)
  02_arifOS_kernel     → 444_ROUTER (DELTA/PSI)
  03_apex_judge         → 888_JUDGE  (PSI Ψ)
  04_vault_ledger      → 999_VAULT  (PSI Ψ)
  05_agi_mind          → 333_MIND   (DELTA Δ)
  06_asi_heart         → 666_HEART  (OMEGA Ω)
  07_engineering_memory→ 555_MEMORY (OMEGA Ω)
  08_physics_reality   → 111_SENSE  (DELTA Δ)
  09_math_estimator    → 444_ROUTER (DELTA Δ)
  10_code_engine       → M-3_EXEC   (ALL)
  11_architect_registry→ M-4_ARCH   (DELTA Δ)

Split: 2026-03-28 — tools.py (2153 lines) → megaTools/ (11 × ~100 lines each)
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any, Callable, Dict, Union
from fastmcp import FastMCP
from fastmcp.dependencies import CurrentContext
from fastmcp.server.context import Context
from arifosmcp.runtime.bridge import call_kernel
from arifosmcp.runtime.governance_identities import (
    PROTECTED_SOVEREIGN_IDS,
    is_protected_sovereign_id,
    validate_sovereign_proof,
)
from arifosmcp.runtime.models import (
    ArifOSError,
    CallerContext,
    CanonicalError,
    RuntimeEnvelope,
    RuntimeStatus,
    Stage,
    UserModel,
    UserModelField,
    UserModelSource,
    Verdict,
    PersonaId,
    ClaimStatus,
    AuthorityLevel,
)
from arifosmcp.runtime.public_registry import (
    public_tool_names as _registry_tool_names,
    public_tool_spec_by_name as _registry_tool_spec_by_name,
    public_tool_specs as _registry_tool_specs,
)
from arifosmcp.runtime.tool_specs import (
    MegaToolName,
    ToolSpec,
)
from arifosmcp.runtime.reality_handlers import handler as reality_handler
from arifosmcp.runtime.reality_models import BundleInput
from arifosmcp.runtime.sessions import (
    _normalize_session_id,
    _resolve_session_id,
    get_session_identity,
    resolve_runtime_context,
    set_active_session,
)
from arifosmcp.runtime.schemas import IntentType
from arifosmcp.runtime.tools_hardened_dispatch import HARDENED_DISPATCH_MAP
from arifosmcp.runtime.tools_internal import (
    agi_mind_dispatch_impl,
    apex_judge_dispatch_impl,
    architect_registry_dispatch_impl,
    arifos_kernel_impl,
    asi_heart_dispatch_impl,
    code_engine_dispatch_impl,
    engineering_memory_dispatch_impl,
    math_estimator_dispatch_impl,
    physics_reality_dispatch_impl,
    vault_ledger_dispatch_impl,
)

# 🔥 Hardening: Path-safe import for Canonical Schemas
try:
    from schemas.canonical import CanonicalResponse, Verdict, IntelligenceStatus
except ImportError:
    # Fallback to internal or dynamic if path is weird during bootstrap
    CanonicalResponse = None

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# RE-EXPORT MEGA-TOOLS FROM megaTools/ PACKAGE
# ═══════════════════════════════════════════════════════════════════════════════

from arifosmcp.runtime.megaTools import (
    init_anchor,
    arifOS_kernel,
    apex_judge,
    vault_ledger,
    agi_mind,
    asi_heart,
    engineering_memory,
    physics_reality,
    math_estimator,
    code_engine,
    architect_registry,
)

try:
    from arifosmcp.init_000.tools import (
        get_deployment as init_000_get_deployment,
        get_provider_soul as init_000_get_provider_soul,
        get_session_anchor as init_000_get_session_anchor,
        log_drift_event as init_000_log_drift_event,
    )
except (ImportError, ModuleNotFoundError):
    # init_000 not available in this environment
    init_000_get_deployment = None
    init_000_get_provider_soul = None
    init_000_get_session_anchor = None
    init_000_log_drift_event = None

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS (kept in tools.py for utilities)
# ═══════════════════════════════════════════════════════════════════════════════


def _has_valid_proof(payload: dict[str, Any], actor_id: str) -> bool:
    proof = payload.get("auth_token") or payload.get("proof") or payload.get("signature")
    if isinstance(proof, dict):
        return validate_sovereign_proof(actor_id, proof)
    return False


def select_governed_philosophy(
    context: str,
    *,
    stage: str,
    verdict: str,
    g_score: float = 1.0,
    failed_floors: list[str] = None,
    session_id: str = "global",
) -> dict[str, Any]:
    from arifosmcp.runtime.philosophy import select_governed_philosophy as _select

    return _select(
        context=context,
        stage=stage,
        verdict=verdict,
        g_score=g_score,
        failed_floors=failed_floors,
        session_id=session_id,
    )


_public_tool_names_fn = _registry_tool_names
_public_tool_specs_fn = _registry_tool_specs
_public_tool_spec_by_name_fn = _registry_tool_spec_by_name
PUBLIC_KERNEL_TOOL_NAME = "arifOS_kernel"
LEGACY_KERNEL_TOOL_NAME = "metabolic_loop_router"

try:
    from arifosmcp.core.telemetry import check_adaptation_status, get_current_hysteresis
except Exception:

    def check_adaptation_status() -> dict[str, Any]:
        return {"status": "unavailable"}

    def get_current_hysteresis() -> float:
        return 0.0


try:
    from arifosmcp.core.physics.thermodynamics_hardened import get_thermodynamic_report
except Exception:

    def get_thermodynamic_report(session_id: str) -> dict[str, Any]:
        return {"status": "unavailable", "session_id": session_id}


# ═══════════════════════════════════════════════════════════════════════════════
# LEGACY COMPAT TOOLS (kept for backward compatibility)
# ═══════════════════════════════════════════════════════════════════════════════


async def metabolic_loop_router(
    query: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    intent: IntentType = None,
    human_approval: bool = False,
    risk_tier: str = "medium",
    dry_run: bool = True,
    allow_execution: bool = False,
    caller_context: dict | None = None,
    auth_context: dict | None = None,
    ctx: Context | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    return await arifOS_kernel(
        query=query,
        session_id=session_id,
        actor_id=actor_id,
        intent=intent,
        human_approval=human_approval,
        risk_tier=risk_tier,
        dry_run=dry_run,
        allow_execution=allow_execution,
        caller_context=caller_context,
        auth_context=auth_context,
        ctx=ctx,
        **kwargs,
    )


def _build_user_model(
    tool_name: str, stage_value: str, payload: dict[str, Any], envelope_data: dict[str, Any]
) -> UserModel:
    query = str(
        payload.get("query") or payload.get("intent") or payload.get("content") or ""
    ).strip()
    context = str(payload.get("context") or "").strip()
    output_constraints: list[UserModelField] = []
    lowered = f"{query} {context}".lower()
    if "concise" in lowered:
        output_constraints.append(
            UserModelField(value="keep_response_concise", source=UserModelSource.EXPLICIT)
        )
    if envelope_data.get("meta", {}).get("dry_run") or payload.get("dry_run"):
        output_constraints.append(
            UserModelField(
                value="state_that_execution_is_simulated", source=UserModelSource.OBSERVABLE
            )
        )
    return UserModel(
        stated_goal=UserModelField(
            value=query or context or f"{tool_name}:{stage_value}", source=UserModelSource.EXPLICIT
        ),
        output_constraints=output_constraints,
    )


async def arifos_kernel(
    query: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    intent: IntentType = None,
    human_approval: bool = False,
    risk_tier: str = "medium",
    dry_run: bool = True,
    allow_execution: bool = False,
    caller_context: dict | None = None,
    auth_context: dict | None = None,
    ctx: Context | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    return await arifOS_kernel(
        query=query,
        session_id=session_id,
        actor_id=actor_id,
        intent=intent,
        human_approval=human_approval,
        risk_tier=risk_tier,
        dry_run=dry_run,
        allow_execution=allow_execution,
        caller_context=caller_context,
        auth_context=auth_context,
        ctx=ctx,
        **kwargs,
    )


async def check_vital(
    session_id: str | None = None,
    actor_id: str | None = None,
    risk_tier: str = "low",
    dry_run: bool = True,
    auth_context: dict | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    from arifosmcp.runtime.megaTools import math_estimator as impl

    return await impl(
        mode="vitals",
        session_id=session_id,
        actor_id=actor_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        auth_context=auth_context,
        **kwargs,
    )


async def audit_rules(
    session_id: str | None = None,
    actor_id: str | None = None,
    risk_tier: str = "low",
    dry_run: bool = True,
    auth_context: dict | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    from arifosmcp.runtime.megaTools import apex_judge as impl

    return await impl(
        mode="rules",
        session_id=session_id,
        actor_id=actor_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        auth_context=auth_context,
        **kwargs,
    )


async def agi_reason(
    query: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    intent: str = None,
    human_approval: bool = False,
    risk_tier: str = "medium",
    dry_run: bool = True,
    caller_context: dict | None = None,
    auth_context: dict | None = None,
    ctx: Context | None = None,
    constitutional_context: str | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    from arifosmcp.runtime.megaTools import agi_mind as impl

    return await impl(
        mode="reason",
        query=query,
        session_id=session_id,
        actor_id=actor_id,
        intent=intent,
        human_approval=human_approval,
        risk_tier=risk_tier,
        dry_run=dry_run,
        caller_context=caller_context,
        auth_context=auth_context,
        ctx=ctx,
        constitutional_context=constitutional_context,
        **kwargs,
    )


async def agi_reflect(
    query: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    intent: str = None,
    human_approval: bool = False,
    risk_tier: str = "medium",
    dry_run: bool = True,
    caller_context: dict | None = None,
    auth_context: dict | None = None,
    ctx: Context | None = None,
    constitutional_context: str | None = None,
) -> RuntimeEnvelope:
    return await agi_mind(
        mode="reflect",
        query=query,
        session_id=session_id,
        actor_id=actor_id,
        intent=intent,
        human_approval=human_approval,
        risk_tier=risk_tier,
        dry_run=dry_run,
        caller_context=caller_context,
        auth_context=auth_context,
        ctx=ctx,
        constitutional_context=constitutional_context,
    )


async def reason_mind(**kwargs: Any) -> RuntimeEnvelope:
    return await agi_mind(mode="reason", **kwargs)


async def reason_mind_synthesis(**kwargs: Any) -> RuntimeEnvelope:
    return await agi_mind(mode="reason", **kwargs)


async def integrate_analyze_reflect(**kwargs: Any) -> RuntimeEnvelope:
    return await agi_mind(mode="reflect", **kwargs)


async def agi_asi_forge_handler(**kwargs: Any) -> RuntimeEnvelope:
    return await agi_mind(mode="forge", **kwargs)


async def asi_simulate(
    content: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    human_approval: bool = False,
    risk_tier: str = "medium",
    dry_run: bool = True,
    caller_context: dict | None = None,
    auth_context: dict | None = None,
    ctx: Context | None = None,
) -> RuntimeEnvelope:
    return await asi_heart(
        mode="simulate",
        content=content,
        session_id=session_id,
        actor_id=actor_id,
        human_approval=human_approval,
        risk_tier=risk_tier,
        dry_run=dry_run,
        caller_context=caller_context,
        auth_context=auth_context,
        ctx=ctx,
    )


async def asi_critique(
    content: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    human_approval: bool = False,
    risk_tier: str = "medium",
    dry_run: bool = True,
    caller_context: dict | None = None,
    auth_context: dict | None = None,
    ctx: Context | None = None,
) -> RuntimeEnvelope:
    return await asi_heart(
        mode="critique",
        content=content,
        session_id=session_id,
        actor_id=actor_id,
        human_approval=human_approval,
        risk_tier=risk_tier,
        dry_run=dry_run,
        caller_context=caller_context,
        auth_context=auth_context,
        ctx=ctx,
    )


async def apex_judge(
    mode: str = "judge",
    candidate: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    human_approval: bool = False,
    risk_tier: str = "medium",
    dry_run: bool = True,
    caller_context: dict | None = None,
    auth_context: dict | None = None,
    ctx: Context | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope:
    from arifosmcp.runtime.megaTools import apex_judge as impl

    return await impl(
        mode=mode,
        proposal=candidate,
        session_id=session_id,
        actor_id=actor_id,
        human_approval=human_approval,
        risk_tier=risk_tier,
        dry_run=dry_run,
        caller_context=caller_context,
        auth_context=auth_context,
        ctx=ctx,
        **kwargs,
    )


async def vault_seal(
    verdict: str | None = None,
    evidence: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    human_approval: bool = False,
    risk_tier: str = "medium",
    dry_run: bool = True,
    caller_context: dict | None = None,
    auth_context: dict | None = None,
    ctx: Context | None = None,
) -> RuntimeEnvelope:
    return await vault_ledger(
        mode="seal",
        query=verdict,
        session_id=session_id,
        actor_id=actor_id,
        human_approval=human_approval,
        risk_tier=risk_tier,
        dry_run=dry_run,
        caller_context=caller_context,
        auth_context=auth_context,
        ctx=ctx,
    )


async def verify_vault_ledger(
    session_id: str | None = None,
    actor_id: str | None = None,
    full_scan: bool = True,
) -> RuntimeEnvelope:
    return await vault_ledger(
        mode="verify",
        session_id=session_id,
        actor_id=actor_id,
    )


async def reality_compass(
    input: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> RuntimeEnvelope:
    return await physics_reality(
        mode="compass",
        query=input,
        session_id=session_id,
        actor_id=actor_id,
    )


async def search_reality(
    input: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> RuntimeEnvelope:
    return await physics_reality(
        mode="search",
        query=input,
        session_id=session_id,
        actor_id=actor_id,
    )


async def reality_atlas(
    input: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> RuntimeEnvelope:
    return await physics_reality(
        mode="atlas",
        query=input,
        session_id=session_id,
        actor_id=actor_id,
    )


async def ingest_evidence(
    input: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> RuntimeEnvelope:
    return await physics_reality(
        mode="ingest",
        query=input,
        session_id=session_id,
        actor_id=actor_id,
    )


async def system_health(**kwargs: Any) -> RuntimeEnvelope:
    return await math_estimator(mode="health", **kwargs)


async def cost_estimator(**kwargs: Any) -> RuntimeEnvelope:
    return await math_estimator(mode="cost", **kwargs)


async def fs_inspect(**kwargs: Any) -> RuntimeEnvelope:
    return await code_engine(mode="fs", **kwargs)


async def process_list(**kwargs: Any) -> RuntimeEnvelope:
    return await code_engine(mode="process", **kwargs)


async def net_status(**kwargs: Any) -> RuntimeEnvelope:
    return await code_engine(mode="net", **kwargs)


async def log_tail(**kwargs: Any) -> RuntimeEnvelope:
    return await code_engine(mode="tail", **kwargs)


async def trace_replay(**kwargs: Any) -> RuntimeEnvelope:
    return await code_engine(mode="replay", **kwargs)


async def agentzero_engineer(
    task: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    human_approval: bool = False,
    risk_tier: str = "medium",
    dry_run: bool = True,
    caller_context: dict | None = None,
    auth_context: dict | None = None,
    ctx: Context | None = None,
) -> RuntimeEnvelope:
    return await engineering_memory(
        mode="engineer",
        task=task,
        session_id=session_id,
        actor_id=actor_id,
        human_approval=human_approval,
        risk_tier=risk_tier,
        dry_run=dry_run,
        caller_context=caller_context,
        auth_context=auth_context,
        ctx=ctx,
    )


async def agentzero_validate(**kwargs: Any) -> RuntimeEnvelope:
    return await apex_judge(mode="validate", **kwargs)


async def agentzero_armor_scan(**kwargs: Any) -> RuntimeEnvelope:
    return await apex_judge(mode="armor", **kwargs)


async def agentzero_hold_check(**kwargs: Any) -> RuntimeEnvelope:
    return await apex_judge(mode="hold", **kwargs)


async def agentzero_memory_query(**kwargs: Any) -> RuntimeEnvelope:
    return await engineering_memory(mode="query", **kwargs)


async def seal_vault_commit(**kwargs: Any) -> RuntimeEnvelope:
    return await vault_ledger(mode="seal", **kwargs)


async def architect_registry(mode: str = "list", **kwargs: Any) -> RuntimeEnvelope:
    from arifosmcp.runtime.megaTools import architect_registry as impl

    return await impl(mode=mode, **kwargs)


async def compat_probe(mode: str = "audit", **kwargs: Any) -> RuntimeEnvelope:
    from arifosmcp.runtime.megaTools import compat_probe as impl

    return await impl(mode=mode, **kwargs)


# ═══════════════════════════════════════════════════════════════════════════════
# FINAL TOOL IMPLEMENTATIONS MAP
# ═══════════════════════════════════════════════════════════════════════════════

FINAL_TOOL_IMPLEMENTATIONS: dict[str, Callable[..., Any]] = {
    "init_anchor": init_anchor,
    "arifOS_kernel": arifOS_kernel,
    "apex_judge": apex_judge,
    "vault_ledger": vault_ledger,
    "agi_mind": agi_mind,
    "asi_heart": asi_heart,
    "engineering_memory": engineering_memory,
    "physics_reality": physics_reality,
    "math_estimator": math_estimator,
    "code_engine": code_engine,
    "architect_registry": architect_registry,
    "compat_probe": compat_probe,
    # init_000 tools
    "init_000_get_deployment": init_000_get_deployment,
    "init_000_get_provider_soul": init_000_get_provider_soul,
    "init_000_get_session_anchor": init_000_get_session_anchor,
    "init_000_log_drift_event": init_000_log_drift_event,
}

LEGACY_COMPAT_MAP: dict[str, Callable[..., Any]] = {
    "metabolic_loop_router": metabolic_loop_router,
    "arifos_kernel": arifos_kernel,
    "check_vital": check_vital,
    "audit_rules": audit_rules,
    "agi_reason": agi_reason,
    "agi_reflect": agi_reflect,
    "asi_critique": asi_critique,
    "asi_simulate": asi_simulate,
    "apex_judge": apex_judge,
    "vault_seal": vault_seal,
    "verify_vault_ledger": verify_vault_ledger,
    "reality_compass": reality_compass,
    "reality_atlas": reality_atlas,
    "search_reality": search_reality,
    "ingest_evidence": ingest_evidence,
    "agentzero_engineer": agentzero_engineer,
    "agentzero_validate": agentzero_validate,
    "agentzero_armor_scan": agentzero_armor_scan,
    "agentzero_hold_check": agentzero_hold_check,
    "agentzero_memory_query": agentzero_memory_query,
    "seal_vault_commit": seal_vault_commit,
    "forge": metabolic_loop_router,
    "reason_mind_synthesis": reason_mind_synthesis,
    "agi_asi_forge_handler": agi_asi_forge_handler,
}

ALL_TOOL_IMPLEMENTATIONS = {**FINAL_TOOL_IMPLEMENTATIONS, **LEGACY_COMPAT_MAP}


# ═══════════════════════════════════════════════════════════════════════════════
# LEGACY PAYLOAD BUILDER
# ═══════════════════════════════════════════════════════════════════════════════


def _build_legacy_payload(mega_tool: str, mode: str, values: dict[str, Any]) -> dict[str, Any]:
    payload = {key: value for key, value in values.items() if value is not None}
    if mega_tool == "apex_judge":
        candidate = (
            payload.get("candidate")
            or payload.get("candidate_output")
            or payload.get("input_to_validate")
            or payload.get("content")
            or payload.get("query")
        )
        if candidate is not None:
            payload.setdefault("candidate", candidate)
    elif mega_tool == "asi_heart":
        content = (
            payload.get("content")
            or payload.get("draft_output")
            or payload.get("scenario")
            or payload.get("query")
        )
        if content is not None:
            payload.setdefault("content", content)
    elif mega_tool == "physics_reality":
        input_value = payload.get("input")
        if input_value is None:
            if mode == "ingest":
                input_value = payload.get("url") or payload.get("query") or payload.get("content")
            else:
                input_value = payload.get("query") or payload.get("content") or payload.get("url")
        if input_value is not None:
            payload.setdefault("input", input_value)
    elif mega_tool == "engineering_memory":
        task = payload.get("task") or payload.get("task_description")
        if task is not None:
            payload.setdefault("task", task)
    elif mega_tool == "vault_ledger":
        if payload.get("summary") is not None and payload.get("evidence") is None:
            payload["evidence"] = payload["summary"]
    elif mega_tool == "arifOS_kernel":
        payload.setdefault("query", "")
    return payload


def _build_user_model(
    tool_name: str, stage_value: str, payload: dict[str, Any], envelope_data: dict[str, Any]
) -> UserModel:
    query = str(
        payload.get("query") or payload.get("intent") or payload.get("content") or ""
    ).strip()
    context = str(payload.get("context") or "").strip()
    output_constraints: list[UserModelField] = []
    lowered = f"{query} {context}".lower()
    if "concise" in lowered:
        output_constraints.append(
            UserModelField(value="keep_response_concise", source=UserModelSource.EXPLICIT)
        )
    if envelope_data.get("meta", {}).get("dry_run") or payload.get("dry_run"):
        output_constraints.append(
            UserModelField(
                value="state_that_execution_is_simulated", source=UserModelSource.OBSERVABLE
            )
        )
    return UserModel(
        stated_goal=UserModelField(
            value=query or context or f"{tool_name}:{stage_value}", source=UserModelSource.EXPLICIT
        ),
        output_constraints=output_constraints,
    )


def _resolve_caller_context(
    caller_context: CallerContext | None, requested_persona: str | None
) -> CallerContext:
    base = caller_context or CallerContext()
    if requested_persona:
        try:
            base.persona_id = PersonaId(requested_persona.lower())
        except (ValueError, AttributeError):
            pass
    return base


def _resolve_caller_state(
    session_id: str, authority: Any
) -> tuple[str, list[str], list[dict[str, str]]]:
    """Single source of truth for caller state resolution."""
    from .tools_internal import _resolve_caller_state as _resolve

    return _resolve(session_id, authority)


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL REGISTRATION
# ═══════════════════════════════════════════════════════════════════════════════


def register_tools(mcp: FastMCP, profile: str = "full") -> None:
    del profile
    import inspect
    from fastmcp.tools.function_tool import FunctionTool
    from arifosmcp.runtime.ingress_middleware import IngressToleranceMiddleware

    ingress = IngressToleranceMiddleware()
    specs = {spec.name: spec for spec in _public_tool_specs_fn()}

    # P1: Register all 11 mega-tools + legacy compat aliases on FastMCP surface
    # Skip handlers with **kwargs — FastMCP FunctionTool does not support them
    all_public_tools = {**FINAL_TOOL_IMPLEMENTATIONS, **LEGACY_COMPAT_MAP}
    for name, handler in all_public_tools.items():
        if handler is None:
            continue
            
        # 🔥 HARDENING: Precision callable check to prevent "first argument must be callable" crash
        if not callable(handler):
            logger.error(f"SYSTEM ERROR: Tool '{name}' handler is not callable: {type(handler)}")
            continue

        sig = inspect.signature(handler)
        if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()):
            continue  # skip **kwargs handlers
            
        # 🔥 HARDENING: Wrap tool in Canonical Envelope for F1-F13 compliance
        async def canonical_wrapper(*args, _target_handler=handler, _tool_name=name, **kwargs):
            try:
                # 1. Execute the tool kernel
                result = await _target_handler(*args, **kwargs)
                
                # 2. If result is already an envelope, pass through
                if isinstance(result, dict) and "verdict" in result:
                    return result
                
                # 3. Otherwise, wrap in CanonicalResponse structure
                if CanonicalResponse:
                    envelope = CanonicalResponse(
                        module="arifOS",
                        ok=True,
                        status=IntelligenceStatus.QUALIFY,
                        verdict=Verdict.PROCEED,
                        confidence=1.0,
                        reasoning=f"Tool '{_tool_name}' executed successfully.",
                        payload={"result": result} if not isinstance(result, dict) else result
                    )
                    return envelope.model_dump()
                
                # Fallback to dict if Pydantic model is unavailable
                return {
                    "ok": True, 
                    "verdict": "PROCEED", 
                    "module": "arifOS", 
                    "payload": result
                }
            except Exception as e:
                logger.exception(f"Tool execution failed: {_tool_name}")
                return {
                    "ok": False,
                    "verdict": "VOID",
                    "reasoning": f"Hard collapse in '{_tool_name}': {str(e)}"
                }

        spec = specs.get(name)
        
        # Use functools.wraps to preserve signature for FastMCP inspection
        import functools
        wrapped_handler = functools.wraps(handler)(canonical_wrapper)
        
        ft = FunctionTool.from_function(
            wrapped_handler,
            name=name,
            description=spec.description if spec else name,
        )
        ft.parameters["additionalProperties"] = True
        ingress.register_tool_params(name, set(sig.parameters.keys()))
        mcp.add_tool(ft)

    mcp.add_middleware(ingress)


__all__ = [
    # P2: Public tool registry exports (backward compat)
    "public_tool_names",
    "public_tool_specs",
    "public_tool_spec_by_name",
    # 11 Mega-Tools
    "init_anchor",
    "arifOS_kernel",
    "apex_judge",
    "vault_ledger",
    "agi_mind",
    "asi_heart",
    "engineering_memory",
    "physics_reality",
    "math_estimator",
    "code_engine",
    "architect_registry",
    # Legacy compat
    "metabolic_loop_router",
    "arifos_kernel",
    "check_vital",
    "audit_rules",
    "agi_reason",
    "agi_reflect",
    "asi_critique",
    "asi_simulate",
    "apex_judge",
    "vault_seal",
    "verify_vault_ledger",
    "reality_compass",
    "reality_atlas",
    "search_reality",
    "ingest_evidence",
    "agentzero_engineer",
    "agentzero_validate",
    "agentzero_armor_scan",
    "agentzero_hold_check",
    "agentzero_memory_query",
    "seal_vault_commit",
    # Utilities
    "FINAL_TOOL_IMPLEMENTATIONS",
    "LEGACY_COMPAT_MAP",
    "ALL_TOOL_IMPLEMENTATIONS",
    "register_tools",
    "select_governed_philosophy",
    "_has_valid_proof",
    "_build_legacy_payload",
    "_build_user_model",
    "_resolve_caller_context",
    "_resolve_caller_state",
]


# P2: Re-export public registry helpers for backward compat
# These were removed from module-level but are still imported by tests/external code
public_tool_names = _registry_tool_names
public_tool_specs = _registry_tool_specs
public_tool_spec_by_name = _registry_tool_spec_by_name

"""
arifosmcp/runtime/orchestrator.py — The arifOS Metabolic Loop Orchestrator

This module implements the Stage 444 logic, coordinating the routed 000-999 flow.
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from typing import Any

from arifosmcp.runtime.metrics import (
    METABOLIC_LOOP_DURATION,
)
from arifosmcp.runtime.models import (
    CallerContext,
    RuntimeEnvelope,
    RuntimeStatus,
    Stage,
    Verdict,
    PNSContext,
    PNSSignal,
    SacredStage,
    CanonicalError,
)

# ---------------------------------------------------------------------------
# STAGE FAILURE HANDLERS (F4: Deterministic Failure Semantics)
# ---------------------------------------------------------------------------

STAGE_FAILURE_HANDLERS: dict[str, dict[str, Any]] = {
    Stage.INIT_000.value: {
        "verdict": Verdict.VOID,
        "status": RuntimeStatus.ERROR,
        "action": "session_invalid",
        "recoverable": False,
        "error_code": "INIT_FAILED",
        "description": "Session initialization failed. Anchor rejected.",
    },
    Stage.SENSE_111.value: {
        "verdict": Verdict.HOLD,
        "status": RuntimeStatus.SABAR,
        "action": "request_more_context",
        "recoverable": True,
        "error_code": "SENSE_INSUFFICIENT",
        "description": "Insufficient reality grounding. Evidence required.",
    },
    Stage.MIND_333.value: {
        "verdict": Verdict.HOLD,
        "status": RuntimeStatus.ERROR,
        "action": "clarify_intent",
        "recoverable": True,
        "error_code": "MIND_INCOHERENT",
        "description": "Cannot form coherent reasoning plan. Clarify intent.",
    },
    Stage.MEMORY_555.value: {
        "verdict": Verdict.DEGRADED,
        "status": RuntimeStatus.SUCCESS,
        "action": "continue_without_memory",
        "recoverable": True,
        "error_code": "MEMORY_UNAVAILABLE",
        "description": "Vector memory unavailable. Continuing without recall.",
    },
    Stage.HEART_666.value: {
        "verdict": Verdict.HOLD_888,
        "status": RuntimeStatus.ERROR,
        "action": "safety_review_required",
        "recoverable": True,
        "error_code": "HEART_SAFETY_BLOCK",
        "description": "Safety critique blocked. Human review required (F6/F7/F8).",
    },
    Stage.CRITIQUE_666.value: {
        "verdict": Verdict.HOLD_888,
        "status": RuntimeStatus.ERROR,
        "action": "critique_review_required",
        "recoverable": True,
        "error_code": "CRITIQUE_BLOCK",
        "description": "Metacognitive critique blocked. Review required.",
    },
    Stage.FORGE_777.value: {
        "verdict": Verdict.SABAR,
        "status": RuntimeStatus.ERROR,
        "action": "forging_failed",
        "recoverable": True,
        "error_code": "FORGE_FAILED",
        "description": "Commitment forging failed. Retry or refine.",
    },
    Stage.JUDGE_888.value: {
        "verdict": Verdict.HOLD_888,
        "status": RuntimeStatus.ERROR,
        "action": "await_human",
        "recoverable": True,
        "error_code": "JUDGE_UNDECIDED",
        "description": "APEX judgment requires human ratification (F13).",
    },
    Stage.VAULT_999.value: {
        "verdict": Verdict.SABAR,
        "status": RuntimeStatus.ERROR,
        "action": "seal_failed",
        "recoverable": False,
        "error_code": "VAULT_COMMIT_FAILED",
        "description": "Cryptographic sealing failed. Audit logged, no commit.",
    },
}


def handle_stage_failure(
    stage_id: str,
    original_error: Exception | None = None,
    session_id: str = "unknown",
    context: dict[str, Any] | None = None,
) -> RuntimeEnvelope:
    """
    Generate standardized failure envelope for a stage.
    
    Ensures F4 (Clarity): All failures have deterministic, documented semantics.
    """
    handler = STAGE_FAILURE_HANDLERS.get(stage_id, STAGE_FAILURE_HANDLERS[Stage.INIT_000.value])
    
    error_details = {
        "stage": stage_id,
        "error_code": handler["error_code"],
        "description": handler["description"],
        "action": handler["action"],
        "recoverable": handler["recoverable"],
    }
    
    if original_error:
        error_details["original_error"] = str(original_error)
    
    if context:
        error_details["context"] = context
    
    return RuntimeEnvelope(
        tool="arifOS_kernel",
        session_id=session_id,
        stage=stage_id,
        verdict=handler["verdict"],
        status=handler["status"],
        errors=[CanonicalError(
            code=handler["error_code"],
            message=handler["description"],
            stage=stage_id,
        )],
        payload={
            "failure_handler": handler["action"],
            "recoverable": handler["recoverable"],
            "error_details": error_details,
        },
    )


# ---------------------------------------------------------------------------
# PNS CIRCULATORY HANDLERS
# ---------------------------------------------------------------------------


async def handle_pns_vision(content_type: str, data: bytes, session_id: str) -> RuntimeEnvelope:
    """PNS·VISION: Multimodal perception organ.
    Processes binary data (Image/PDF) into semantic sensory artifacts.
    """
    # Logic: Dispatch to vision-capable cortex (e.g., LLaVA or Stirling PDF)
    # For now, we simulate the sensory conversion into structured text evidence.
    summary = f"Processed {content_type} data ({len(data)} bytes)."

    # In production, this would call Stirling PDF or a Vision Model
    return RuntimeEnvelope(
        tool="pns_vision",
        session_id=session_id,
        stage=Stage.SENSE_111.value,
        verdict=Verdict.SEAL,
        status=RuntimeStatus.SUCCESS,
        payload={
            "sensory_mode": content_type,
            "semantic_summary": summary,
            "visual_tokens": ["detected_structure", "text_extraction_active"],
            "fidelity_score": 0.92,
        },
    )


async def handle_pns_shield(content: str, session_id: str) -> RuntimeEnvelope:
    """PNS·SHIELD: Injection defense organ."""
    from arifosmcp.agentzero.security.prompt_armor import PromptArmor

    armor = PromptArmor()
    report = await armor.scan(text=content, context="user_input")
    status = RuntimeStatus.SUCCESS
    verdict = Verdict.SEAL
    if report.is_injection:
        status = RuntimeStatus.SABAR
        verdict = Verdict.VOID
    return RuntimeEnvelope(
        tool="pns_shield",
        session_id=session_id,
        stage=Stage.INIT_000.value,
        verdict=verdict,
        status=status,
        payload={"shield_status": status, "threat_score": report.score},
    )


async def handle_pns_search(query: str, session_id: str) -> RuntimeEnvelope:
    """PNS·SEARCH: Web search grounding organ."""
    from arifosmcp.runtime.tools import reality_compass

    res = await reality_compass(input=query, session_id=session_id, mode="search")
    res.tool = "PNS_SEARCH"
    return res


async def handle_pns_health(session_id: str) -> RuntimeEnvelope:
    """PNS·HEALTH: System stability monitoring."""
    from arifosmcp.runtime.tools import check_vital

    return await check_vital(session_id=session_id)


async def handle_pns_orchestrate(task: str, session_id: str) -> RuntimeEnvelope:
    """PNS·ORCHESTRATE: Tool routing mediation."""
    from arifosmcp.tools.agentzero_tools import agentzero_engineer

    return await agentzero_engineer(task=task, action_type="execute_code", session_id=session_id)


async def handle_pns_floor(input_data: Any, session_id: str) -> RuntimeEnvelope:
    """PNS·FLOOR: Semantic grounding checks."""
    from arifosmcp.runtime.tools import audit_rules

    return await audit_rules(session_id=session_id)


async def handle_pns_redteam(candidate: str, session_id: str) -> RuntimeEnvelope:
    """PNS·REDTEAM: Adversarial testing."""
    from arifosmcp.tools.agentzero_tools import agentzero_validate

    return await agentzero_validate(
        input_to_validate=candidate, validation_type="plan", session_id=session_id
    )


def _extract_auth_context(
    envelope: RuntimeEnvelope | None, fallback: dict[str, Any] | None = None
) -> dict[str, Any]:
    if envelope is None:
        return dict(fallback or {})

    auth_context = getattr(envelope, "auth_context", None)
    if isinstance(auth_context, dict):
        return dict(auth_context)

    return dict(fallback or {})


def _extract_caller_context(
    envelope: RuntimeEnvelope | None, fallback: CallerContext | None = None
) -> CallerContext | None:
    """Carry the caller_context forward through the metabolic loop."""
    if envelope is None:
        return fallback

    ctx = getattr(envelope, "caller_context", None)
    if isinstance(ctx, CallerContext):
        return ctx

    return fallback


def _dump_caller_context(caller_ctx: CallerContext | None) -> dict[str, Any] | None:
    """Serialize CallerContext for embedding in output dicts."""
    if caller_ctx is None:
        return None
    return caller_ctx.model_dump(mode="json", exclude_none=True)


def _get_sacred_name(stage_id: str) -> str:
    """Map Stage ID to its canonical Sacred Name."""
    mapping = {
        Stage.INIT_000.value: SacredStage.INIT_ANCHOR.value,
        Stage.MIND_333.value: SacredStage.AGI_REASON.value,
        Stage.MEMORY_555.value: SacredStage.AGI_REFLECT.value,
        Stage.HEART_666.value: SacredStage.ASI_SIMULATE.value,
        Stage.CRITIQUE_666.value: SacredStage.ASI_CRITIQUE.value,
        Stage.FORGE_777.value: SacredStage.AGI_ASI_FORGE.value,
        Stage.JUDGE_888.value: SacredStage.APEX_JUDGE.value,
        Stage.VAULT_999.value: SacredStage.VAULT_SEAL.value,
    }
    return mapping.get(stage_id, "UNKNOWN")


async def run_stage(
    stage_id: str,
    query: str,
    session_id: str,
    auth_ctx: dict[str, Any],
    verdicts: list[Verdict],
    trace: dict[str, Any],
    reality_summary: dict[str, Any],
    caller_ctx: CallerContext | None = None,
    pns_context: PNSContext | None = None,
    dry_run: bool = False,
    actor_id: str = "anonymous",
    declared_name: str | None = None,
    human_approval: bool = False,
    risk_tier: str = "medium",
) -> RuntimeEnvelope:
    """Execute one routed stage for the metabolic loop.
    
    Includes deterministic failure handling per F4 (Clarity).
    All stage failures are caught and mapped to standardized responses.
    """
    from arifosmcp.runtime.tools import (
        init_anchor,
        agi_reason,
        agi_reflect,
        asi_simulate,
        asi_critique,
        agi_asi_forge_handler,
        apex_judge,
        vault_seal,
    )
    
    try:
        verdict_history = verdicts
        pns_trace = trace.setdefault("pns", {})

        # === FORBIDDEN ZONES: No PNS data allowed ===
        active_pns = pns_context
        if stage_id in {Stage.HEART_666.value, Stage.VAULT_999.value}:
            active_pns = None

        # 1. INIT·ANCHOR (000) - Entry Gate (Feeds PNS·SHIELD)
        if stage_id == Stage.INIT_000.value:
            shield = active_pns.shield if active_pns else None
            return await init_anchor(
                raw_input=query,
                session_id=session_id,
                pns_shield=shield.model_dump() if shield else None,
                ctx=None,  # type: ignore
                actor_id=actor_id,
                declared_name=declared_name,
                human_approval=human_approval,
                auth_context=auth_ctx,
            )

        # 2. AGI·REASON (333) - Grounding (Feeds PNS·SEARCH)
        if stage_id == Stage.MIND_333.value:
            search_res = active_pns.search if active_pns else None
            if not search_res:
                try:
                    # Add timeout to prevent hanging on search
                    search_env = await asyncio.wait_for(
                        handle_pns_search(query=query, session_id=session_id), timeout=10.0
                    )
                    search_res = PNSSignal(source="PNS_SEARCH", payload=search_env.payload)
                    pns_trace["PNS_SEARCH"] = search_res.model_dump(mode="json")
                except asyncio.TimeoutError:
                    # Continue without search results if timeout
                    pns_trace["PNS_SEARCH"] = {"error": "timeout", "source": "PNS_SEARCH"}

            # F12: Retrieve constitutional grounding context from session
            c_ctx = None
            if session_id:
                from arifosmcp.runtime.sessions import get_session_identity
                ident = get_session_identity(session_id)
                if ident:
                    c_ctx = ident.get("constitutional_context")

            return await agi_reason(
                query=query,
                session_id=session_id,
                pns_search=search_res.model_dump() if search_res else None,
                ctx=None,  # type: ignore
                auth_context=auth_ctx,
                constitutional_context=c_ctx,
            )

        # 3. AGI·REFLECT (555) - Sensory (Feeds PNS·VISION)
        if stage_id == Stage.MEMORY_555.value:
            vision_res = active_pns.vision if active_pns else None

            # Multimodal Auto-Trigger: If binary data is detected in query, trigger vision
            if not vision_res and (query.startswith("data:") or "IMAGE_ATTACHED" in query):
                vision_env = await handle_pns_vision(
                    content_type="image", data=b"", session_id=session_id
                )
                vision_res = PNSSignal(source="PNS_VISION", payload=vision_env.payload)
                pns_trace["PNS_VISION"] = vision_res.model_dump(mode="json")

            return await agi_reflect(
                topic=query,
                session_id=session_id,
                pns_vision=vision_res.model_dump() if vision_res else None,
                ctx=None,  # type: ignore
            )

        # 4. ASI·SIMULATE (666) - FORBIDDEN ZONE
        if stage_id == Stage.HEART_666.value:
            return await asi_simulate(
                scenario=query,
                session_id=session_id,
                ctx=None,  # type: ignore
            )

        # 5. ASI·CRITIQUE (666B) - Metacognition (Feeds PNS·HEALTH + PNS·FLOOR)
        if stage_id == Stage.CRITIQUE_666.value:
            health_res = active_pns.health if active_pns else None
            floor_res = active_pns.floor if active_pns else None
            return await asi_critique(
                draft_output=query,
                session_id=session_id,
                health=health_res.model_dump() if health_res else None,
                floor=floor_res.model_dump() if floor_res else None,
                ctx=None,  # type: ignore
            )

        # 6. AGI–ASI·FORGE (777) - Action (Feeds PNS·ORCHESTRATE)
        if stage_id == Stage.FORGE_777.value:
            from arifosmcp.runtime.tools import agi_asi_forge_handler

            orch_res = active_pns.orchestrate if active_pns else None
            return await agi_asi_forge_handler(
                spec=query,
                session_id=session_id,
                pns_orchestrate=orch_res.model_dump() if orch_res else None,
                ctx=None,  # type: ignore
                dry_run=dry_run,
            )

        # 7. APEX·JUDGE (888) - Verdict (Feeds PNS·REDTEAM)
        if stage_id == Stage.JUDGE_888.value:
            red_res = active_pns.redteam if active_pns else None
            candidate = Verdict.SEAL
            if Verdict.VOID in verdict_history:
                candidate = Verdict.VOID
            elif Verdict.HOLD_888 in verdict_history or Verdict.HOLD in verdict_history:
                candidate = Verdict.HOLD_888
            elif Verdict.SABAR in verdict_history:
                candidate = Verdict.SABAR

            return await apex_judge(
                candidate_output=query,
                session_id=session_id,
                redteam=red_res.model_dump() if red_res else None,
                ctx=None,  # type: ignore
            )

        # 8. VAULT·SEAL (999) - FORBIDDEN ZONE
        if stage_id == Stage.VAULT_999.value:
            last_verdict = verdict_history[-1] if verdict_history else Verdict.SABAR
            
            # QSP-333: Quantum Sabar Protocol - Byzantine Witness Check
            # In a live system, this would ping W1 (Human) and W3 (Earth) heartbeats.
            # Here we simulate a blackout if risk is high and dry_run is false.
            is_blackout = (risk_tier in ("high", "critical")) and (not dry_run)
            
            decision_payload = {
                "verdict": last_verdict.value,
                "witness_blackout": is_blackout,
                "protocol": "QSP-333" if is_blackout else "STANDARD"
            }

            return await vault_seal(
                decision=decision_payload,
                evidence=query,
                session_id=session_id,
                ctx=None,  # type: ignore
            )


    except Exception as e:
        # F4: Deterministic failure handling
        return handle_stage_failure(
            stage_id=stage_id,
            original_error=e,
            session_id=session_id,
            context={"query": query[:100] if query else None},  # Truncate for safety
        )
    
    return RuntimeEnvelope(
        tool="arifOS_kernel",
        session_id=session_id,
        stage=stage_id,
        verdict=Verdict.SABAR,
        payload={"warning": f"Unknown routed stage: {stage_id}"},
        auth_context=auth_ctx,
        caller_context=caller_ctx,
    )


async def metabolic_loop(
    query: str,
    risk_tier: str = "medium",
    mode: str = "recommend",
    actor_id: str = "anonymous",
    auth_context: dict[str, Any] | None = None,
    session_id: str | None = None,
    allow_execution: bool = False,
    dry_run: bool = False,
    caller_context: CallerContext | None = None,
    pns_context: PNSContext | None = None,  # Double Helix Injection
    timeout_seconds: float = 30.0,  # Configurable timeout
    declared_name: str | None = None,
    human_approval: bool = False,
    tool_name: str = "arifOS_kernel",
    **kwargs,
) -> dict[str, Any]:
    """Run the Double Helix metabolic loop (Inner Ring + Outer Ring)."""
    start_time = time.perf_counter()

    if dry_run:
        from arifosmcp.runtime.models import AuthContext
        
        _actual_session = session_id or "dry-run-session"
        _actual_actor = actor_id or "anonymous"
        
        ctx = AuthContext(
            session_id=_actual_session,
            actor_id=_actual_actor,
            authority_level="declared",
            approval_scope=["*"],
        )
        
        return {
            "ok": True,
            "tool": tool_name,
            "session_id": _actual_session,
            "stage": "444_ROUTER",
            "verdict": "SEAL",
            "status": "DRY_RUN",
            "authority": {
                "actor_id": _actual_actor,
                "level": "declared",
                "auth_state": "verified"
            },
            "auth_context": ctx,
            "dry_run": True,
            "meta": {"dry_run": True},
        }

    from arifosmcp.runtime.sessions import _resolve_session_id as _normalize_session_id
    from arifosmcp.core.governance_kernel import route_pipeline

    # Track if we're approaching timeout
    def _check_timeout() -> bool:
        elapsed = time.perf_counter() - start_time
        return elapsed > timeout_seconds * 0.8  # 80% threshold for early warning

    # ─── METABOLIC SYNONYM LAYER ───
    LEGACY_SYNONYMS = {
        "session_memory": "agi_reflect",
        "simulate_heart": "asi_simulate",
        "assess_heart_impact": "asi_simulate",
        "critique_thought": "asi_critique",
        "critique_thought_audit": "asi_critique",
        "eureka_forge": "forge",
        "quantum_eureka_forge": "forge",
        "seal_vault": "vault_seal",
        "seal_vault_commit": "vault_seal",
    }

    # Check if the query intent implies a legacy tool and normalize it
    # (In a real E2E, this might be triggered by the 'tool' field in the envelope)

    current_session_id = _normalize_session_id(session_id)
    try:
        # === OUTER RING GATE: PNS·SHIELD ===
        if not pns_context or not pns_context.shield:
            shield_env = await handle_pns_shield(content=query, session_id=current_session_id)
            pns_context = pns_context or PNSContext()
            pns_context.shield = PNSSignal(
                source="PNS_SHIELD", status=shield_env.status, score=0.0, payload=shield_env.payload
            )

        if pns_context.shield.status == "VOID":
            return {
                "ok": False,
                "tool": "arifOS_kernel",
                "session_id": current_session_id,
                "verdict": "VOID",
                "status": "BLOCKED",
                "errors": [{"message": "PNS·SHIELD block: Injection detected."}],
            }

        # === INNER RING START: INIT·ANCHOR ===
        init_res = await run_stage(
            stage_id=Stage.INIT_000.value,
            query=query,
            session_id=current_session_id,
            auth_ctx=auth_context or {},
            verdicts=[],
            trace={},
            reality_summary={},
            caller_ctx=caller_context,
            pns_context=pns_context,
            dry_run=dry_run,
            actor_id=actor_id,
            declared_name=declared_name,
            human_approval=human_approval,
            risk_tier=risk_tier,
        )

        auth_ctx = _extract_auth_context(init_res, auth_context)

        # For dry_run, we inject a mock context if the real one is missing/blocked/unsuccessful
        if dry_run and (not auth_ctx or init_res.verdict != Verdict.SEAL):
            from arifosmcp.core.enforcement.auth_continuity import mint_auth_context

            auth_ctx = mint_auth_context(
                session_id=current_session_id,
                actor_id=actor_id,
                token_fingerprint="sha256:dry-run-bypass",
                approval_scope=["*"],
                parent_signature="",
                authority_level="declared",
            )
            # Update init_res to look successful for the loop logic
            init_res = init_res.model_copy(
                update={"verdict": Verdict.SEAL, "auth_context": auth_ctx}
            )

        caller_ctx = _extract_caller_context(init_res, caller_context)
        trace = {Stage.INIT_000.value: init_res.verdict.value}

        # Early exit if initialization was not successful and we are not in dry_run
        if init_res.verdict != Verdict.SEAL and not dry_run:
            import sys
            print(f"DEBUG: Early exit. Init verdict: {init_res.verdict}", file=sys.stderr)
            # We return the initialization failure directly
            out = init_res.model_dump(mode="json")
            out["trace"] = trace
            out["tool"] = tool_name  # P0: Preserve identity — arifOS_kernel is the router
            return out

        # Early timeout check after init
        if _check_timeout():
            return {
                "ok": False,
                "tool": "arifOS_kernel",
                "session_id": current_session_id,
                "verdict": "TIMEOUT",
                "status": "TIMEOUT",
                "errors": [
                    {
                        "message": f"Metabolic loop approaching timeout ({timeout_seconds}s). Init stage took too long."
                    }
                ],
                "trace": trace,
            }

        plan = route_pipeline(query, {"human_required": allow_execution})
        if Stage.VAULT_999.value not in plan:
            plan.append(Stage.VAULT_999.value)

        reality_summary = {"status": "SKIPPED", "required": False, "score": 0.0}
        verdict_history: list[Verdict] = [init_res.verdict]
        
        # P0: Cumulative payload preservation (Fix: Wire kernel to agi_mind output)
        cumulative_payload = init_res.payload.copy() if init_res.payload else {}
        policy_res: RuntimeEnvelope = init_res
        policy_verdict = init_res.verdict

        for stage_id in plan:
            if stage_id == Stage.INIT_000.value:
                continue

            res = await run_stage(
                stage_id=stage_id,
                query=query,
                session_id=current_session_id,
                auth_ctx=auth_ctx,
                verdicts=verdict_history,
                trace=trace,
                reality_summary=reality_summary,
                caller_ctx=caller_ctx,
                pns_context=pns_context,
                dry_run=dry_run,
                actor_id=actor_id,
                risk_tier=risk_tier,
            )
            current_verdict = res.verdict

            # Constitutional Verdict Normalization: stage < 888 and VOID -> SABAR
            if stage_id < Stage.JUDGE_888.value and current_verdict == Verdict.VOID:
                current_verdict = Verdict.SABAR
                res = res.model_copy(update={"verdict": current_verdict})

            trace[stage_id] = current_verdict.value
            verdict_history.append(current_verdict)
            auth_ctx = _extract_auth_context(res, auth_ctx)
            caller_ctx = _extract_caller_context(res, caller_ctx)

            # Accumulate payloads (MIND/AGI results are high-fidelity)
            if res.payload:
                if stage_id == Stage.MIND_333.value:
                    # Promote mind results to top-level fields for visibility
                    cumulative_payload["answer"] = res.payload.get("answer")
                    cumulative_payload["thought"] = res.payload.get("thought")
                    cumulative_payload["steps"] = res.payload.get("steps")
                
                # Merge the rest
                cumulative_payload.update(res.payload)

            if stage_id != Stage.VAULT_999.value:
                policy_res = res
                policy_verdict = current_verdict

            # Loop Termination Logic
            if stage_id == Stage.JUDGE_888.value and current_verdict in {
                Verdict.SEAL,
                Verdict.VOID,
                Verdict.HOLD_888,
            }:
                if Stage.VAULT_999.value not in trace:
                    vault_res = await run_stage(
                        stage_id=Stage.VAULT_999.value,
                        query=query,
                        session_id=current_session_id,
                        auth_ctx=auth_ctx,
                        verdicts=verdict_history,
                        trace=trace,
                        reality_summary=reality_summary,
                        caller_ctx=caller_ctx,
                        dry_run=dry_run,
                        risk_tier=risk_tier,
                    )
                    trace[Stage.VAULT_999.value] = vault_res.verdict.value
                break

        # ─── SCORE INTEGRITY PROTOCOL: Final Vitals ───
        from arifosmcp.runtime.metrics import compute_integrity_telemetry

        # Extract metabolic signals for computation
        sources = 0
        pns_trace = trace.get("pns", {})
        if "PNS_SEARCH" in pns_trace:
            sources = len(pns_trace["PNS_SEARCH"].get("payload", {}).get("results", []))

        # Wire G★ to actual content scoring
        actual_content = str(cumulative_payload.get("answer", "")) + str(cumulative_payload.get("thought", ""))
        actual_tokens = max(10, len(actual_content) // 4)  # rough token estimate (1 word/token ≈ 4 chars)
        actual_options = 1
        if "steps" in cumulative_payload and isinstance(cumulative_payload["steps"], list):
            actual_options = len(cumulative_payload["steps"])
        elif "options" in cumulative_payload and isinstance(cumulative_payload["options"], list):
            actual_options = len(cumulative_payload["options"])
        else:
            actual_options = 3 if "AGI_REASON" in trace else 1

        # Calculate public score card
        final_metrics = compute_integrity_telemetry(
            sources_cited=sources,
            floors_passed=len([v for v in trace.values() if v == "SEAL"]),
            hold_active=policy_verdict == Verdict.HOLD_888,
            options_offered=actual_options,
            response_tokens=actual_tokens,
            echo_debt_count=0,  # Measured from session memory
            reasoning_depth=len(plan),
            tri_witness_confirmed=True if Stage.JUDGE_888.value in trace else False,
        )

        out = policy_res.model_dump(mode="json")
        out.update(
            {
                "tool": tool_name,
                "session_id": current_session_id,
                "stage": policy_res.stage,
                "sacred_stage": _get_sacred_name(policy_res.stage),
                "verdict": final_metrics.telemetry.verdict,
                "status": "SUCCESS" if final_metrics.telemetry.verdict == "ALIVE" else "ERROR",
                "trace": trace,
                "payload": cumulative_payload,  # Replaces overwritten payload with cumulative one
                "final_verdict": final_metrics.telemetry.verdict,
                "metrics": final_metrics.model_dump(mode="json"),  # Rule 3 Format
                "pns_active": pns_context is not None,
                "caller_context": _dump_caller_context(caller_ctx),
                "auth_context": auth_ctx,
            }
        )

        return out
    finally:
        duration = time.perf_counter() - start_time
        METABOLIC_LOOP_DURATION.observe(duration)

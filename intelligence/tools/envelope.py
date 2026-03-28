"""
Unified Tool Output Envelope — MGI (Machine, Governance, Intelligence)

This module enforces the 3-layer GovernedResponse envelope on all tools.
Ensures F3 Quad-Witness compliance by structuring output through:
- Machine Layer: Status, issue labels, physical state
- Governance Layer: Verdict, authority, trace
- Intelligence Layer: Metrics, exploration/entropy/eureka state
"""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any

from arifosmcp.core.ontology import OntologyRegistry
from arifosmcp.runtime.models import (
    CallerContext,
    CanonicalAuthority,
    CanonicalError,
    CanonicalMeta,
    CanonicalMetrics,
    EntropyState,
    EurekaState,
    ExplorationState,
    IntelligenceStage,
    MachineIssueLabel,
    MachineState,
    RiskClass,
    RuntimeEnvelope,
    RuntimeStatus,
    Verdict,
)


def unified_tool_output(
    tool_name: str | None = None,
    stage: str = "444_ROUTER",
    default_verdict: Verdict = Verdict.SEAL,
) -> Callable:
    """
    Decorator that forces tool output into RuntimeEnvelope (MGI structure).

    Args:
        tool_name: Name of the tool (auto-detected from function name if None)
        stage: Metabolic stage identifier (default: 444_ROUTER for tools)
        default_verdict: Default verdict for successful execution

    Returns:
        Decorated function that always returns RuntimeEnvelope
    """

    def decorator(func: Callable) -> Callable:
        import inspect

        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs) -> RuntimeEnvelope:
                # Auto-detect tool name from function
                detected_name = tool_name or func.__name__

                # Extract caller_context from kwargs if present
                caller_ctx = kwargs.get("caller_context")
                auth_ctx = kwargs.get("auth_context", {}) or {}
                session_id = kwargs.get("session_id")

                try:
                    # Execute the actual tool function
                    raw_result = await func(*args, **kwargs)
                    return _finalize_envelope(
                        raw_result,
                        detected_name,
                        stage,
                        default_verdict,
                        session_id,
                        auth_ctx,
                        caller_ctx,
                    )
                except Exception as e:
                    return _error_envelope(
                        e, detected_name, session_id, stage, auth_ctx, caller_ctx
                    )
        else:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> RuntimeEnvelope:
                # Auto-detect tool name from function
                detected_name = tool_name or func.__name__

                # Extract caller_context from kwargs if present
                caller_ctx = kwargs.get("caller_context")
                auth_ctx = kwargs.get("auth_context", {}) or {}
                session_id = kwargs.get("session_id")

                try:
                    # Execute the actual tool function
                    raw_result = func(*args, **kwargs)
                    return _finalize_envelope(
                        raw_result,
                        detected_name,
                        stage,
                        default_verdict,
                        session_id,
                        auth_ctx,
                        caller_ctx,
                    )
                except Exception as e:
                    return _error_envelope(
                        e, detected_name, session_id, stage, auth_ctx, caller_ctx
                    )

        return wrapper

    return decorator


def _finalize_envelope(
    raw_result: Any,
    detected_name: str,
    stage: str,
    default_verdict: Verdict,
    session_id: str | None,
    auth_ctx: dict[str, Any],
    caller_ctx: Any,
) -> RuntimeEnvelope:
    # If already a RuntimeEnvelope, return as-is
    if isinstance(raw_result, RuntimeEnvelope):
        return raw_result

    # If dict with envelope-like structure, unwrap and re-wrap properly
    if isinstance(raw_result, dict):
        # Extract verdict if provided by tool
        verdict_str = raw_result.get("verdict", default_verdict.value)
        verdict = (
            Verdict(verdict_str) if isinstance(verdict_str, str) else default_verdict
        )

        # Map ok/status to machine state
        ok = raw_result.get("ok", True)
        status_str = raw_result.get("status", "SUCCESS" if ok else "ERROR")
        status = (
            RuntimeStatus(status_str)
            if isinstance(status_str, str)
            else (RuntimeStatus.SUCCESS if ok else RuntimeStatus.ERROR)
        )

        # Determine machine state
        if status == RuntimeStatus.SUCCESS:
            machine_state = MachineState.READY
        elif status == RuntimeStatus.TIMEOUT:
            machine_state = MachineState.DEGRADED
        else:
            machine_state = MachineState.FAILED if not ok else MachineState.READY

        # Extract issue label if present
        issue_label = raw_result.get("issue")
        machine_issue = MachineIssueLabel(issue_label) if issue_label else None

        # Build errors list if error present
        errors = []
        if "error" in raw_result and raw_result["error"]:
            error_msg = str(raw_result["error"])
            error_code = raw_result.get("issue", "TOOL_ERROR")
            errors.append(
                CanonicalError(
                    code=error_code,
                    message=error_msg,
                    stage=stage,
                    recoverable=verdict not in (Verdict.VOID, Verdict.HOLD_888),
                )
            )

        # Extract payload (everything that's not metadata)
        payload_keys = {"ok", "verdict", "status", "error", "issue", "trace"}
        payload = {k: v for k, v in raw_result.items() if k not in payload_keys}

        # 3E Logic: Derive Intelligence State
        intel_state = raw_result.get("intelligence_state", {})
        hypotheses = intel_state.get("hypotheses", raw_result.get("hypotheses", []))
        
        if len(hypotheses) > 3:
            expl_state = ExplorationState.BROAD
        elif len(hypotheses) > 0:
            expl_state = ExplorationState.SCOPED
        else:
            expl_state = (
                ExplorationState.BROAD
                if "search" in detected_name
                else ExplorationState.SCOPED
            )

        # Estimate Entropy State (dS)
        ds = float(raw_result.get("dS", raw_result.get("entropy_delta", -0.1)))
        if ds <= -0.5:
            entr_state = EntropyState.LOW
        elif ds <= 0.0:
            entr_state = EntropyState.MANAGEABLE
        else:
            entr_state = EntropyState.HIGH

        # Estimate Eureka State
        is_forged = raw_result.get("eureka", False) or verdict == Verdict.SEAL
        eur_state = (
            EurekaState.FORGED
            if is_forged
            else EurekaState.PARTIAL if ok else EurekaState.NONE
        )

        # Map to Ontology for motto and canonical labels
        registry = OntologyRegistry()
        metabolic_stage = registry.get_stage(stage)
        motto = metabolic_stage.motto if metabolic_stage else None

        # Map metrics to Canonical schema
        metrics = CanonicalMetrics(
            truth=float(raw_result.get("truth", 0.9 if ok else 0.5)),
            clarity_delta=ds,
            confidence=float(raw_result.get("confidence", 0.9 if ok else 0.1)),
            peace=float(raw_result.get("peace2", 1.0)),
            vitality=float(
                raw_result.get(
                    "psi_le", 1.0 if machine_state == MachineState.READY else 0.5
                )
            ),
            entropy_delta=ds,
            authority=float(raw_result.get("authority", 1.0 if auth_ctx else 0.0)),
            risk=float(raw_result.get("risk", 0.0 if ok else 0.7)),
        )

        # Build the RuntimeEnvelope
        envelope = RuntimeEnvelope(
            ok=ok,
            tool=detected_name,
            canonical_tool_name=detected_name,
            risk_class=RiskClass.LOW,  # Default for intel tools
            requires_auth=False,
            requires_human=verdict in (Verdict.HOLD, Verdict.HOLD_888),
            recoverable=ok or verdict not in (Verdict.VOID, Verdict.HOLD_888),
            session_id=session_id,
            stage=stage,
            verdict=verdict,
            status=status,
            machine_status=machine_state,
            machine_issue=machine_issue,
            intelligence_stage=raw_result.get(
                "intel_stage", IntelligenceStage.EXPLORATION
            ),
            intelligence_state={
                "exploration": expl_state,
                "entropy": entr_state,
                "eureka": eur_state,
                "hypotheses": hypotheses,
                "uncertainty_score": 1.0 - metrics.confidence,
                "dS": ds,
            },
            metrics=metrics,
            payload=payload,
            errors=errors,
            authority=CanonicalAuthority(
                actor_id=auth_ctx.get("actor_id", "anonymous"),
                level=auth_ctx.get("authority_level", "anonymous"),
                human_required=verdict in (Verdict.HOLD, Verdict.HOLD_888),
            ),
            meta=CanonicalMeta(
                debug=bool(raw_result.get("debug")),
                dry_run=bool(raw_result.get("dry_run")),
                motto=motto,
            ),
            caller_context=caller_ctx
            if isinstance(caller_ctx, CallerContext)
            else None,
            auth_context=auth_ctx if auth_ctx else None,
        )

        # P1 Strike: Sync with Governance Kernel if possible
        if session_id:
            try:
                from arifosmcp.core.governance_kernel import get_governance_kernel
                kernel = get_governance_kernel(session_id)
                # Sync telemetry components
                kernel.consume_tool_call()
                if ds != 0:
                    kernel.update_uncertainty(
                        safety_omega=1.0 - metrics.confidence,
                        display_omega=1.0 - metrics.confidence,
                        components={detected_name: ds}
                    )
            except Exception:
                pass

        return envelope

    # For any other return type, wrap as payload
    return RuntimeEnvelope(
        ok=True,
        tool=detected_name,
        canonical_tool_name=detected_name,
        session_id=session_id,
        stage=stage,
        verdict=default_verdict,
        status=RuntimeStatus.SUCCESS,
        machine_status=MachineState.READY,
        payload={"result": raw_result},
        caller_context=caller_ctx if isinstance(caller_ctx, CallerContext) else None,
        auth_context=auth_ctx if auth_ctx else None,
    )


def _error_envelope(
    e: Exception,
    detected_name: str,
    session_id: str | None,
    stage: str,
    auth_ctx: dict[str, Any],
    caller_ctx: Any,
) -> RuntimeEnvelope:
    # Even exceptions get wrapped in RuntimeEnvelope — never escape naked
    return RuntimeEnvelope(
        ok=False,
        tool=detected_name,
        session_id=session_id,
        stage=stage,
        verdict=Verdict.HOLD,  # Never VOID for mechanical failures
        status=RuntimeStatus.ERROR,
        machine_status=MachineState.FAILED,
        machine_issue=MachineIssueLabel.INTERNAL_RUNTIME_ERROR,
        metrics=CanonicalMetrics(
            confidence=0.0,
            vitality=0.0,
            risk=0.9,
        ),
        errors=[
            CanonicalError(
                code="TOOL_EXCEPTION",
                message=str(e),
                stage=stage,
                recoverable=False,
            )
        ],
        authority=CanonicalAuthority(
            actor_id=auth_ctx.get("actor_id", "anonymous") if auth_ctx else "anonymous",
            level="anonymous",
            human_required=True,  # Exception requires human review
        ),
        caller_context=caller_ctx if isinstance(caller_ctx, CallerContext) else None,
        auth_context=auth_ctx if auth_ctx else None,
        canonical_tool_name=detected_name,
    )


# Convenience partials for common tool patterns
seal_tool = functools.partial(unified_tool_output, default_verdict=Verdict.SEAL)
sabar_tool = functools.partial(unified_tool_output, default_verdict=Verdict.SABAR)
hold_tool = functools.partial(unified_tool_output, default_verdict=Verdict.HOLD)

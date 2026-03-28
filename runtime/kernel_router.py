"""
kernel_router.py — Internal Routing Consolidation for arifOS_kernel

CONSOLIDATION PRINCIPLE:
- All intelligence routing goes through arifOS_kernel
- Internal tools (agi_mind, asi_heart, engineering_memory, etc.) are called internally
- No external mode exposure — intent is inferred from query
- Legacy aliases map to unified calls

USER-FACING TOOLS (4):
1. init_anchor     — Identity + authority
2. arifOS_kernel   — ALL thinking + execution (internal routing)
3. apex_soul       — Judgment + validation (explicit constitutional check)
4. physics_reality — Grounding + reality ops

INTERNAL TOOLS (called by kernel, not user-facing):
- agi_mind, asi_heart, engineering_memory, math_estimator, code_engine, vault_ledger
"""

from __future__ import annotations

import logging
from typing import Any, Literal

from arifosmcp.runtime.models import RuntimeEnvelope, Stage, Verdict
from arifosmcp.runtime.sessions import get_session_identity, _normalize_session_id

logger = logging.getLogger(__name__)

# Internal capability detection patterns
REASONING_PATTERNS = [
    "analyze", "reason", "think", "synthesize", "compare", "evaluate",
    "what is", "how does", "why", "explain", "interpret", "assess"
]

SAFETY_PATTERNS = [
    "is this safe", "critique", "review", "validate", "check for",
    "potential harm", "risk assessment", "ethical", "concern"
]

MEMORY_PATTERNS = [
    "remember", "recall", "search memory", "find previous", "what did",
    "store this", "save to memory", "vector search", "semantic"
]

CODE_PATTERNS = [
    "execute", "run command", "file system", "inspect", "list files",
    "process list", "network status", "tail log", "replay trace"
]

REALITY_PATTERNS = [
    "search web", "fetch url", "current time", "weather", "news",
    "ground truth", "verify fact", "atlas", "compass"
]


def _detect_intent(query: str | None) -> tuple[Literal["reason", "safety", "memory", "code", "reality"], float]:
    """
    Detect intent from query without requiring explicit mode.
    Returns: (intent_type, confidence)
    """
    if not query:
        return "reason", 0.5
    
    query_lower = query.lower()
    scores = {
        "reason": sum(1 for p in REASONING_PATTERNS if p in query_lower),
        "safety": sum(1 for p in SAFETY_PATTERNS if p in query_lower),
        "memory": sum(1 for p in MEMORY_PATTERNS if p in query_lower),
        "code": sum(1 for p in CODE_PATTERNS if p in query_lower),
        "reality": sum(1 for p in REALITY_PATTERNS if p in query_lower),
    }
    
    total = sum(scores.values())
    if total == 0:
        return "reason", 0.5  # Default to reasoning
    
    best = max(scores, key=scores.get)
    confidence = scores[best] / max(total, 1)
    return best, confidence


async def _route_to_internal_tool(
    intent_type: str,
    query: str,
    session_id: str | None,
    payload: dict[str, Any],
    ctx: Any = None,
    trace: list[dict] | None = None,
) -> RuntimeEnvelope:
    """
    Route to appropriate internal tool based on detected intent.
    All internal tools return RuntimeEnvelope for consistency.
    """
    from arifosmcp.runtime.tools_internal import (
        agi_mind_dispatch_impl,
        asi_heart_dispatch_impl,
        engineering_memory_dispatch_impl,
        code_engine_dispatch_impl,
    )
    
    session_id = _normalize_session_id(session_id)
    trace_entry = {
        "stage": "444_ROUTER",
        "intent_detected": intent_type,
        "query": query[:100] if query else "",
    }
    
    if intent_type == "reason":
        trace_entry["routed_to"] = "agi_mind"
        if trace is not None:
            trace.append(trace_entry)
        return await agi_mind_dispatch_impl(
            mode="reason",
            payload={"query": query, **payload},
            auth_context=payload.get("auth_context"),
            risk_tier=payload.get("risk_tier", "medium"),
            dry_run=bool(payload.get("dry_run", True)),
            ctx=ctx,
        )
    
    elif intent_type == "safety":
        trace_entry["routed_to"] = "asi_heart"
        if trace is not None:
            trace.append(trace_entry)
        return await asi_heart_dispatch_impl(
            mode="critique",
            payload={"content": query, **payload},
            auth_context=payload.get("auth_context"),
            risk_tier=payload.get("risk_tier", "high"),  # Safety always high tier
            dry_run=bool(payload.get("dry_run", True)),
            ctx=ctx,
        )
    
    elif intent_type == "memory":
        trace_entry["routed_to"] = "engineering_memory"
        if trace is not None:
            trace.append(trace_entry)
        return await engineering_memory_dispatch_impl(
            mode="vector_query" if "search" in query.lower() or "find" in query.lower() else "vector_store",
            payload={"task": query, **payload},
            auth_context=payload.get("auth_context"),
            risk_tier=payload.get("risk_tier", "medium"),
            dry_run=bool(payload.get("dry_run", True)),
            ctx=ctx,
        )
    
    elif intent_type == "code":
        trace_entry["routed_to"] = "code_engine"
        if trace is not None:
            trace.append(trace_entry)
        mode = "fs"  # Default
        if "process" in query.lower():
            mode = "process"
        elif "net" in query.lower() or "network" in query.lower():
            mode = "net"
        elif "tail" in query.lower() or "log" in query.lower():
            mode = "tail"
        elif "replay" in query.lower():
            mode = "replay"
        
        return await code_engine_dispatch_impl(
            mode=mode,
            payload={"query": query, **payload},
            auth_context=payload.get("auth_context"),
            risk_tier=payload.get("risk_tier", "high"),  # Code execution high tier
            dry_run=bool(payload.get("dry_run", True)),
            ctx=ctx,
        )
    
    elif intent_type == "reality":
        trace_entry["routed_to"] = "physics_reality"
        if trace is not None:
            trace.append(trace_entry)
        # Reality calls should go to physics_reality tool directly
        # This is handled by the caller (arifOS_kernel)
        from arifosmcp.runtime.tools_internal import physics_reality_dispatch_impl
        return await physics_reality_dispatch_impl(
            mode="compass",
            payload={"query": query, **payload},
            auth_context=payload.get("auth_context"),
            risk_tier=payload.get("risk_tier", "medium"),
            dry_run=bool(payload.get("dry_run", True)),
            ctx=ctx,
        )
    
    # Fallback to reasoning
    trace_entry["routed_to"] = "agi_mind (fallback)"
    if trace is not None:
        trace.append(trace_entry)
    return await agi_mind_dispatch_impl(
        mode="reason",
        payload={"query": query, **payload},
        auth_context=payload.get("auth_context"),
        risk_tier=payload.get("risk_tier", "medium"),
        dry_run=bool(payload.get("dry_run", True)),
        ctx=ctx,
    )


async def kernel_intelligent_route(
    query: str | None = None,
    session_id: str | None = None,
    payload: dict[str, Any] | None = None,
    auth_context: dict[str, Any] | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    allow_execution: bool = False,
    ctx: Any = None,
    intent: str | None = None,  # Optional explicit override
    use_memory: bool = True,
    use_heart: bool = True,
    debug: bool = False,
) -> RuntimeEnvelope:
    """
    Unified kernel router — internal consolidation entry point.
    
    This is the heart of the consolidation:
    - No external modes exposed
    - Intent detected from query or explicit intent param
    - Routes to agi_mind, asi_heart, engineering_memory, code_engine internally
    - Returns unified RuntimeEnvelope
    - Optional debug mode includes full routing trace
    """
    payload = dict(payload or {})
    session_id = _normalize_session_id(session_id)
    
    # Build routing trace for transparency
    trace: list[dict] = [] if debug else None
    
    if debug:
        trace.append({
            "stage": "444_ROUTER",
            "action": "kernel_entry",
            "query": query[:100] if query else "",
            "session_id": session_id,
        })
    
    # Step 1: Detect intent
    if intent:
        intent_type = intent
        confidence = 1.0
    else:
        intent_type, confidence = _detect_intent(query)
    
    if debug and trace is not None:
        trace.append({
            "stage": "444_ROUTER", 
            "action": "intent_detection",
            "detected": intent_type,
            "confidence": round(confidence, 2),
        })
    
    # Step 2: Check session validity (F2 Truth enforcement)
    session_identity = get_session_identity(session_id)
    if not session_identity and session_id != "global":
        # Session not anchored — redirect to init_anchor
        result = RuntimeEnvelope(
            ok=False,
            tool="arifOS_kernel",
            session_id=session_id,
            stage=Stage.ROUTER_444.value,
            verdict=Verdict.VOID,
            status="ERROR",
            errors=[{
                "code": "SESSION_NOT_ANCHORED",
                "message": "Session not found. Call init_anchor first.",
                "stage": "444_ROUTER",
            }],
            payload={
                "next_action": {
                    "tool": "init_anchor",
                    "mode": "init",
                    "reason": "Identity required for kernel execution",
                },
            },
        )
        if debug:
            result.payload["_trace"] = trace
        return result
    
    # Step 3: Route to internal tool
    result = await _route_to_internal_tool(
        intent_type=intent_type,
        query=query or "",
        session_id=session_id,
        payload={**payload, "auth_context": auth_context, "risk_tier": risk_tier, "dry_run": dry_run},
        ctx=ctx,
        trace=trace if debug else None,
    )
    
    # Step 4: Apply safety critique if enabled (use_heart)
    if use_heart and not dry_run and risk_tier in ("high", "critical"):
        from arifosmcp.runtime.tools_internal import asi_heart_dispatch_impl
        
        if debug and trace is not None:
            trace.append({
                "stage": "666_HEART",
                "action": "safety_critique",
                "reason": f"high-risk tier {risk_tier}",
            })
        
        critique = await asi_heart_dispatch_impl(
            mode="critique",
            payload={
                "content": result.payload.get("output", str(result.payload)),
                "original_query": query,
                **payload,
            },
            auth_context=auth_context,
            risk_tier=risk_tier,
            dry_run=True,  # Critique is always dry-run
            ctx=ctx,
        )
        
        # Attach critique to result
        result.payload["_safety_critique"] = critique.payload if critique else None
    
    # Step 5: Store to memory if enabled (use_memory)
    if use_memory and not dry_run and result.verdict == Verdict.SEAL:
        from arifosmcp.runtime.tools_internal import engineering_memory_dispatch_impl
        
        if debug and trace is not None:
            trace.append({
                "stage": "555_MEMORY",
                "action": "store_outcome",
            })
        
        await engineering_memory_dispatch_impl(
            mode="vector_store",
            payload={
                "task": f"Query: {query}\nResult: {result.payload.get('output', '')}",
                "session_id": session_id,
                **payload,
            },
            auth_context=auth_context,
            risk_tier=risk_tier,
            dry_run=dry_run,
            ctx=ctx,
        )
    
    # Step 6: Attach trace if debug mode
    if debug and trace is not None:
        result.payload["_trace"] = trace
        result.payload["_routing"] = {
            "intent_detected": intent_type,
            "internal_tools_called": [t.get("routed_to") for t in trace if "routed_to" in t],
        }
    
    return result


# Legacy alias mappings (for backward compatibility)
async def legacy_agi_reason_route(**kwargs) -> RuntimeEnvelope:
    """Maps legacy agi_reason to unified kernel router."""
    return await kernel_intelligent_route(intent="reason", **kwargs)


async def legacy_asi_critique_route(**kwargs) -> RuntimeEnvelope:
    """Maps legacy asi_critique to unified kernel router."""
    return await kernel_intelligent_route(intent="safety", **kwargs)


async def legacy_memory_query_route(**kwargs) -> RuntimeEnvelope:
    """Maps legacy memory query to unified kernel router."""
    return await kernel_intelligent_route(intent="memory", **kwargs)


async def legacy_code_engine_route(**kwargs) -> RuntimeEnvelope:
    """Maps legacy code_engine to unified kernel router."""
    return await kernel_intelligent_route(intent="code", **kwargs)

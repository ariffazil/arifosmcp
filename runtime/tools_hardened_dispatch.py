"""
arifosmcp/runtime/tools_hardened_dispatch.py — Dispatcher for Hardened Tools

FIX: apex_soul mode dispatch and argument alignment.
FIX: code_engine and architect_registry floor induction.
"""

from __future__ import annotations

import logging
from typing import Any

from arifosmcp.runtime.init_anchor_hardened import HardenedInitAnchor
from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
from arifosmcp.runtime.tools_hardened_v2 import (
    HardenedAGIReason,
    HardenedAgentZeroEngineer,
    HardenedASICritique,
    HardenedApexJudge,
    HardenedVaultSeal,
    HardenedMathEstimator,
)
from arifosmcp.runtime.truth_pipeline_hardened import HardenedRealityAtlas, HardenedRealityCompass
from fastmcp.dependencies import CurrentContext

# Initialize hardened tool instances
init_anchor_tool = HardenedInitAnchor()
reality_compass_tool = HardenedRealityCompass()
reality_atlas_tool = HardenedRealityAtlas()
agi_reason_tool = HardenedAGIReason()
asi_heart_dispatch_impl = HardenedASICritique()
agentzero_engineer_tool = HardenedAgentZeroEngineer()
apex_judge_tool = HardenedApexJudge()
vault_seal_tool = HardenedVaultSeal()
math_estimator_tool = HardenedMathEstimator()


def _apply_policy(
    envelope_dict: dict[str, Any], tool: str, mode: str, input_payload: dict[str, Any]
) -> dict[str, Any]:
    """Apply high-level governance policy to the tool envelope."""
    # Ensure envelope has required fields for bridge
    if "ok" not in envelope_dict:
        envelope_dict["ok"] = envelope_dict.get("status") == "OK"
    if "verdict" not in envelope_dict:
        envelope_dict["verdict"] = "SEAL" if envelope_dict["ok"] else "VOID"
    return envelope_dict


async def hardened_init_anchor_dispatch(
    mode: str, payload: dict[str, Any], **kwargs
) -> dict[str, Any]:
    envelope = await init_anchor_tool.init(
        mode=mode,
        actor_id=payload.get("actor_id"),
        intent=payload.get("intent"),
        human_approval=payload.get("human_approval", False),
        session_id=payload.get("session_id"),
    )
    return _apply_policy(envelope.to_dict(), "init_anchor", mode, payload)


async def hardened_physics_reality_dispatch(
    mode: str, payload: dict[str, Any], **kwargs
) -> dict[str, Any]:
    if mode == "compass":
        envelope = await reality_compass_tool.search(
            query=payload.get("query") or payload.get("input"),
            session_id=payload.get("session_id"),
        )
    elif mode == "atlas":
        envelope = await reality_atlas_tool.map(
            query=payload.get("query") or payload.get("input"),
            session_id=payload.get("session_id"),
        )
    else:
        # Fallback to internal reality handlers
        from arifosmcp.runtime.tools_internal import physics_reality_dispatch_impl

        envelope = await physics_reality_dispatch_impl(
            mode=mode,
            payload=payload,
            auth_context=payload.get("auth_context"),
            risk_tier=payload.get("risk_tier", "medium"),
            dry_run=payload.get("dry_run", True),
            ctx=CurrentContext(),
        )

    return _apply_policy(envelope.to_dict(), "physics_reality", mode, payload)


async def hardened_agi_mind_dispatch(
    mode: str, payload: dict[str, Any], **kwargs
) -> dict[str, Any]:
    session_id = payload.get("session_id")
    query = payload.get("query")

    if mode in ("reason", "reflect", "forge"):
        # Check if we should run full Ollama reasoning (for "reason" mode)
        # The "reflect" and "forge" modes go through metabolic_loop internally
        thought_chain = None

        if mode == "reason":
            # Run full agi() pipeline to get actual reasoning with Ollama
            try:
                from arifosmcp.core.organs._1_agi import (
                    agi,
                    build_st_thought_chain_from_agi_output,
                )

                # Execute the 3-phase Ollama reasoning
                agi_output = await agi(
                    query=query,
                    session_id=session_id,
                    action="reason",
                    reason_mode="default",
                    max_tokens=800,
                )

                # Build Sequential Thinking chain from agi output
                thought_chain = build_st_thought_chain_from_agi_output(agi_output, session_id)

            except Exception as ollama_err:
                # Ollama not available or failed — use fallback chain
                logger = __import__("logging").getLogger(__name__)
                logger.warning(f"Ollama reasoning failed: {ollama_err}, using fallback")
                thought_chain = None

        # Call HardenedAGIReason with thought chain for QT Quad
        # Pass through telos manifold, coherence, AND constitutional context for AI grounding
        envelope = await agi_reason_tool.reason(
            query=query,
            is_forge=(mode == "forge"),
            session_id=session_id,
            thought_chain=thought_chain,
            telos_manifold=payload.get("telos_manifold"),
            previous_coherence=payload.get("previous_coherence"),
            constitutional_context=payload.get("constitutional_context"),
        )
    else:
        return {"ok": False, "error": f"Invalid mode for agi_mind: {mode}"}

    envelope_dict = _apply_policy(envelope.to_dict(), "agi_mind", mode, payload)
    return envelope_dict


async def hardened_asi_heart_dispatch(
    mode: str, payload: dict[str, Any], **kwargs
) -> dict[str, Any]:
    if mode in ("critique", "simulate"):
        envelope = await asi_heart_dispatch_impl.critique(
            candidate=payload.get("proposal") or payload.get("content"),
            session_id=payload.get("session_id"),
        )
    else:
        return {"ok": False, "error": f"Invalid mode for asi_heart: {mode}"}

    return _apply_policy(envelope.to_dict(), "asi_heart", mode, payload)


async def hardened_engineering_memory_dispatch(
    mode: str, payload: dict[str, Any], **kwargs
) -> dict[str, Any]:
    if mode in ("engineer", "recall", "write", "generate"):
        from arifosmcp.runtime.tools_internal import engineering_memory_dispatch_impl

        envelope = await engineering_memory_dispatch_impl(
            mode=mode,
            payload=payload,
            auth_context=payload.get("auth_context"),
            risk_tier=payload.get("risk_tier", "medium"),
            dry_run=payload.get("dry_run", True),
            ctx=CurrentContext(),
        )
        return _apply_policy(envelope.to_dict(), "engineering_memory", mode, payload)
    else:
        return {"ok": False, "error": f"Invalid mode for engineering_memory: {mode}"}

    return _apply_policy(envelope.to_dict(), "engineering_memory", mode, payload)


async def hardened_apex_judge_dispatch(
    mode: str, payload: dict[str, Any], **kwargs
) -> dict[str, Any]:
    if mode in ("judge", "rules", "validate", "armor", "probe", "hold", "notify"):
        envelope = await apex_judge_tool.judge(
            proposal=payload.get("proposal") or payload.get("candidate"),
            session_id=payload.get("session_id"),
            mode=mode,
        )
    else:
        return {"ok": False, "error": f"Invalid mode for apex_judge: {mode}"}

    return _apply_policy(envelope.to_dict(), "apex_judge", mode, payload)


async def hardened_vault_ledger_dispatch(
    mode: str, payload: dict[str, Any], **kwargs
) -> dict[str, Any]:
    if mode in ("seal", "verify"):
        envelope = await vault_seal_tool.seal(
            decision=payload.get("decision") or {}, session_id=payload.get("session_id")
        )
        return _apply_policy(envelope.to_dict(), "vault_ledger", mode, payload)
    return {"ok": False, "error": f"Invalid mode for vault_ledger: {mode}"}


async def hardened_code_engine_dispatch(
    mode: str, payload: dict[str, Any], **kwargs
) -> dict[str, Any]:
    from arifosmcp.runtime.shell_forge import forge

    command = payload.get("command") or payload.get("code")
    if not command:
        return {"ok": False, "error": "No command/code provided"}
    res = forge.execute(
        command=command,
        dry_run=payload.get("dry_run", True),
        session_id=payload.get("session_id", "anonymous"),
    )
    return _apply_policy(res, "code_engine", mode, payload)


async def hardened_architect_registry_dispatch(
    mode: str, payload: dict[str, Any], **kwargs
) -> dict[str, Any]:
    res = {"ok": True, "registry": "arifOS Sovereign Registry", "mode": mode}
    return _apply_policy(res, "architect_registry", mode, payload)


async def hardened_arifos_kernel_dispatch(
    mode: str, payload: dict[str, Any], **kwargs
) -> dict[str, Any]:
    session_id = payload.get("session_id")
    if not session_id:
        return {"ok": False, "error": "arifOS_kernel requires session_id."}
    from arifosmcp.runtime.orchestrator import metabolic_loop

    result = await metabolic_loop(
        query=payload.get("query") or "No query",
        session_id=session_id,
        risk_tier=payload.get("risk_tier", "medium"),
        actor_id=payload.get("actor_id", "anonymous"),
        auth_context=payload.get("auth_context"),
        dry_run=payload.get("dry_run", True),
    )
    return _apply_policy(result, "arifOS_kernel", mode, payload)


async def hardened_math_estimator_dispatch(
    mode: str, payload: dict[str, Any], **kwargs
) -> dict[str, Any]:
    if mode in ("health", "cost", "vitals"):
        envelope = await math_estimator_tool.estimate(
            mode=mode, session_id=payload.get("session_id")
        )
        return _apply_policy(envelope.to_dict(), "math_estimator", mode, payload)
    return {"ok": False, "error": f"Invalid mode for math_estimator: {mode}"}


async def hardened_compat_probe_dispatch(
    mode: str, payload: dict[str, Any], **kwargs
) -> dict[str, Any]:
    # This tool is its own implementation for now
    from arifosmcp.runtime.megaTools.tool_12_compat_probe import compat_probe

    envelope = await compat_probe(
        mode=mode,
        session_id=payload.get("session_id"),
        auth_context=payload.get("auth_context"),
    )
    return _apply_policy(envelope.to_dict(), "compat_probe", mode, payload)


HARDENED_DISPATCH_MAP = {
    "init_anchor": hardened_init_anchor_dispatch,
    "arifOS_kernel": hardened_arifos_kernel_dispatch,
    "physics_reality": hardened_physics_reality_dispatch,
    "agi_mind": hardened_agi_mind_dispatch,
    "asi_heart": hardened_asi_heart_dispatch,
    "engineering_memory": hardened_engineering_memory_dispatch,
    "apex_judge": hardened_apex_judge_dispatch,
    "vault_ledger": hardened_vault_ledger_dispatch,
    "code_engine": hardened_code_engine_dispatch,
    "architect_registry": hardened_architect_registry_dispatch,
    "math_estimator": hardened_math_estimator_dispatch,
    "compat_probe": hardened_compat_probe_dispatch,
}

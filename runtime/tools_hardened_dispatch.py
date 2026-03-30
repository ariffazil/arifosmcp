"""
arifosmcp/runtime/tools_hardened_dispatch.py — Dispatcher for Hardened Tools

FIX: apex_soul mode dispatch and argument alignment.
FIX: code_engine and architect_registry floor induction.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from arifosmcp.core.shared.physics import delta_S, genius_score, humility_band
from arifosmcp.runtime.contracts_v2 import (
    OutputPolicy,
    VerdictScope,
)
from arifosmcp.runtime.init_anchor_hardened import HardenedInitAnchor
from arifosmcp.runtime.substrate_policy import get_policy
from arifosmcp.runtime.tools_hardened_v2 import (
    HardenedAGIReason,
    HardenedAgentZeroEngineer,
    HardenedASICritique,
    HardenedApexJudge,
    HardenedVaultSeal,
    HardenedMathEstimator,
)
from arifosmcp.runtime.truth_pipeline_hardened import HardenedRealityAtlas, HardenedRealityCompass

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
    """Inject empirical substrate policy and thermodynamic metrics."""
    policy = get_policy(tool, mode)
    if not policy:
        return envelope_dict

    # 1. Base Policy Mapping (Now with Floors)
    envelope_dict["substrate_class"] = [policy.substrate.value]
    envelope_dict["risk_tier"] = policy.risk.value
    envelope_dict["organ_stage"] = policy.organ_stage
    envelope_dict["floors"] = policy.floors  # Assigned Floors now visible

    # 2. Empirical Thermodynamic Measurement (F4 Clarity)
    input_str = json.dumps(input_payload, sort_keys=True, default=str)
    output_str = json.dumps(envelope_dict.get("payload", {}), sort_keys=True, default=str)

    ds = delta_S(input_str, output_str)
    envelope_dict["entropy"] = {
        "delta_s": round(ds, 4),
        "is_stable": ds <= 0,
        "source": "empirical_measurement",
    }

    # 3. Dynamic Genius Score (F8) — Enhanced with QT Quad W₂/W₄
    conf = envelope_dict.get("confidence", 0.85)
    peace = 1.0
    exploration = 0.9
    energy = 1.0 if ds <= 0 else 0.8

    g = genius_score(A=conf, P=peace, X=exploration, E=energy)

    # QT Quad Enhancement: G_governed = G × W_four
    # If W_four present (from agi_reason with thought chain), apply governance
    payload = envelope_dict.get("payload", {})
    w_four = payload.get("W_four", 0.0)
    if w_four > 0:
        g_governed = round(g * w_four, 4)
        envelope_dict["g_score"] = g_governed
        envelope_dict["g_base"] = round(g, 4)
        envelope_dict["W_four"] = w_four
        envelope_dict["g_override"] = True
    else:
        envelope_dict["g_score"] = round(g, 4)
        envelope_dict["g_override"] = False

    # 4. Humility Mapping (F7)
    omega = humility_band(conf).omega_0
    envelope_dict["humility_band"] = omega

    # 5. Geox Eureka: Goldilocks & Godellock (The Paradox Eureka)
    is_goldilocks = (ds <= 0) and (0.03 <= omega <= 0.05)
    is_godellock = omega < 0.03

    envelope_dict["geox_eureka"] = {
        "is_goldilocks": is_goldilocks,
        "is_godellock": is_godellock,
        "verdict": "HABITABLE" if is_goldilocks else ("LOCKED" if is_godellock else "UNSTABLE"),
    }

    # 6. Proactive 888_HOLD & Godellock Void
    if is_godellock:
        envelope_dict["verdict"] = "VOID"
        envelope_dict["note"] = (
            "Godellock Detected: System trapped in internal consistency. Zero external reach."
        )
    elif (policy.risk in ("high", "critical")) and envelope_dict.get("verdict") != "VOID":
        envelope_dict["verdict"] = "888_HOLD"
        envelope_dict["note"] = f"Sovereign approval required for {policy.substrate} operation."

    # 7. QT Quad Proof — Propagate to envelope top-level for visibility
    qt_proof = payload.get("qt_proof")
    if qt_proof:
        envelope_dict["qt_proof"] = qt_proof
        envelope_dict["quad_witness_valid"] = qt_proof.get("quad_witness_valid", False)

        # Override verdict based on W_four threshold
        if qt_proof["W_four"] >= 0.75:
            envelope_dict["qt_verdict"] = "SEAL"
        elif qt_proof["W_four"] >= 0.50:
            envelope_dict["qt_verdict"] = "SABAR"
        else:
            envelope_dict["qt_verdict"] = "HOLD_888"

    return envelope_dict


async def hardened_init_anchor_dispatch(
    mode: str, payload: dict[str, Any], **kwargs
) -> dict[str, Any]:
    # Fix 4 — import anchor hold registry for void propagation
    from arifosmcp.agentzero.escalation.hold_state import anchor_hold_registry

    if mode == "init":
        human_approval_val = payload.get("human_approval", payload.get("human_approved", False))
        if "human_approved" in payload and "human_approval" not in payload:
            import logging

            logging.warning("Deprecated field 'human_approved' used. Migrate to 'human_approval'.")

        envelope = await init_anchor_tool.init(
            actor_id=payload.get("actor_id"),
            declared_name=payload.get("declared_name"),
            intent=payload.get("intent"),
            session_id=payload.get("session_id"),
            human_approval=human_approval_val,
            query=payload.get("query"),
            raw_input=payload.get("raw_input"),
            auth_context=payload.get("auth_context"),
            caller_context=payload.get("caller_context"),
            pns_shield=payload.get("pns_shield"),
            model_soul=payload.get("model_soul"),
            risk_tier=payload.get("risk_tier", "low"),
            session_class=payload.get("session_class", "execute"),
            requested_scope=payload.get("requested_scope"),
        )
    elif mode in ("state", "status"):
        envelope = await init_anchor_tool.state(session_id=payload.get("session_id"))
    elif mode == "refresh":
        envelope = await init_anchor_tool.refresh(session_id=payload.get("session_id"))
    elif mode == "revoke":
        envelope = await init_anchor_tool.revoke(session_id=payload.get("session_id") or "unknown")
    else:
        return {"ok": False, "error": f"Invalid mode for init_anchor: {mode}"}

    envelope_dict = _apply_policy(envelope.to_dict(), "init_anchor", mode, payload)

    # Preserve objects for RuntimeEnvelope reconstruction
    envelope_dict["authority"] = getattr(envelope, "authority", None)
    envelope_dict["auth_context"] = getattr(envelope, "auth_context", None)
    envelope_dict["caller_state"] = getattr(envelope, "caller_state", "anonymous")
    envelope_dict["allowed_next_tools"] = getattr(envelope, "allowed_next_tools", [])

    # Fix 4 — Anchor void propagation (F1/F11/F12).
    raw_status = envelope_dict.get("status") or envelope_dict.get("payload", {}).get("status")
    raw_session = envelope_dict.get("session_id", "")
    if mode == "init" and (
        raw_status in ("void", "VOID") or str(raw_session).startswith("session-rejected")
    ):
        void_reason = (
            envelope_dict.get("payload", {}).get("reason")
            or envelope_dict.get("error")
            or "init_anchor returned void; session not established."
        )
        anchor_key = payload.get("actor_id") or payload.get("session_id") or "unknown"
        anchor_hold_registry.set_global_hold(
            session_key=anchor_key,
            reason=void_reason,
            blocked_tools="ALL_ANCHOR_DEPENDENT",
            release_condition="Re-run init_anchor with valid intent+query+raw_input+actor_id",
        )
        envelope_dict["output_policy"] = OutputPolicy.CANNOT_COMPUTE.value
        envelope_dict["verdict_scope"] = VerdictScope.DOMAIN_VOID.value
        envelope_dict.setdefault("warnings", []).append(
            "888_HOLD activated: anchor is void. "
            "All anchor-dependent tools are blocked until valid init_anchor succeeds. "
            "Model MUST NOT proceed to any anchor-dependent tool. "
            "Surface to user: '888_HOLD — anchor void. Re-init required.'"
        )
    elif mode == "init" and raw_status not in ("void", "VOID", None):
        anchor_key = payload.get("actor_id") or payload.get("session_id") or "unknown"
        anchor_hold_registry.clear_hold(anchor_key)
        envelope_dict["verdict_scope"] = VerdictScope.SESSION_SEAL.value

    if mode == "init":
        try:
            from arifosmcp.core.recovery.rollback_engine import outcome_ledger

            envelope_dict["scar_context"] = outcome_ledger.build_scar_context(n=10)
        except Exception as _sc_err:
            envelope_dict["scar_context"] = {"error": str(_sc_err)}

    return envelope_dict


async def hardened_physics_reality_dispatch(
    mode: str, payload: dict[str, Any], **kwargs
) -> dict[str, Any]:
    if mode in ("compass", "search", "ingest"):
        envelope = await reality_compass_tool.ingest(
            query=payload.get("query") or payload.get("input"),
            is_temporal=payload.get("is_temporal", False),
            strips=payload.get("strips"),
            session_id=payload.get("session_id"),
        )
    elif mode == "atlas":
        envelope = await reality_atlas_tool.map_claims(
            evidence_bundles=payload.get("evidence_bundles", []),
            session_id=payload.get("session_id"),
        )
    elif mode == "time":
        res = {"ok": True, "utc": datetime.now(timezone.utc).isoformat()}
        return _apply_policy(res, "physics_reality", mode, payload)
    else:
        return {"ok": False, "error": f"Invalid mode for physics_reality: {mode}"}

    result = _apply_policy(envelope.to_dict(), "physics_reality", mode, payload)
    return result


async def hardened_agi_mind_dispatch(
    mode: str, payload: dict[str, Any], **kwargs
) -> dict[str, Any]:
    if mode in ("reason", "reflect", "forge"):
        query = payload.get("query", "")
        session_id = payload.get("session_id") or "anonymous"

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
        envelope = await agentzero_engineer_tool.plan_execution(
            task=payload.get("task") or payload.get("query"),
            action_class=payload.get("action_class", "read"),
            session_id=payload.get("session_id"),
        )
    else:
        return {"ok": False, "error": f"Invalid mode for engineering_memory: {mode}"}

    return _apply_policy(envelope.to_dict(), "engineering_memory", mode, payload)


async def hardened_apex_soul_dispatch(
    mode: str, payload: dict[str, Any], **kwargs
) -> dict[str, Any]:
    if mode in ("judge", "rules", "validate", "armor", "probe", "hold", "notify"):
        envelope = await apex_judge_tool.judge(
            proposal=payload.get("proposal") or payload.get("candidate"),
            session_id=payload.get("session_id"),
            mode=mode,
        )
    else:
        return {"ok": False, "error": f"Invalid mode for apex_soul: {mode}"}

    return _apply_policy(envelope.to_dict(), "apex_soul", mode, payload)


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
    "apex_soul": hardened_apex_soul_dispatch,
    "vault_ledger": hardened_vault_ledger_dispatch,
    "code_engine": hardened_code_engine_dispatch,
    "architect_registry": hardened_architect_registry_dispatch,
    "math_estimator": hardened_math_estimator_dispatch,
    "compat_probe": hardened_compat_probe_dispatch,
}

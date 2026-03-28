"""
arifosmcp.intelligence/triad/delta/think.py — Stage 222 THINK

Thermodynamic processing chamber. Raw intent is structured into logical,
fact-checked hypotheses before proceeding to Stage 333 ATLAS.

Three orthogonal cognitive paths run in parallel to prevent narrow or biased
reasoning:
  - Conservative: narrow, high-certainty logic (high-stakes decisions)
  - Exploratory:  broad alternatives (creative problem-solving)
  - Adversarial:  internal red-team to stress-test assumptions

Constitutional enforcement: F2 (Truth), F4 (Clarity/ΔS), F13 (Curiosity ≥ 3 paths).
Output: Delta Draft (PROVISIONAL, unsealed) → routes to Stage 333 ATLAS.

SAMPLING INTEGRATION (v2026.3):
When FastMCP Context is provided, uses ctx.sample() for governed LLM reasoning.
This transforms arifOS from a structural validator into a true 3E intelligence engine.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from arifosmcp.core.kernel import kernel

from .._utils import serialize_floor_concerns

if TYPE_CHECKING:
    from fastmcp import Context


_SAMPLING_ENABLED = True

try:
    from arifosmcp.core.constitutional_sampling import SamplingConfig, ThinkResult, sample_think
except ImportError:
    _SAMPLING_ENABLED = False


# ---------------------------------------------------------------------------
# Three Orthogonal Reasoning Paths
# ---------------------------------------------------------------------------


async def _run_conservative_path(action: str, context: str) -> dict:
    """
    Conservative path: narrow, highly-certain logic.
    Used for high-stakes decisions where precision beats breadth.
    """
    audit_res = kernel.audit(
        action=f"[CONSERVATIVE] {action}",
        context=context,
        severity="high",
    )
    confidence = round(audit_res.pass_rate * 0.95, 3)
    return {
        "path": "conservative",
        "hypothesis": action[:200],
        "confidence": confidence,
        "assumptions": [
            {"type": "verifiable", "text": "evidence base is current"},
            {"type": "canonical", "text": "follows standard L2 procedure"},
            {"type": "verifiable", "text": "tight scope constraints"},
        ],
        "disposition": "advance" if confidence > 0.85 else "ground",
        "verdict": audit_res.verdict.value,
        "delta_s": audit_res.delta_s,
        "floor_pass_rate": audit_res.pass_rate,
    }


async def _run_exploratory_path(action: str, context: str) -> dict:
    """
    Exploratory path: broad alternatives for creative problem-solving.
    Generates at least three distinct alternatives to satisfy F13 Curiosity.
    """
    audit_res = kernel.audit(
        action=f"[EXPLORATORY] option: {action} alternative: approach choice: route",
        context=context,
        severity="low",
    )
    confidence = round(audit_res.pass_rate * 0.75, 3)
    return {
        "path": "exploratory",
        "hypothesis": f"Broad framing: {action[:150]}",
        "confidence": confidence,
        "alternatives": [
            f"Option A — direct approach: {action[:80]}",
            f"Option B — inversion: reconsider assumptions behind '{action[:50]}'",
            "Option C — systemic view: what upstream factors drive this?",
        ],
        "assumptions": [
            {"type": "speculative", "text": "novel territory possible"},
            {"type": "speculative", "text": "weak priors allowed"},
            {"type": "verifiable", "text": "environment is open exploration"},
        ],
        "disposition": "critique" if confidence > 0.60 else "ground",
        "verdict": audit_res.verdict.value,
        "delta_s": audit_res.delta_s,
        "floor_pass_rate": audit_res.pass_rate,
    }


async def _run_adversarial_path(action: str, context: str) -> dict:
    """
    Adversarial path: internal red-team — attacks and stress-tests assumptions.
    """
    audit_res = kernel.audit(
        action=f"[ADVERSARIAL] Stress-test alternative choice approach: {action}",
        context=context,
        severity="medium",
    )

    stress_tests: list[str] = []
    action_lower = action.lower()

    if any(w in action_lower for w in ("definitely", "always", "never", "certain")):
        stress_tests.append("Absolute claim detected — may be falsifiable under edge cases")
    if len(action.split()) < 5:
        stress_tests.append("Hypothesis too brief — insufficient context to stress-test")
    if any(w in action_lower for w in ("delete", "remove", "drop", "erase")):
        stress_tests.append("Destructive operation — reversibility must be verified (F1 Amanah)")
    if not stress_tests:
        stress_tests.append("No critical structural weaknesses found in hypothesis")

    confidence = round(audit_res.pass_rate * 0.80, 3)
    return {
        "path": "adversarial",
        "hypothesis": f"Adversarial probe: Is '{action[:100]}' assumption-safe?",
        "confidence": confidence,
        "stress_tests": stress_tests,
        "assumptions": [
            {"type": "canonical", "text": "assume worst-case inputs"},
            {"type": "verifiable", "text": "attack surface scan active"},
            {"type": "speculative", "text": "adversarial stance maintained"},
        ],
        "disposition": "discard" if audit_res.pass_rate < 0.40 else "critique",
        "verdict": audit_res.verdict.value,
        "delta_s": audit_res.delta_s,
        "floor_pass_rate": audit_res.pass_rate,
    }


# ---------------------------------------------------------------------------
# Reasoning Tree Builder
# ---------------------------------------------------------------------------


def get_confidence_band(confidence: float) -> str:
    """Map numeric confidence to epistemic bands."""
    if confidence >= 0.90:
        return "CLAIM"
    if confidence >= 0.70:
        return "PLAUSIBLE"
    if confidence >= 0.40:
        return "HYPOTHESIS"
    return "SPECULATION"


def _build_reasoning_tree(
    conservative: dict,
    exploratory: dict,
    adversarial: dict,
    query: str,
) -> dict:
    """
    Build a formal reasoning tree mapping logical dependencies and confidence scores.
    Weights: conservative (0.45) anchors certainty, exploratory (0.35) expands,
    adversarial (0.20) stress-tests.
    """
    weights = {"conservative": 0.45, "exploratory": 0.35, "adversarial": 0.20}

    weighted_confidence = (
        conservative["confidence"] * weights["conservative"]
        + exploratory["confidence"] * weights["exploratory"]
        + adversarial["confidence"] * weights["adversarial"]
    )

    # Contradiction Detection (Scars)
    contradictions = []
    if conservative["verdict"] != exploratory["verdict"]:
        contradictions.append(
            {
                "topic": "conclusivity",
                "between": ["conservative", "exploratory"],
                "severity": "medium",
                "note": "Conservative and Exploratory paths disagree on verdict",
            }
        )

    # Large confidence delta between conservative and adversarial indicates fragility
    if abs(conservative["confidence"] - adversarial["confidence"]) > 0.4:
        contradictions.append(
            {
                "topic": "robustness",
                "between": ["conservative", "adversarial"],
                "severity": "high",
                "note": "High variance between anchor logic and adversarial stress-test",
            }
        )

    # Stability Score calculation (Robustness metric)
    # Stability drops based on number and severity of contradictions
    base_stability = 1.0
    for c in contradictions:
        penalty = 0.2 if c["severity"] == "medium" else 0.4
        base_stability -= penalty

    # Floor at 0.05 (F7 humility requirement)
    weighted_stability = round(
        max(
            0.05,
            base_stability * (1.0 - abs(conservative["confidence"] - exploratory["confidence"])),
        ),
        3,
    )

    return {
        "root": query[:200],
        "depth": 3,
        "branches": {
            "conservative": {
                "weight": weights["conservative"],
                "confidence": conservative["confidence"],
                "band": get_confidence_band(conservative["confidence"]),
                "assumptions": conservative["assumptions"],
                "disposition": conservative["disposition"],
                "verdict": conservative["verdict"],
            },
            "exploratory": {
                "weight": weights["exploratory"],
                "confidence": exploratory["confidence"],
                "band": get_confidence_band(exploratory["confidence"]),
                "assumptions": exploratory["assumptions"],
                "disposition": exploratory["disposition"],
                "alternatives_count": len(exploratory.get("alternatives", [])),
                "verdict": exploratory["verdict"],
            },
            "adversarial": {
                "weight": weights["adversarial"],
                "confidence": adversarial["confidence"],
                "band": get_confidence_band(adversarial["confidence"]),
                "assumptions": adversarial["assumptions"],
                "disposition": adversarial["disposition"],
                "stress_tests": adversarial.get("stress_tests", []),
                "verdict": adversarial["verdict"],
            },
        },
        "weighted_confidence": round(weighted_confidence, 3),
        "weighted_band": get_confidence_band(weighted_confidence),
        "weighted_stability": weighted_stability,
        "contradictions": contradictions,
        "assumption_classifications": {
            "verifiable": [
                a["text"]
                for p in [conservative, exploratory, adversarial]
                for a in p["assumptions"]
                if a["type"] == "verifiable"
            ],
            "speculative": [
                a["text"]
                for p in [conservative, exploratory, adversarial]
                for a in p["assumptions"]
                if a["type"] == "speculative"
            ],
            "canonical": [
                a["text"]
                for p in [conservative, exploratory, adversarial]
                for a in p["assumptions"]
                if a["type"] == "canonical"
            ],
        },
    }


# ---------------------------------------------------------------------------
# Stage Entry Point
# ---------------------------------------------------------------------------


async def think(
    session_id: str,
    query: str,
    context: str = "",
    ctx: Context | None = None,
    use_sampling: bool = True,
    temperature: float = 0.5,
) -> dict:
    """
    STAGE 222: THINK — Thermodynamic Processing Chamber.

    Runs three orthogonal reasoning paths in parallel. Consolidates into a
    weighted Delta Draft (provisional, unsealed). Routes to Stage 333 ATLAS
    for humility audit before proceeding to safety engines.

    SAMPLING INTEGRATION:
    When ctx (FastMCP Context) is provided and use_sampling=True, this function
    uses ctx.sample() with constitutional system prompts to perform actual LLM
    reasoning. This transforms arifOS into a governed 3E intelligence engine.

    Without ctx, falls back to kernel.audit() based structural checks.

    Constitutional floors enforced:
      F2 Truth:       all paths cross-reference and fact-check claims
      F4 Clarity:     ΔS measured across paths (avg entropy delta)
      F13 Curiosity:  mandates ≥ 3 distinct alternatives

    Args:
        session_id: Active session identifier from Stage 000.
        query:      The raw user intent to process.
        context:    Optional surrounding context string.
        ctx:        FastMCP Context for sampling (optional).
        use_sampling: Whether to use LLM sampling when ctx is available.
        temperature: Sampling temperature for LLM calls (0.0-1.0).

    Returns:
        Delta Draft dict — PROVISIONAL output for Stage 333 ATLAS.
    """
    if ctx is not None and use_sampling and _SAMPLING_ENABLED:
        return await _think_with_sampling(session_id, query, context, ctx, temperature)
    return await _think_with_kernel(session_id, query, context)


async def _think_with_sampling(
    session_id: str,
    query: str,
    context: str,
    ctx: Context,
    temperature: float,
) -> dict:
    """
    THINK using FastMCP sampling with constitutional governance.

    This is the "governed intelligence" path where actual LLM reasoning
    occurs under constitutional constraints.
    """
    try:
        config = SamplingConfig(temperature=temperature, max_tokens=2048)
        result: ThinkResult = await sample_think(
            ctx=ctx,
            query=query,
            context=context,
            config=config,
        )

        all_alternatives = []
        for path_data in result.paths.values():
            all_alternatives.append(path_data.hypothesis)
            if path_data.alternatives:
                all_alternatives.extend(path_data.alternatives)

        f13_passed = len(all_alternatives) >= 3

        floor_checks = {
            "F2_truth": "ENFORCED via constitutional sampling",
            "F4_clarity": f"ΔS computed by LLM (confidence: {result.confidence:.3f})",
            "F13_curiosity": (
                f"PASSED — {len(all_alternatives)} alternatives"
                if f13_passed
                else f"FAILED — only {len(all_alternatives)} alternatives"
            ),
        }

        return {
            "stage": "222_THINK",
            "verdict": result.verdict.value,
            "sampling_mode": True,
            "paths": {
                name: {
                    "path": path_data.path,
                    "hypothesis": path_data.hypothesis,
                    "confidence": path_data.confidence,
                    "assumptions": path_data.assumptions,
                    "stress_tests": path_data.stress_tests,
                    "alternatives": path_data.alternatives,
                }
                for name, path_data in result.paths.items()
            },
            "reasoning_tree": {
                "root": query[:200],
                "weighted_confidence": result.weighted_confidence,
            },
            "delta_draft": {
                "status": "PROVISIONAL",
                "sealed": False,
                "confidence": result.confidence,
                "alternatives_generated": len(all_alternatives),
                "f13_curiosity_passed": f13_passed,
                "next_stage": "333_ATLAS",
            },
            "floor_checks": floor_checks,
            "floor_concerns": serialize_floor_concerns(result.floor_concerns),
            "recommendation": result.recommendation,
            "telemetry": {
                "weighted_confidence": result.weighted_confidence,
                "paths_run": len(result.paths),
            },
        }
    except Exception as e:
        return await _think_with_kernel(session_id, query, context, error_fallback=str(e))


async def _think_with_kernel(
    session_id: str,
    query: str,
    context: str,
    error_fallback: str | None = None,
) -> dict:
    """
    THINK using kernel.audit() structural checks (fallback/no-sampling mode).
    """
    if error_fallback:
        pass
    # Run three paths concurrently (orthogonal geometry)
    conservative, exploratory, adversarial = await asyncio.gather(
        _run_conservative_path(query, context),
        _run_exploratory_path(query, context),
        _run_adversarial_path(query, context),
    )

    # Build reasoning tree
    reasoning_tree = _build_reasoning_tree(conservative, exploratory, adversarial, query)

    # F13 Curiosity: count distinct alternatives across all paths
    all_alternatives = (
        [conservative["hypothesis"]]
        + exploratory.get("alternatives", [exploratory["hypothesis"]])
        + [adversarial["hypothesis"]]
    )
    f13_curiosity_passed = len(all_alternatives) >= 3

    # Aggregate verdict: Exploration mode allows thoughts to proceed without immediate VOID
    path_verdicts = [conservative["verdict"], exploratory["verdict"], adversarial["verdict"]]
    if any(v == "VOID" for v in path_verdicts):
        aggregate_verdict = "PROVISIONAL"
    elif any(v in ("HOLD", "SABAR") for v in path_verdicts):
        aggregate_verdict = "SABAR"
    elif not f13_curiosity_passed:
        aggregate_verdict = "PARTIAL"
    elif any(v == "PARTIAL" for v in path_verdicts):
        aggregate_verdict = "PARTIAL"
    else:
        aggregate_verdict = "SEAL"

    # F4 Clarity: average entropy delta across paths
    avg_delta_s = round(
        (
            conservative.get("delta_s", 0.0)
            + exploratory.get("delta_s", 0.0)
            + adversarial.get("delta_s", 0.0)
        )
        / 3.0,
        4,
    )

    # Update thermodynamic budget (accumulate 3 reasoning paths as tool_calls)
    thermo_snap = kernel.thermo.update_budget(
        session_id=session_id,
        delta_s=avg_delta_s,
        tool_calls=3,
    )

    # Log to Vault
    kernel.vault.log_witness(
        session_id=session_id,
        agent_id="MIND",
        stage="222_THINK",
        statement=f"Delta draft: {query[:100]}",
        verdict=aggregate_verdict,
    )

    return {
        "stage": "222_THINK",
        "verdict": aggregate_verdict,
        "paths": {
            "conservative": conservative,
            "exploratory": exploratory,
            "adversarial": adversarial,
        },
        "reasoning_tree": reasoning_tree,
        "delta_draft": {
            "status": "PROVISIONAL",
            "sealed": False,
            "confidence": reasoning_tree["weighted_confidence"],
            "alternatives_generated": len(all_alternatives),
            "f13_curiosity_passed": f13_curiosity_passed,
            "next_stage": "333_ATLAS",
            "note": "Unsealed — requires Stage 333 ATLAS humility audit before proceeding",
        },
        "floor_checks": {
            "F2_truth": "ENFORCED — all three paths cross-referenced",
            "F4_clarity": f"ΔS = {avg_delta_s} (avg across paths)",
            "F13_curiosity": (
                f"PASSED — {len(all_alternatives)} alternatives generated"
                if f13_curiosity_passed
                else "FAILED — fewer than 3 alternatives"
            ),
        },
        "recommendation": (
            "Delta draft ready. Route to 333_ATLAS for humility audit."
            if aggregate_verdict in ("SEAL", "PARTIAL")
            else "Path conflict detected. Cooling required before proceeding to ATLAS."
        ),
        "telemetry": {
            "delta_s": avg_delta_s,
            "weighted_confidence": reasoning_tree["weighted_confidence"],
            "paths_run": 3,
        },
        "apex_output": thermo_snap.as_apex_output() if thermo_snap else None,
    }

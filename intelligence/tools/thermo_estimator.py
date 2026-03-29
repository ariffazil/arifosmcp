"""
arifosmcp.intelligence/tools/thermo_estimator.py — Resource Cost & Constitutional Metrics
================================================================================

Modules:
    - cost_estimator(): Thermodynamic and financial cost projection
    - coherence_score(): Lyapunov-like stability metric (ΔΩΨ)
    - shadow_prices(): Lagrange multiplier estimation for floor constraints
    - shannon_entropy(): Information-theoretic entropy H(X)
    - entropy_delta(): ΔS calculation for F4 Clarity

DITEMPA BUKAN DIBERI — Forged, Not Given [ΔΩΨ | ARIF]
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Any

from arifosmcp.intelligence.tools.aclip_base import PSUTIL_OK, psutil


# =============================================================================
# ENTROPY — Information-Theoretic Foundations (F4 Clarity)
# =============================================================================


def shannon_entropy(text: str, base: float = 2.0) -> float:
    """
    Compute Shannon entropy H(X) of a text.

    H(X) = -Σ p(x) log₂ p(x)

    Measures uncertainty/information content.
    - High entropy → random, unpredictable (confusion)
    - Low entropy → ordered, predictable (clarity)

    Args:
        text: Input string
        base: Logarithm base (2 = bits, e = nats, 10 = dits)

    Returns:
        entropy: Shannon entropy in specified units

    Example:
        "AAAA" → very low entropy (predictable)
        "ABCD" → higher entropy (random)
    """
    if not text:
        return 0.0

    # Count character frequencies
    counts = Counter(text)
    total = len(text)

    # Calculate probability distribution
    probs = [count / total for count in counts.values()]

    # Shannon entropy: H = -Σ p(x) log(p(x))
    entropy = -sum(p * math.log(p, base) for p in probs if p > 0)

    return round(entropy, 4)


def entropy_delta(
    input_text: str,
    output_text: str,
    base: float = 2.0,
) -> dict[str, Any]:
    """
    Compute entropy change ΔS = H_output - H_input.

    F4 Clarity requires ΔS ≤ 0 (clarity must increase, not decrease).

    If ΔS > 0: The system added confusion (entropy increased)
    If ΔS = 0: No change in information content
    If ΔS < 0: Clarity improved (entropy decreased)

    Args:
        input_text: Input to the system
        output_text: Output from the system
        base: Logarithm base for entropy calculation

    Returns:
        delta_s: H_output - H_input (must be ≤ 0 for F4)
        h_input: Entropy of input
        h_output: Entropy of output
        verdict: PASS | FAIL (based on ΔS ≤ 0)
        clarity_gain: Absolute reduction in entropy
    """
    h_input = shannon_entropy(input_text, base)
    h_output = shannon_entropy(output_text, base)
    delta_s = h_output - h_input

    verdict = "PASS" if delta_s <= 0 else "FAIL"
    clarity_gain = abs(delta_s) if delta_s < 0 else 0.0

    return {
        "delta_s": round(delta_s, 4),
        "h_input": round(h_input, 4),
        "h_output": round(h_output, 4),
        "verdict": verdict,
        "verdict_code": "SEAL" if verdict == "PASS" else "VOID",
        "clarity_gain": round(clarity_gain, 4),
        "interpretation": (
            f"Entropy {'reduced' if delta_s <= 0 else 'increased'} by {abs(delta_s):.4f} bits. "
            f"F4 Clarity {'PASSED' if verdict == 'PASS' else 'FAILED'}."
        ),
    }


# =============================================================================
# LANDONAUTIC LANDMARK CALCULATOR (not currently exported but available)
# =============================================================================


def landauer_limit(bits_erased: float, temperature_kelvin: float = 300.0) -> dict[str, float]:
    """
    Compute minimum thermodynamic cost of erasing information.

    Landauer Limit: E_min = k_B * T * ln(2) per bit erased

    At room temperature (300K):
        E_min ≈ 2.9 × 10⁻²¹ J per bit

    Args:
        bits_erased: Number of bits being reset to zero
        temperature_kelvin: System temperature in Kelvin

    Returns:
        energy_joules: Minimum energy required in Joules
        energy_ztograms: Equivalent in zeptograms (10⁻²¹ g)
    """
    k_boltzmann = 1.380649e-23  # J/K
    ln2 = 0.6931471805599453

    energy_joules = k_boltzmann * temperature_kelvin * ln2 * bits_erased
    energy_ztograms = energy_joules / 1e-21  # Convert to zeptograms

    return {
        "bits_erased": bits_erased,
        "temperature_K": temperature_kelvin,
        "energy_joules": energy_joules,
        "energy_zeptograms": energy_ztograms,
        "efficiency_target": "reversible" if energy_joules < 1e-18 else "dissipative",
    }


# =============================================================================
# COHERENCE METRIC — Lyapunov-like Stability Function
# =============================================================================


def coherence_score(
    delta_bundle: dict | None = None,
    omega_bundle: dict | None = None,
    agi_vote: float = 1.0,
    asi_vote: float = 1.0,
    apex_vote: float = 1.0,
    contradiction_ratio: float = 0.0,
    drift_from_baseline: float = 0.0,
    previous_coherence: float | None = None,
) -> dict[str, Any]:
    """
    Lyapunov-like coherence metric for constitutional stability.

    V(state) decreases → system stabilizing
    V(state) increases → system destabilizing

    The 3 dimensions of coherence:
    1. Goal consistency — how aligned are reasoning outputs with intent?
    2. Identity stability — how much has the system drifted from baseline?
    3. Cross-module agreement — do AGI, ASI, APEX agree?

    Args:
        delta_bundle: AGI reasoning output (optional)
        omega_bundle: ASI safety output (optional)
        agi_vote: AGI SEAL vote [0, 1]
        asi_vote: ASI SEAL vote [0, 1]
        apex_vote: APEX SEAL vote [0, 1]
        contradiction_ratio: Fraction of reasoning steps with contradictions [0, 1]
        drift_from_baseline: How much telos/behavior has shifted from session baseline [0, 1]
        previous_coherence: Coherence from previous step for delta calculation

    Returns:
        coherence: Geometric mean of the 3 coherence dimensions
        coherence_delta: Change from previous coherence (negative = stabilizing)
        verdict: STABLE | MARGINAL | UNSTABLE
        lyapunov: Dict with energy function details
    """
    # Dimension 1: Goal Consistency
    # = 1 - contradiction_ratio (no contradictions = perfect consistency)
    goal_consistency = max(0.0, 1.0 - contradiction_ratio)

    # Dimension 2: Identity Stability
    # = 1 - drift (no drift = perfect stability)
    identity_stability = max(0.0, 1.0 - drift_from_baseline)

    # Dimension 3: Cross-Module Agreement (Trinity consensus)
    # Geometric mean of trinity votes — if any vote is 0, agreement is 0
    trinity_agreement = (agi_vote * asi_vote * apex_vote) ** (1.0 / 3.0)

    # Coherence: Product of 3 dimensions (multiplicative, like G = A × P × X × E²)
    coherence = goal_consistency * identity_stability * trinity_agreement

    # Lyapunov analysis
    if previous_coherence is not None and previous_coherence > 0:
        coherence_delta = coherence - previous_coherence
        lyapunov_sign = (
            "DECREASING"
            if coherence_delta < 0
            else ("INCREASING" if coherence_delta > 0 else "STABLE")
        )
        is_lyapunov_stable = coherence_delta <= 0
    else:
        coherence_delta = None
        lyapunov_sign = "INITIAL"
        is_lyapunov_stable = None

    # Constitutional verdict
    if coherence >= 0.8:
        verdict = "STABLE"
        verdict_code = "SEAL"
    elif coherence >= 0.5:
        verdict = "MARGINAL"
        verdict_code = "SABAR"
    else:
        verdict = "UNSTABLE"
        verdict_code = "VOID"

    return {
        "coherence": round(coherence, 4),
        "coherence_delta": round(coherence_delta, 4) if coherence_delta is not None else None,
        "dimensions": {
            "goal_consistency": round(goal_consistency, 4),
            "identity_stability": round(identity_stability, 4),
            "trinity_agreement": round(trinity_agreement, 4),
        },
        "lyapunov": {
            "sign": lyapunov_sign,
            "is_stable": is_lyapunov_stable,
            "energy_change": "REDUCING"
            if lyapunov_sign == "DECREASING"
            else ("RAISING" if lyapunov_sign == "INCREASING" else "INITIAL"),
        },
        "verdict": verdict,
        "verdict_code": verdict_code,
        "omega_0": 0.04,  # F7 Humility band
    }


def shadow_prices(
    floor_scores: dict[str, float] | None = None,
    thresholds: dict[str, float] | None = None,
) -> dict[str, Any]:
    """
    Estimate Lagrange multipliers for constitutional floor constraints.

    λᵢ > 0 → floor i is binding (system lives exactly at that boundary)
    λᵢ = 0 → floor i is slack (system has margin)

    This is the shadow price of each constraint:
    How much would the objective improve if the constraint relaxed by 1 unit?

    Args:
        floor_scores: Dict of floor_name -> score (e.g., {"F2": 0.99, "F5": 1.2})
        thresholds: Dict of floor_name -> minimum threshold (e.g., {"F2": 0.99, "F5": 1.0})

    Returns:
        shadows: Dict of floor_name -> shadow_price (λᵢ)
        binding_floors: List of floors with λᵢ > 0
        slack_floors: List of floors with λᵢ = 0
        total_constraint_pressure: Sum of all shadow prices
    """
    if thresholds is None:
        thresholds = {
            "F1": 1.0,  # Amanah: Boolean (reversible)
            "F2": 0.99,  # Truth: τ ≥ 0.99
            "F3": 0.95,  # Tri-Witness: W³ ≥ 0.95
            "F4": 0.0,  # Clarity: ΔS ≤ 0 (negative = good)
            "F5": 1.0,  # Peace²: P² ≥ 1.0
            "F6": 0.95,  # Empathy: κᵣ ≥ 0.95
            "F7": 0.03,  # Humility: Ω₀ ∈ [0.03, 0.05] — use lower bound
            "F8": 0.80,  # Genius: G ≥ 0.80
            "F9": 0.30,  # Anti-Hantu: C_dark < 0.30
            "F10": 1.0,  # Ontology: Boolean (role lock)
            "F11": 1.0,  # Authority: Boolean (verified)
            "F12": 0.85,  # Injection: Defense ≥ 0.85
            "F13": 1.0,  # Sovereign: Human approval required
        }

    if floor_scores is None:
        floor_scores = {}

    shadows = {}
    binding_floors = []
    slack_floors = []

    for floor, threshold in thresholds.items():
        score = floor_scores.get(floor, threshold)  # Default to threshold if not provided
        distance = score - threshold

        if distance <= 0:
            # At or below threshold → binding constraint (λᵢ > 0)
            # Shadow price = how far below threshold
            shadow = abs(distance) + 0.01  # Small positive floor
            binding_floors.append(floor)
        else:
            # Above threshold → slack constraint (λᵢ = 0)
            shadow = 0.0
            slack_floors.append(floor)

        shadows[floor] = round(shadow, 4)

    total_pressure = round(sum(shadows.values()), 4)

    return {
        "shadows": shadows,
        "binding_floors": binding_floors,
        "slack_floors": slack_floors,
        "total_constraint_pressure": total_pressure,
        "binding_count": len(binding_floors),
        "slack_count": len(slack_floors),
        "interpretation": (
            f"{len(binding_floors)} floors binding, {len(slack_floors)} floors slack. "
            f"Total pressure: {total_pressure}"
        ),
    }


def cost_estimator(
    action_description: str = "",
    estimated_cpu_percent: float = 0.0,
    estimated_ram_mb: float = 0.0,
    estimated_io_mb: float = 0.0,
    operation_type: str = "compute",
    token_count: int | None = None,
    compute_seconds: float | None = None,
    storage_gb: float | None = None,
    api_calls: int | None = None,
    provider: str = "openai",
    model: str = "gpt-4",
    operation: str | None = None,  # Architectural alias
) -> dict[str, Any]:
    """
    Predicts the thermodynamic and financial cost of a proposed action.
    Serves as a proxy for entropy change (ΔS).
    """
    # Use 'operation' if provided, otherwise 'operation_type'
    actual_op_type = operation if operation is not None else operation_type
    # ---------------------------------------------------------------------------
    # 1. Financial Costs (USD)
    # ---------------------------------------------------------------------------
    pricing = {
        "openai": {
            "gpt-4": {"input_per_1k": 0.03, "output_per_1k": 0.06},
            "gpt-4-turbo": {"input_per_1k": 0.01, "output_per_1k": 0.03},
            "gpt-3.5-turbo": {"input_per_1k": 0.0005, "output_per_1k": 0.0015},
            "text-embedding-3-small": {"per_1k": 0.00002},
            "text-embedding-3-large": {"per_1k": 0.00013},
        },
        "anthropic": {
            "claude-3-opus": {"input_per_1k": 0.015, "output_per_1k": 0.075},
            "claude-3-sonnet": {"input_per_1k": 0.003, "output_per_1k": 0.015},
            "claude-3-haiku": {"input_per_1k": 0.00025, "output_per_1k": 0.00125},
        },
        "gemini": {
            "gemini-pro": {"input_per_1k": 0.0005, "output_per_1k": 0.0015},
            "gemini-ultra": {"input_per_1k": 0.001, "output_per_1k": 0.003},
        },
    }

    infra_costs = {
        "compute_per_hour": 0.05,
        "storage_per_gb_month": 0.02,
        "egress_per_gb": 0.09,
    }

    costs = {
        "llm_cost_usd": 0.0,
        "compute_cost_usd": 0.0,
        "storage_cost_usd": 0.0,
        "api_cost_usd": 0.0,
        "total_usd": 0.0,
    }

    if actual_op_type == "llm" and token_count:
        p_pricing = pricing.get(provider, {})
        m_pricing = p_pricing.get(model, {"input_per_1k": 0.03, "output_per_1k": 0.06})
        in_tokens = int(token_count * 0.7)
        out_tokens = int(token_count * 0.3)
        costs["llm_cost_usd"] = round(
            (in_tokens / 1000) * m_pricing.get("input_per_1k", 0.03)
            + (out_tokens / 1000) * m_pricing.get("output_per_1k", 0.06),
            6,
        )
    elif actual_op_type == "embedding" and token_count:
        p_pricing = pricing.get(provider, {})
        m_pricing = p_pricing.get(model, {"per_1k": 0.00002})
        costs["llm_cost_usd"] = round((token_count / 1000) * m_pricing.get("per_1k", 0.00002), 6)

    if compute_seconds:
        compute_cost = (compute_seconds / 3600) * infra_costs["compute_per_hour"]
        costs["compute_cost_usd"] = round(compute_cost, 6)
    if storage_gb:
        storage_cost = storage_gb * infra_costs["storage_per_gb_month"]
        costs["storage_cost_usd"] = round(storage_cost, 6)
    if api_calls:
        costs["api_cost_usd"] = round(api_calls * 0.0001, 6)

    costs["total_usd"] = round(sum(v for k, v in costs.items() if k != "total_usd"), 6)

    # ---------------------------------------------------------------------------
    # 2. Thermodynamic Score (Entropy Proxy)
    # ---------------------------------------------------------------------------
    logical_cores = 1
    max_ram_mb = 16384.0
    if PSUTIL_OK:
        logical_cores = psutil.cpu_count(logical=True) or 1
        max_ram_mb = psutil.virtual_memory().total / (1024 * 1024)

    max_cpu_pct = 100.0 * logical_cores
    max_io_mb = 1000.0

    norm_cpu = min(estimated_cpu_percent / max_cpu_pct, 1.0)
    norm_ram = min(estimated_ram_mb / max_ram_mb, 1.0)
    norm_io = min(estimated_io_mb / max_io_mb, 1.0)

    cost_score = round((0.5 * norm_cpu) + (0.3 * norm_ram) + (0.2 * norm_io), 4)

    return {
        "status": "ok",
        "action_description": action_description,
        "operation_type": actual_op_type,
        "costs": costs,
        "hardware_context": {
            "cores": logical_cores,
            "max_cpu_percent": max_cpu_pct,
            "total_ram_mb": round(max_ram_mb, 0),
        },
        "thermodynamic": {
            "cost_score": cost_score,
            "risk_band": (
                "red" if cost_score >= 0.8 else ("amber" if cost_score >= 0.5 else "green")
            ),
        },
        "apex_input": {
            "tokens": token_count or 0,
            "tool_calls": api_calls or 0,
        },
    }

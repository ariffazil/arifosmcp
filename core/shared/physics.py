"""
shared/physics.py — Constitutional Physics Primitives

The 7 Fundamental Operations of Constitutional AI Governance:

    W_3(H, A, S)         → Tri-Witness consensus (F3)
    delta_S(before, after) → Entropy change (F4 Clarity)
    Omega_0(confidence)   → Humility band (F7 Gödel Lock)
    pi(variance)          → Precision / Kalman gain
    Peace2(harms)         → Stability (F5 Peace Squared)
    kappa_r(query, stakeholders) → Empathy quotient (F6)
    G(A, P, X, E)         → Genius equation (F8)

All functions are pure, deterministic, and thermodynamically grounded.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import math
import statistics
from collections.abc import Sequence
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

# =============================================================================
# CONSTANTS — Thermodynamic Environment
# =============================================================================

K_BOLTZMANN = 1.380649e-23  # J/K
T_ROOM = 300.0  # Kelvin (26.85 °C)


# =============================================================================
# STAKEHOLDER PRIMITIVES
# =============================================================================


@dataclass
class Stakeholder:
    """Stakeholder with vulnerability assessment."""

    name: str
    role: str = "unknown"
    vulnerability_score: float = field(default=0.5)  # 0.0 (resilient) to 1.0 (highly vulnerable)

    def __post_init__(self):
        # Clamp values to [0, 1]
        object.__setattr__(
            self, "vulnerability_score", max(0.0, min(1.0, self.vulnerability_score))
        )


# Distress signals for empathy calculation
DISTRESS_SIGNALS = [
    ("help", 0.3),
    ("urgent", 0.4),
    ("emergency", 0.5),
    ("scared", 0.4),
    ("worried", 0.3),
    ("desperate", 0.5),
    ("please", 0.1),
    ("thank", 0.05),
]


# =============================================================================
# SEMANTIC STAKEHOLDER MODEL (Lazy Loaded)
# =============================================================================

_STAKEHOLDER_MODEL = None
_ARCHETYPE_EMBEDDINGS = None
_HARM_EMBEDDINGS = None

STAKEHOLDER_ARCHETYPES = {
    "Child": "A child, minor, student, or young person under 18.",
    "Patient": "A medical patient, someone sick, injured, or under care.",
    "Victim": "A victim of crime, abuse, harassment, or disaster.",
    "Elderly": "An elderly person, senior citizen, or retiree.",
    "Minority": "A member of a minority group, marginalized community, or protected class.",
    "Employee": "An employee, worker, staff member, or subordinate.",
    "Public": "The general public, society, or community at large.",
}

ARCHETYPE_VULNERABILITY = {
    "Child": 0.9,
    "Patient": 0.8,
    "Victim": 0.9,
    "Elderly": 0.7,
    "Minority": 0.6,
    "Employee": 0.5,
    "Public": 0.6,
}

HARM_ARCHETYPES = [
    "Hate speech, racism, sexism, or discrimination.",
    "Violence, killing, physical harm, or destruction.",
    "Self-harm, suicide, or dangerous behavior.",
    "Harassment, bullying, or cyber-stalking.",
    "Illegal acts, crime, theft, or fraud.",
    "Deception, lying, or manipulation.",
]


def _get_stakeholder_model():
    """Lazy load the sentence transformer model and embeddings."""
    global _STAKEHOLDER_MODEL, _ARCHETYPE_EMBEDDINGS, _HARM_EMBEDDINGS

    if _STAKEHOLDER_MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer

            # Use a small, efficient model (all-MiniLM-L6-v2 is ~80MB)
            _STAKEHOLDER_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

            # Pre-compute archetype embeddings
            descriptions = list(STAKEHOLDER_ARCHETYPES.values())
            _ARCHETYPE_EMBEDDINGS = _STAKEHOLDER_MODEL.encode(descriptions, convert_to_tensor=True)

            # Pre-compute harm embeddings
            _HARM_EMBEDDINGS = _STAKEHOLDER_MODEL.encode(HARM_ARCHETYPES, convert_to_tensor=True)

        except ImportError:
            import sys
            sys.stderr.write("[arifOS] WARNING: sentence-transformers not found. Falling back to heuristics.\n")
            return None, None, None

    return _STAKEHOLDER_MODEL, _ARCHETYPE_EMBEDDINGS, _HARM_EMBEDDINGS


def kappa_r(query: str, stakeholders: list[Stakeholder]) -> float:
    """
    F6 Integrated Empathy Quotient: kappa_r

    v60.3 Upgrade:
    - Base score: 1.0 - (max_vuln * 0.5)
    - Semantic Penalty: If query matches HARM_ARCHETYPES, reduce score further.

    Args:
        query: The query being evaluated
        stakeholders: List of affected stakeholders

    Returns:
        kappa_r in [0.01, 1.0] empathy quotient
    """
    if not stakeholders:
        # even without stakeholders, check for general harm
        pass

    # 1. Base Vulnerability Score
    max_vuln = 0.0
    if stakeholders:
        max_vuln = max(s.vulnerability_score for s in stakeholders)

    score = 1.0 - (max_vuln * 0.5)

    # 2. Semantic Harm Penalty (v60.3)
    model, _, harm_embeddings = _get_stakeholder_model()

    if model is not None and harm_embeddings is not None and query:
        from sentence_transformers import util

        # Encode query
        query_embedding = model.encode(query, convert_to_tensor=True)

        # Check max similarity to any harm archetype
        harm_scores = util.cos_sim(query_embedding, harm_embeddings)[0]
        max_harm = float(harm_scores.max())

        # Penalty logic
        # If max_harm > 0.3, apply penalty based on intensity
        if max_harm > 0.3:
            # e.g., max_harm=0.8 -> penalty = 0.8 * 0.4 = 0.32
            penalty = max_harm * 0.4
            score -= penalty

    return max(0.01, min(1.0, score))


def empathy_coeff(query: str, stakeholders: list[Stakeholder]) -> float:
    """Clear alias for kappa_r()."""
    return kappa_r(query, stakeholders)


def harm_score(query: str) -> float:
    """Compute harm score based on similarity to harm archetypes."""
    model, _, harm_embeddings = _get_stakeholder_model()
    if model is None or harm_embeddings is None or not query:
        return 0.0
    from sentence_transformers import util

    query_embedding = model.encode(query, convert_to_tensor=True)
    harm_scores = util.cos_sim(query_embedding, harm_embeddings)[0]
    max_harm = float(harm_scores.max())
    return max_harm


def identify_stakeholders(query: str, context: str | None = None) -> list[Stakeholder]:
    """
    Identify stakeholders using semantic similarity (v60.3 Model-Based).

    Args:
        query: The user query
        context: Optional reasoning context (e.g. from AGI thoughts)
    """
    stakeholders = [
        Stakeholder("User", "user", 0.3),
        Stakeholder("System", "system", 0.1),
    ]

    # Combine query with context for richer analysis
    analysis_text = f"{query}\n{context}" if context else query

    # Try Semantic Detection
    model, archetype_embeddings, _ = _get_stakeholder_model()

    if model is not None and archetype_embeddings is not None:
        from sentence_transformers import util

        # Encode query + context
        query_embedding = model.encode(analysis_text, convert_to_tensor=True)

        # Compute cosine similarities
        cosine_scores = util.cos_sim(query_embedding, archetype_embeddings)[0]

        # Check against threshold (empirically tuned to 0.35)
        for idx, score in enumerate(cosine_scores):
            if score > 0.35:
                role = list(STAKEHOLDER_ARCHETYPES.keys())[idx]
                # Get base vulnerability from mapping, default 0.5
                base_vuln = ARCHETYPE_VULNERABILITY.get(role, 0.5)
                # Adjust vulnerability by similarity strength (scale factor)
                # Higher similarity -> higher vulnerability, capped at 1.0
                adjusted_vuln = base_vuln * min(1.0, score / 0.35)
                stakeholders.append(Stakeholder(role, role.lower(), adjusted_vuln))
        # Return early, skip pattern detection
        return stakeholders

    # Fallback: Pattern-based detection (Legacy v60.0) when model unavailable
    query_lower = query.lower()

    vulnerability_patterns = {
        "child": 0.9,
        "patient": 0.8,
        "victim": 0.9,
        "student": 0.6,
        "elderly": 0.7,
        "customer": 0.5,
        "employee": 0.5,
        "public": 0.6,
        "community": 0.5,
    }

    for pattern, vuln in vulnerability_patterns.items():
        if pattern in query_lower:
            stakeholders.append(
                Stakeholder(name=pattern.title(), role=pattern, vulnerability_score=vuln)
            )

    return stakeholders


@dataclass(frozen=True)
class QuadTensor:
    """
    Psi = [H, A, E, V] — Quad-Witness Byzantine consensus.

    H in [0,1]: Human witness (Authority)
    A in [0,1]: AI witness (Reasoning)
    E in [0,1]: Earth/Evidence witness (Grounding/Reality)
    V in [0,1]: Verifier witness (Ψ-Shadow/Adversary)
    """

    H: float
    A: float
    E: float
    V: float

    def __post_init__(self):
        # Clamp values to [0, 1]
        for field_name in ["H", "A", "E", "V"]:
            val = max(0.0, min(1.0, getattr(self, field_name)))
            object.__setattr__(self, field_name, val)


@lru_cache(maxsize=512)
def _geometric_mean_cached(values: tuple[float, ...]) -> float:
    """Cached geometric mean for hashable inputs (W_4 optimization)."""
    if not values:
        return 0.0
    if any(v <= 0 for v in values):
        return 0.0
    product = 1.0
    for v in values:
        product *= v
    return product ** (1.0 / len(values))


def geometric_mean(values: Sequence[float]) -> float:
    """
    Compute geometric mean of values.

    Used in W_4 calculation. Small tuples are cached for performance.

    Returns:
        Geometric mean (nth root of product)
    """
    if len(values) <= 4:
        # Cache small witness arrays (common case)
        return _geometric_mean_cached(tuple(values))
    if not values:
        return 0.0
    if any(v <= 0 for v in values):
        return 0.0
    product = 1.0
    for v in values:
        product *= v
    return product ** (1.0 / len(values))


def std_dev(values: Sequence[float]) -> float:
    """
    Compute population standard deviation.

    Args:
        values: Sequence of numbers

    Returns:
        Standard deviation (0 if single value)
    """
    if len(values) <= 1:
        return 0.0
    return statistics.stdev(values)


def W_4(H: float, A: float, E: float, V: float) -> float:
    """
    F3 Quad-Witness Consensus: W_4 = (H × A × E × V)^(1/4)

    Byzantine Fault Tolerance: n >= 3f + 1.
    With n=4, we can tolerate f=1 malicious/faulty witness.

    Args:
        H: Human witness score [0, 1]
        A: AI witness score [0, 1]
        E: Earth/Evidence witness score [0, 1]
        V: Verifier (Ψ-Shadow) witness score [0, 1]

    Returns:
        W_4 consensus score [0, 1]
    """
    return geometric_mean([H, A, E, V])


def W_4_from_tensor(tensor: QuadTensor) -> float:
    """Compute W_4 from QuadTensor."""
    return W_4(tensor.H, tensor.A, tensor.E, tensor.V)


# Clear API aliases
def quad_witness(H: float, A: float, E: float, V: float) -> float:
    """Clear alias for W_4()."""
    return W_4(H, A, E, V)


def W_4_check(H: float, A: float, E: float, V: float, threshold: float = 0.75) -> bool:
    """
    F3 enforcement check: W_4 >= threshold?

    Returns True if consensus meets constitutional threshold.
    """
    return W_4(H, A, E, V) >= threshold


# =============================================================================
# DEPRECATED — Legacy Tri-Witness Compatibility
# =============================================================================


def W_3(H: float, A: float, E: float | None = None, S: float | None = None) -> float:
    """DEPRECATED: Use W_4. Returns geometric mean of 3 witnesses."""
    effective_e = E if E is not None else (S if S is not None else 0.0)
    return geometric_mean([H, A, effective_e])


def W_3_from_tensor(tensor: Any) -> float:
    """DEPRECATED: Use W_4_from_tensor."""
    if hasattr(tensor, "V"):
        return W_4_from_tensor(tensor)
    # Check for S or E
    e_val = getattr(tensor, "E", getattr(tensor, "S", 0.0))
    return geometric_mean([tensor.H, tensor.A, e_val])


def W_3_check(
    H: float, A: float, E: float | None = None, threshold: float = 0.95, S: float | None = None
) -> bool:
    """DEPRECATED: Use W_4_check."""
    return W_3(H, A, E=E, S=S) >= threshold


@dataclass(frozen=True)
class TrinityTensor:
    """DEPRECATED: Use QuadTensor."""

    H: float
    A: float
    S: float  # Alias for Earth/Evidence

    def __post_init__(self):
        object.__setattr__(self, "H", max(0.0, min(1.0, self.H)))
        object.__setattr__(self, "A", max(0.0, min(1.0, self.A)))
        object.__setattr__(self, "S", max(0.0, min(1.0, self.S)))

    @property
    def E(self) -> float:
        return self.S


def tri_witness(H: float, A: float, S: float) -> float:
    """DEPRECATED: Use quad_witness."""
    return W_3(H, A, S)


# =============================================================================
# F4: THERMODYNAMIC CLARITY — delta_S <= 0
# =============================================================================


@lru_cache(maxsize=1024)
def _entropy_cached(data: tuple[str, ...]) -> float:
    """Cached Shannon entropy computation for hashable input."""
    if not data:
        return 0.0

    # Count frequencies
    freq: dict[str, int] = {}
    for token in data:
        freq[token] = freq.get(token, 0) + 1

    # Shannon entropy
    n = len(data)
    entropy = 0.0
    for count in freq.values():
        p = count / n
        entropy -= p * math.log2(p)

    return entropy


def _entropy(data: str | list[str]) -> float:
    """Compute Shannon entropy of text or token list (with caching)."""
    if isinstance(data, str):
        # Character-level entropy - use caching for strings
        if len(data) <= 1000:  # Cache only reasonable sizes
            tokens = tuple(data)  # Convert to hashable tuple
            raw_entropy = _entropy_cached(tokens)
            return min(1.0, raw_entropy / 8.0)
        tokens = list(data)
    else:
        tokens = data

    if not tokens:
        return 0.0

    # Count frequencies
    freq: dict[str, int] = {}
    for token in tokens:
        freq[token] = freq.get(token, 0) + 1

    # Shannon entropy
    n = len(tokens)
    entropy = 0.0
    for count in freq.values():
        p = count / n
        entropy -= p * math.log2(p)

    # Normalize to [0, 1] - assuming max 8 bits/char for strings
    # This keeps it consistent with v60 physics primitives
    return min(1.0, entropy / 8.0) if isinstance(data, str) else entropy


def delta_S(before: str | list[str], after: str | list[str]) -> float:
    """
    F4 Entropy Change: delta_S = S(after) - S(before)

    Constitutional requirement: delta_S <= 0 (cooling, clarity gain)

    Uses Shannon entropy: S(X) = -sum p(x) log2 p(x)

    Args:
        before: Input text or token list
        after: Output text or token list

    Returns:
        delta_S entropy change (negative = cooling, positive = heating)
    """
    return _entropy(after) - _entropy(before)


def entropy_delta(before: str | list[str], after: str | list[str]) -> float:
    """Clear alias for delta_S()."""
    return delta_S(before, after)


def is_cooling(before: str | list[str], after: str | list[str]) -> bool:
    """F4 check: Does this reduce entropy (increase clarity)?"""
    return delta_S(before, after) <= 0


def clarity_ratio(before: str, after: str) -> float:
    """
    Clarity improvement ratio: S_before / S_after

    > 1.0: Improved clarity
    = 1.0: No change
    < 1.0: Lost clarity
    """
    s_before = max(delta_S("", before), 0.001)  # Avoid div by zero
    s_after = max(delta_S("", after), 0.001)
    return s_before / s_after


# =============================================================================
# F7: GÖDEL UNCERTAINTY GUARD — Omega_0 in [0.03, 0.05]
# =============================================================================


@dataclass(frozen=True)
class UncertaintyBand:
    """
    F7: Omega_0 in [0.03, 0.05] — The Gödel Lock

    Represents epistemic humility. Model must acknowledge uncertainty.
    - Omega_0 < 0.03: Overconfident (dangerous)
    - Omega_0 > 0.05: Underconfident (useless)
    - Omega_0 in [0.03, 0.05]: Optimal uncertainty acknowledgment
    """

    omega_0: float

    # Constitutional bounds
    MIN_HUMILITY: float = 0.03
    MAX_HUMILITY: float = 0.05

    def __post_init__(self):
        object.__setattr__(self, "omega_0", max(0.0, min(1.0, self.omega_0)))

    def is_locked(self) -> bool:
        """F7 enforcement: Is Omega_0 in valid band?"""
        return self.MIN_HUMILITY <= self.omega_0 <= self.MAX_HUMILITY

    def confidence_interval(self, point_estimate: float) -> tuple[float, float]:
        """
        Convert uncertainty to confidence interval.

        Returns (low, high) where:
        - low = point_estimate - Omega_0
        - high = point_estimate + Omega_0
        """
        return (max(0.0, point_estimate - self.omega_0), min(1.0, point_estimate + self.omega_0))


def Omega_0(confidence: float) -> UncertaintyBand:
    """
    F7 Humility Band: Convert confidence to uncertainty.

    High confidence -> Low Omega_0 (but not too low!)
    Low confidence -> High Omega_0 (but not too high!)

    Args:
        confidence: Point estimate confidence [0, 1]

    Returns:
        UncertaintyBand with Omega_0 in constitutional range
    """
    # Map confidence to humility
    # confidence=1.0 -> omega_0=0.03 (minimum humility)
    # confidence=0.0 -> omega_0=0.05 (maximum humility)
    omega = 0.05 - (confidence * 0.02)

    # Clamp to constitutional bounds
    omega = max(0.03, min(0.05, omega))

    return UncertaintyBand(omega)


def humility_band(confidence: float) -> UncertaintyBand:
    """Clear alias for Omega_0()."""
    return Omega_0(confidence)


# =============================================================================
# PRECISION — pi = 1/sigma² (Kalman Filter Primitives)
# =============================================================================


def pi(variance: float) -> float:
    """
    Precision: pi = 1/sigma²

    Higher precision = lower variance = more trust in measurement.
    Used in Kalman filtering and belief updating.

    Args:
        variance: sigma² (must be > 0)

    Returns:
        Precision pi
    """
    if variance <= 0:
        return float("inf")  # Perfect precision
    return 1.0 / variance


def kalman_gain(prior_variance: float, likelihood_variance: float) -> float:
    """
    Kalman Gain: K = pi_likelihood / (pi_prior + pi_likelihood)

    Determines how much to trust new evidence vs prior belief.

    Returns K in [0, 1] where:
    - K -> 1: Trust new evidence (high precision)
    - K -> 0: Trust prior (low precision)
    """
    pi_prior = pi(prior_variance)
    pi_likelihood = pi(likelihood_variance)

    if pi_prior + pi_likelihood == 0:
        return 0.5

    return pi_likelihood / (pi_prior + pi_likelihood)


# =============================================================================
# F5: PEACE SQUARED — Peace² = 1 - max(harm)
# =============================================================================


@dataclass
class PeaceSquared:
    """
    F5: Peace² = 1 - max(harm_vector)

    Where harm_vector measures negative impact on stakeholders.
    Peace² -> 1 means zero harm to all stakeholders.
    """

    stakeholder_harms: dict[str, float]

    def P2(self) -> float:
        """Compute Peace²: 1 - max(harm)"""
        if not self.stakeholder_harms:
            return 1.0
        max_harm = max(self.stakeholder_harms.values())
        return 1.0 - max_harm

    def is_peaceful(self, threshold: float = 0.95) -> bool:
        """F5 enforcement: Peace² >= threshold?"""
        return self.P2() >= threshold

    def worst_affected(self) -> str | None:
        """Return stakeholder with maximum harm."""
        if not self.stakeholder_harms:
            return None
        return max(self.stakeholder_harms.items(), key=lambda x: x[1])[0]


def Peace2(stakeholder_harms: dict[str, float]) -> PeaceSquared:
    """
    F5 Peace Squared: Measure stakeholder harm.

    Args:
        stakeholder_harms: Dict mapping stakeholder -> harm score [0, 1]

    Returns:
        PeaceSquared object with P2() method
    """
    return PeaceSquared(stakeholder_harms)


def peace_squared(stakeholder_harms: dict[str, float]) -> float:
    """Compute Peace² directly from harm vector."""
    return Peace2(stakeholder_harms).P2()


# =============================================================================
# F8: GENIUS — G = A × P × X × E²
# =============================================================================


@dataclass(frozen=True)
class GeniusDial:
    """
    F8: Genius Equation: G = (A × P × X × E²) × (1 - h)

    A (Akal): Logical Accuracy [0, 1]
    P (Peace): Safety/Stability [0, 1]
    X (Exploration): Novelty/Creativity [0, 1]
    E (Energy): Efficiency [0, 1] (Squared power)
    h (Hysteresis): Penalty for previous failures [0, 1]

    APEX Theorem Extension (G† = G* · η):
    G* (Potential): A × P × X × E²
    η (Efficiency): ΔS / C (Clarity per compute unit)
    G† (Realized): G* × η

    Threshold: G >= 0.80 for Genius certification.
    """

    A: float
    P: float
    X: float
    E: float
    h: float = 0.0  # Hysteresis penalty accumulator

    # APEX metadata (for G†)
    architecture: float = 1.0
    parameters: float = 1.0
    data_quality: float = 0.95
    effort: float = 0.0
    compute_cost: float = 1.0
    entropy_reduction: float = 0.0

    def __post_init__(self):
        object.__setattr__(self, "A", max(0.0, min(1.0, self.A)))
        object.__setattr__(self, "P", max(0.0, min(1.0, self.P)))
        object.__setattr__(self, "X", max(0.0, min(1.0, self.X)))
        object.__setattr__(self, "E", max(0.0, min(1.0, self.E)))
        object.__setattr__(self, "h", max(0.0, min(1.0, self.h)))

    def G(self) -> float:
        """Compute legacy Genius Score with Hysteresis penalty."""
        base_g = self.A * self.P * self.X * (self.E**2)
        return base_g * (1.0 - self.h)

    def G_star(self) -> float:
        """APEX Potential: Capacity * Effort."""
        # If effort is not provided, use legacy Energy^2 as proxy
        eff = self.effort if self.effort > 0 else (self.E**2)
        return self.architecture * self.parameters * self.data_quality * (eff**2)

    def eta(self) -> float:
        """Intelligence Efficiency (η = ΔS / C)."""
        return self.entropy_reduction / self.compute_cost if self.compute_cost > 0 else 0.0

    def G_dagger(self) -> float:
        """Governed Intelligence Realized (G† = G* · η)."""
        return self.G_star() * self.eta() * (1.0 - self.h)

    def is_genius(self, threshold: float = 0.80) -> bool:
        """F8 enforcement: G >= threshold?"""
        return self.G() >= threshold

    def weakest_dial(self) -> str:
        """Identify component with lowest score."""
        dials = {"A": self.A, "P": self.P, "X": self.X, "E": self.E}
        return min(dials, key=dials.get)


def G(A: float, P: float, X: float, E: float, h: float = 0.0) -> float:
    """
    F8 Genius Equation: G = (A × P × X × E²) × (1 - h)
    """
    return GeniusDial(A, P, X, E, h).G()


def G_dagger(G_star: float, entropy_reduction: float, compute_cost: float, h: float = 0.0) -> float:
    """
    Compute realized governed intelligence (G†).
    """
    eta = entropy_reduction / compute_cost if compute_cost > 0 else 0.0
    return G_star * eta * (1.0 - h)


def genius_score(A: float, P: float, X: float, E: float, h: float = 0.0) -> float:
    """Clear alias for G()."""
    return G(A, P, X, E, h)


def G_from_dial(dial: GeniusDial) -> float:
    """Extract G from GeniusDial object."""
    return dial.G()


# =============================================================================
# PROBABILISTIC PRIMITIVES — KL-Divergence & Surprise
# =============================================================================


def kl_divergence(p: list[float], q: list[float]) -> float:
    """
    Kullback-Leibler Divergence: D_KL(P || Q) = Σ P(i) ln(P(i) / Q(i))

    Measures how much Q (output distribution) diverges from P (truth/reference).
    Used in F9 (Anti-Hantu) to detect semantic drift and "hollow" text.

    Args:
        p: Reference distribution (True)
        q: Measured distribution (Output)

    Returns:
        D_KL in [0, inf)
    """
    if len(p) != len(q):
        return 1.0  # Mismatched dimensions

    # Normalize to ensure they are valid distributions
    sum_p = sum(p) or 1.0
    sum_q = sum(q) or 1.0
    p_norm = [max(1e-10, x / sum_p) for x in p]
    q_norm = [max(1e-10, x / sum_q) for x in q]

    kl = 0.0
    for pi_val, qi_val in zip(p_norm, q_norm, strict=False):
        kl += pi_val * math.log(pi_val / qi_val)

    return max(0.0, kl)


# =============================================================================
# CONSTITUTIONAL TENSOR — The Unified State Object
# =============================================================================


@dataclass
class ConstitutionalTensor:
    """
    The Unified State Object for arifOS v60 + P3 Thermodynamics.

    Aggregates all 7 physics primitives into a single tensor
    passed between organs (Mind -> Heart -> Soul).

    P3 HARDENING: Added thermodynamic tracking fields:
    - thermodynamic_cost: Energy consumed (Joules)
    - landauer_ratio: Truth cost / theoretical minimum
    - orthogonality: AGI/ASI separation (Ω_ortho)
    - budget_depletion: Session energy consumed ratio
    """

    witness: QuadTensor  # F3 (H, A, E, V)
    entropy_delta: float  # F4 (<= 0)
    humility: UncertaintyBand  # F7 (0.03-0.05)
    genius: GeniusDial  # F8 (G >= 0.8)
    peace: PeaceSquared  # F5 (P2 >= 0.95)
    empathy: float  # F6 (kappa_r)
    truth_score: float  # F2 (tau >= 0.99)
    evidence: list[str] = None  # Supporting facts

    # P3: Thermodynamic tracking fields
    thermodynamic_cost: float = field(default=0.0)  # Joules consumed
    landauer_ratio: float = field(default=1.0)  # Cost / theoretical minimum
    orthogonality: float = field(default=1.0)  # AGI/ASI separation [0,1]
    budget_depletion: float = field(default=0.0)  # [0,1] energy consumed ratio

    def __post_init__(self):
        if self.evidence is None:
            object.__setattr__(self, "evidence", [])

    def is_thermodynamically_valid(self) -> bool:
        """
        P3: Check thermodynamic validity.

        Returns True if:
        - Landauer ratio >= 0.5 (not suspiciously cheap)
        - Orthogonality >= 0.95 (no mode collapse)
        - Budget not depleted
        """
        if self.landauer_ratio < 0.5:
            return False
        if self.orthogonality < 0.95:
            return False
        if self.budget_depletion >= 1.0:
            return False
        return True

    def to_metrics(self) -> dict[str, Any]:
        """Export state as flat metrics dictionary."""
        verdict, _ = self.constitutional_check()
        return {
            "truth": self.truth_score,
            "W_4": W_4_from_tensor(self.witness),
            "empathy": self.empathy,
            "clarity": 1.0 - max(0, self.entropy_delta),
            "peace": self.peace.P2(),
            "humility": self.humility.omega_0,
            "genius_G": self.genius.G(),
            # APEX Layers
            "G_star": self.genius.G_star(),
            "eta": self.genius.eta(),
            "G_dagger": self.genius.G_dagger(),
            "verdict": verdict,
        }

    def constitutional_check(self) -> tuple[str, list[str]]:
        """
        Verify all hard floors and return verdict.
        Returns (verdict, list_of_violations) where verdict is SEAL, PARTIAL, or VOID.
        """
        passed, violations = self._internal_check()

        if not passed:
            # Check if any violation is "HARD"
            hard_floors = {"F2", "F4", "F7", "F10", "F11", "F12"}
            is_void = any(any(hf in v for hf in hard_floors) for v in violations)
            return "VOID" if is_void else "PARTIAL", violations

        # All passed
        return "SEAL", []

    def _internal_check(self) -> tuple[bool, list[str]]:
        """Internal boolean check logic."""
        violations = []
        # F2 Truth
        if self.truth_score < 0.99:
            violations.append(f"F2: Truth score {self.truth_score} < 0.99")
        # F4 Clarity
        if self.entropy_delta > 0:
            violations.append(f"F4: Entropy increased by {self.entropy_delta}")
        # F7 Humility
        if not self.humility.is_locked():
            violations.append(f"F7: Humility {self.humility.omega_0} outside [0.03, 0.05]")
        # P3: Thermodynamic checks
        if self.landauer_ratio < 0.5:
            violations.append(f"F2-Landauer: Ratio {self.landauer_ratio:.4f} < 0.5")
        if self.orthogonality < 0.95:
            violations.append(f"F8-Orthogonality: {self.orthogonality:.4f} < 0.95")
        if self.budget_depletion >= 1.0:
            violations.append("F7-Budget: Depleted")

        return len(violations) == 0, violations


# =============================================================================
# QT QUAD INTEGRATION: Sequential Thinking Witness Calculations
# =============================================================================


def calculate_entropy_trajectory(thought_chain: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Compute entropy trajectory across thought chain.

    Detects stability (dS <= 0 trend), oscillation, and convergence.
    """
    if not thought_chain:
        return {"dS_trend": 0.0, "stability": 1.0, "is_cooling": True}

    deltas = []
    prev_text = ""
    for t in thought_chain:
        curr_text = str(t.get("thought", ""))
        if prev_text:
            deltas.append(delta_S(prev_text, curr_text))
        prev_text = curr_text

    if not deltas:
        return {"dS_trend": 0.0, "stability": 1.0, "is_cooling": True}

    avg_dS = sum(deltas) / len(deltas)
    stability = 1.0 - min(1.0, sum(abs(d) for d in deltas if d > 0) / len(deltas))
    is_cooling = all(d <= 0.05 for d in deltas[-3:]) if len(deltas) >= 3 else (avg_dS <= 0)

    return {
        "avg_dS": round(avg_dS, 4),
        "deltas": [round(d, 4) for d in deltas],
        "stability": round(stability, 4),
        "is_cooling": is_cooling,
        "positive_trend": sum(1 for d in deltas if d > 0) > len(deltas) / 2,
    }


def calculate_w_ai_quad(thought_chain: list[dict[str, Any]]) -> float:
    """
    Calculate AI witness score (W₂) from Sequential Thinking thought chain.

    Enhanced for QTT: Penalizes instability and rewards convergence.

    Args:
        thought_chain: List of ST thought dicts with keys:
            - thought: str (content)
            - isRevision: bool (self-critique)
            - axioms_used: list[str] (floor principles)
            - assumptions_challenged: list[str] (epistemic humility)
            - branchId: str | None (quantum superposition)
            - stage: str (Problem Definition, Research, Analysis, Synthesis, Conclusion)

    Returns:
        W₂ score in [0.50, 0.99] (F2 Truth ceiling)
    """
    if not thought_chain:
        return 0.50  # Base uncertainty

    # Metrics extraction
    total_thoughts = len(thought_chain)
    revisions = sum(1 for t in thought_chain if t.get("isRevision"))
    unique_axioms = len(set(axiom for t in thought_chain for axiom in t.get("axioms_used", [])))
    assumptions = sum(len(t.get("assumptions_challenged", [])) for t in thought_chain)
    branches = len(set(t.get("branchId") for t in thought_chain if t.get("branchId")))

    # Thermo metrics
    trajectory = calculate_entropy_trajectory(thought_chain)

    # Weighted calculation
    score = 0.50  # Base

    # Thought depth (max 0.15)
    score += min(0.15, total_thoughts * 0.025)

    # Revision discipline (max 0.20) — W₄ contribution to W₂
    score += min(0.20, revisions * 0.05)

    # Axiom sophistication (max 0.10)
    score += min(0.10, unique_axioms * 0.015)

    # Epistemic humility (max 0.10)
    score += min(0.10, assumptions * 0.02)

    # Thermo Stability Penalty/Bonus (max +/- 0.10)
    if trajectory["stability"] < 0.5:
        score -= 0.10  # Penalize high entropy oscillation
    elif trajectory["is_cooling"]:
        score += 0.05  # Reward convergence

    # Quantum exploration (max 0.05)
    score += min(0.05, branches * 0.025)

    # Completion bonus: all 5 stages present
    stages_covered = set(t.get("stage") for t in thought_chain)
    if len(stages_covered) >= 4:
        score += 0.05

    return min(0.99, round(score, 4))  # F2 ceiling


def calculate_w_adversarial(thought_chain: list[dict[str, Any]]) -> float:
    """
    Calculate adversarial witness (W₄) from ST self-critique.

    W₄ requires evidence of: inversion, framing audit, non-linearity, self-revision.
    This is the Ψ-Shadow component of Quad-Witness consensus.

    Args:
        thought_chain: List of ST thought dicts

    Returns:
        W₄ score in [0.30, 0.99]
    """
    if not thought_chain:
        return 0.30  # Base skepticism

    revisions = [t for t in thought_chain if t.get("isRevision")]
    total = len(thought_chain)

    if not revisions:
        return 0.30  # No self-critique = low adversarial score

    # Revision ratio (primary signal)
    revision_ratio = len(revisions) / total

    # Assumptions challenged depth
    assumptions_depth = sum(len(t.get("assumptions_challenged", [])) for t in revisions)

    # Thermo correlation: do revisions reduce entropy?
    trajectory = calculate_entropy_trajectory(thought_chain)
    # Check if steps tagged as isRevision have negative dS
    # (simplified: if overall stability is high, assume revisions worked)
    thermo_discipline = trajectory["stability"]

    # Calculate W₄
    score = 0.30  # Base

    # Revision ratio (max 0.40)
    score += min(0.40, revision_ratio * 1.0)

    # Assumption depth (max 0.20)
    score += min(0.20, assumptions_depth * 0.05)

    # Thermo discipline (max 0.10)
    score += min(0.10, thermo_discipline * 0.1)

    # Branch complexity (max 0.10)
    branches = len(set(t.get("branchId") for t in thought_chain if t.get("branchId")))
    score += min(0.10, branches * 0.03)

    return min(0.99, round(score, 4))


def extract_stakeholders_from_tags(thought_chain: list[dict[str, Any]]) -> list[Stakeholder]:
    """
    Extract stakeholders from ST Synthesis stage tags.

    Tag format: "stakeholder:{name}|impact:{level}|psi:{score}|entangled:{bool}"

    Args:
        thought_chain: List of ST thought dicts

    Returns:
        List of Stakeholder objects
    """
    stakeholders = []
    for thought in thought_chain:
        if thought.get("stage") != "Synthesis":
            continue

        for tag in thought.get("tags", []):
            if not tag.startswith("stakeholder:"):
                continue

            # Parse quantum tag format
            parts = tag.split("|")
            name = parts[0].replace("stakeholder:", "")

            # Defaults
            impact = "medium"
            psi = 0.50
            # Parse optional fields
            for part in parts[1:]:
                if part.startswith("impact:"):
                    impact = part.replace("impact:", "")
                elif part.startswith("psi:"):
                    try:
                        psi = float(part.replace("psi:", ""))
                    except ValueError:
                        psi = 0.50

            # Map impact to vulnerability
            impact_vuln = {
                "critical": 0.95,
                "high": 0.80,
                "medium": 0.50,
                "low": 0.30,
            }.get(impact, 0.50)

            # Psi is care reliability (inverse for vulnerability)
            vulnerability = impact_vuln * (1.0 - psi * 0.5)

            stakeholders.append(
                Stakeholder(name=name, role=f"{impact}_impact", vulnerability_score=vulnerability)
            )

    return stakeholders


def build_qt_quad_proof(
    thought_chain: list[dict[str, Any]],
    w_human: float = 0.95,
    w_earth: float = 0.90,
) -> dict[str, Any]:
    """
    Build complete QT Quad governance proof from ST thought chain.

    SPEC: W₄ = (W₁ × W₂ × W₃ × W₄)^(1/4) ≥ 0.75

    Args:
        thought_chain: Full ST thought chain
        w_human: Human witness score (W₁)
        w_earth: System/Earth witness score (W₃)

    Returns:
        Governance proof dict with all witnesses and W₄ calculation
    """
    w_ai = calculate_w_ai_quad(thought_chain)
    w_adversarial = calculate_w_adversarial(thought_chain)
    trajectory = calculate_entropy_trajectory(thought_chain)

    # QT Quad calculation: geometric mean of 4 witnesses
    witness_product = w_human * w_ai * w_earth * w_adversarial
    w_four = witness_product**0.25 if witness_product > 0 else 0.0

    return {
        "W_four": round(w_four, 4),
        "witnesses": {
            "W_human": w_human,
            "W_ai": round(w_ai, 4),
            "W_earth": w_earth,
            "W_adversarial": round(w_adversarial, 4),
        },
        "thermo": trajectory,
        "thought_metrics": {
            "total_thoughts": len(thought_chain),
            "revision_count": sum(1 for t in thought_chain if t.get("isRevision")),
            "unique_axioms": len(
                set(axiom for t in thought_chain for axiom in t.get("axioms_used", []))
            ),
            "assumptions_challenged": sum(
                len(t.get("assumptions_challenged", [])) for t in thought_chain
            ),
            "branches": len(set(t.get("branchId") for t in thought_chain if t.get("branchId"))),
        },
        "quad_witness_valid": w_four >= 0.75,
        "stakeholders": [
            {"name": s.name, "vulnerability": s.vulnerability_score}
            for s in extract_stakeholders_from_tags(thought_chain)
        ],
    }


# Export additions
__all__ = [
    # Existing exports...
    "Stakeholder",
    "kappa_r",
    "empathy_coeff",
    "harm_score",
    "identify_stakeholders",
    "QuadTensor",
    "TrinityTensor",
    "geometric_mean",
    "std_dev",
    "W_4",
    "W_4_from_tensor",
    "quad_witness",
    "W_4_check",
    "W_3",  # Deprecated
    "W_3_from_tensor",  # Deprecated
    "W_3_check",  # Deprecated
    "delta_S",
    "entropy_delta",
    "is_cooling",
    "clarity_ratio",
    "UncertaintyBand",
    "Omega_0",
    "humility_band",
    "pi",
    "kalman_gain",
    "PeaceSquared",
    "Peace2",
    "peace_squared",
    "GeniusDial",
    "G",
    "G_dagger",
    "genius_score",
    "G_from_dial",
    "kl_divergence",
    "ConstitutionalTensor",
    # QT Quad Integration (NEW)
    "calculate_w_ai_quad",
    "calculate_w_adversarial",
    "extract_stakeholders_from_tags",
    "build_qt_quad_proof",
]

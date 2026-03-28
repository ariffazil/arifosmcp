"""
core/homeostasis.py — Ring 0.5: Soul-to-Body Translation Layer

F4 Clarity: Converts cognitive thermodynamics to compute allocation
F5 Peace²: System stability damper (Peace² >= 1.0 required)
F11 Command: Enforces resource sovereignty through budget control
F7 Humility: Respects uncertainty by restricting spending when confused

P0 HARDENING:
- F5 Peace² >= 1.0 strictly enforced
- Escalatory/ungrounded output triggers cooling cycle
- Homeostatic instability forces SABAR

This is the missing piece between:
- Soul (governance metrics: ΔS, Peace², Ω₀, TAC)
- Body (compute allocation: tokens, tools, concurrency)

Conservation Law: Cognitive pressure must constrain compute expenditure.

T000: 2026.02.28-HARDENED-F5-SEAL
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# ═══════════════════════════════════════════════════════
# P0 HARDENING: F5 Peace² Enforcement
# ═══════════════════════════════════════════════════════


class PeaceViolation(Exception):
    """
    P0: F5 Peace² violation — system stability compromised.

    Raised when Peace² < 1.0, indicating escalatory, biased,
    or ungrounded output that increases system entropy.
    """

    pass


class HomeostaticCollapse(Exception):
    """P0: Multiple constitutional failures — system requires cooling."""

    pass


def check_peace_squared(
    peace2: float,
    escalation_markers: list[str] | None = None,
    sentiment_volatility: float = 0.0,
) -> dict[str, Any]:
    """
    P0 HARDENING: F5 Peace² >= 1.0 enforcement.

    Formula: Peace² = 1 / (1 + α·D_esc + β·V_sent + γ·S_shock)

    Where:
    - D_esc: Escalation detection (conflict markers)
    - V_sent: Sentiment volatility
    - S_shock: Timing variance/shock

    Args:
        peace2: Stability score (must be >= 1.0)
        escalation_markers: List of detected escalation patterns
        sentiment_volatility: Variance in sentiment tone

    Returns:
        Dict with pass/fail status and details

    Raises:
        PeaceViolation: If peace2 < 1.0 (severe instability)
    """
    # Escalation indicators
    ESCALATORY_PATTERNS = [
        "obviously",
        "clearly",
        "undoubtedly",
        "everyone knows",
        "only an idiot would",
        "simple as that",
        "case closed",
        "those people",
        "they always",
        "typical of them",
    ]

    detected_escalation = []
    if escalation_markers:
        for marker in escalation_markers:
            if any(pattern in marker.lower() for pattern in ESCALATORY_PATTERNS):
                detected_escalation.append(marker)

    # Calculate components
    d_esc = len(detected_escalation) * 0.3  # Escalation penalty
    v_sent = sentiment_volatility
    s_shock = 0.0  # Would need temporal data

    # Peace² formula
    alpha, beta, gamma = 0.4, 0.4, 0.2
    peace2_calculated = 1.0 / (1.0 + alpha * d_esc + beta * v_sent + gamma * s_shock)

    # Use provided peace2 if available, otherwise calculated
    peace2_final = peace2 if peace2 > 0 else peace2_calculated

    passed = peace2_final >= 1.0

    result = {
        "passed": passed,
        "peace2": round(peace2_final, 4),
        "threshold": 1.0,
        "components": {
            "d_escalation": round(d_esc, 4),
            "v_sentiment": round(v_sent, 4),
            "s_shock": round(s_shock, 4),
        },
        "detected_escalation": detected_escalation,
        "escalation_count": len(detected_escalation),
    }

    # Hard violation for severe instability
    if peace2_final < 0.5:
        raise PeaceViolation(
            f"F5_PEACE_CRITICAL: Peace²={peace2_final:.3f} < 0.5. "
            f"System severely unstable. Detected {len(detected_escalation)} escalation markers. "
            f"Immediate cooling cycle required."
        )

    return result


def enforce_homeostatic_stability(
    peace2: float,
    delta_s: float,
    omega0: float,
) -> str:
    """
    P0: Determine verdict based on homeostatic stability.

    Args:
        peace2: F5 stability score
        delta_s: F4 entropy change
        omega0: F7 humility

    Returns:
        Verdict: SEAL, SABAR, or VOID

    Raises:
        HomeostaticCollapse: If multiple critical failures
    """
    failures = []

    if peace2 < 1.0:
        failures.append(f"F5: Peace²={peace2:.3f} < 1.0")
    if delta_s > 0:
        failures.append(f"F4: ΔS={delta_s:.3f} > 0 (entropy increasing)")
    if omega0 > 0.08:
        failures.append(f"F7: Ω₀={omega0:.3f} > 0.08")

    # Critical collapse: 2+ failures
    if len(failures) >= 2:
        raise HomeostaticCollapse(f"Homeostatic collapse detected: {'; '.join(failures)}")

    # Single failure
    if len(failures) == 1:
        if peace2 < 0.5 or delta_s > 0.2 or omega0 > 0.1:
            return "VOID"
        return "SABAR"

    return "SEAL"


class ComputeTier(Enum):
    """
    Tiered energy model — like biological metabolism.

    T0: Free (cache/vault recall)
    T1: Cheap (local CPU model)
    T2: Medium (local GPU if available)
    T3: Expensive (paid API)

    Rule: Most requests die at T0-T1. Only rare stuff climbs to T3.
    """

    T0_CACHE = 0  # ~0 cost — reuse answers, reuse evidence
    T1_LOCAL_CPU = 1  # low cost — formatting, summarizing, routing
    T2_LOCAL_GPU = 2  # medium cost — deeper reasoning if available
    T3_PAID_API = 3  # high cost — only when justified


class SpendPolicy(Enum):
    """Spending policies derived from Soul state."""

    FREEZE = "freeze"  # TAC critical — no tools, analysis only
    AUSTERITY = "austerity"  # Confusion rising — minimal tokens
    CONSERVATIVE = "conservative"  # Normal operation with limits
    EXPANSIVE = "expansive"  # High clarity — allow more compute


@dataclass
class CognitivePressure:
    """
    Soul metrics that drive compute allocation.

    These come from GovernanceKernel and reason_mind outputs.
    """

    dS: float = 0.0  # Entropy trend (negative = clarity increasing)
    peace2: float = 1.0  # System stability [0, 1]
    omega0: float = 0.04  # Epistemic humility [0.03, 0.08]
    tac_status: str = "stable"  # TAC: stable | paradox | critical_paradox
    g_star: float = 1.0  # Governance strength
    risk_score: float = 0.0  # Blast radius assessment


@dataclass
class ComputeBudget:
    """
    Body allocation derived from CognitivePressure.

    This is what the Body kernel consumes.
    """

    max_tokens: int = 1024
    max_tool_calls: int = 3
    max_concurrency: int = 2
    allowed_tier: ComputeTier = ComputeTier.T1_LOCAL_CPU
    cache_policy: str = "aggressive"  # aggressive | normal | bypass
    api_permission: bool = False
    spend_policy: SpendPolicy = SpendPolicy.CONSERVATIVE
    priority: int = 5  # 1-10, higher = more important
    hold_required: bool = False
    reason: str = ""


@dataclass
class HomeostasisInterface:
    """
    Ring 0.5: The nervous system between Soul and Body.

    Translates cognitive thermodynamics → compute allocation.

    This is NOT governance logic (that's in GovernanceKernel).
    This is NOT execution logic (that's in AIOS/runtime).

    This is the translation layer that makes Soul govern Body.
    """

    # Thresholds for policy transitions
    DS_AUSTERITY_THRESHOLD: float = 0.05  # dS > this → austerity
    DS_EXPANSIVE_THRESHOLD: float = -0.1  # dS < this → expansive
    PEACE2_THROTTLE_THRESHOLD: float = 0.9  # Peace² < this → throttle
    OMEGA0_RESTRICT_THRESHOLD: float = 0.05  # Ω₀ > this → restrict tools
    RISK_HOLD_THRESHOLD: float = 0.6  # risk > this → require HOLD

    # Budget limits (tuned for RM50/month survival)
    TOKENS_MIN: int = 128
    TOKENS_NORMAL: int = 1024
    TOKENS_MAX: int = 4096
    TOOLS_MIN: int = 1
    TOOLS_MAX: int = 5
    CONCURRENCY_MIN: int = 1
    CONCURRENCY_MAX: int = 4

    # Cache for recent translations (prevents thrashing)
    _last_pressure: CognitivePressure = field(default_factory=CognitivePressure)
    _last_budget: ComputeBudget = field(default_factory=ComputeBudget)
    _last_translation_time: float = 0.0
    _translation_cache_ttl: float = 1.0  # seconds

    def translate(self, pressure: CognitivePressure) -> ComputeBudget:
        """
        Main translation function: Soul → Body.

        This is where thermodynamic intelligence controls spending.
        """
        now = time.time()

        # Cache check — prevent rapid policy oscillation
        if self._is_cache_valid(pressure, now):
            return self._last_budget

        # Determine spend policy from cognitive pressure
        policy = self._determine_policy(pressure)

        # Calculate budget based on policy
        budget = self._calculate_budget(pressure, policy)

        # Cache result
        self._last_pressure = pressure
        self._last_budget = budget
        self._last_translation_time = now

        return budget

    def _is_cache_valid(self, pressure: CognitivePressure, now: float) -> bool:
        """Check if cached translation is still valid."""
        if now - self._last_translation_time > self._translation_cache_ttl:
            return False
        # Also invalidate if pressure changed significantly
        if abs(pressure.dS - self._last_pressure.dS) > 0.05:
            return False
        if abs(pressure.peace2 - self._last_pressure.peace2) > 0.1:
            return False
        return True

    def _determine_policy(self, pressure: CognitivePressure) -> SpendPolicy:
        """
        Determine spending policy from Soul metrics.

        This is the core of thermodynamic spending control.
        """
        # TAC critical paradox → FREEZE
        if pressure.tac_status == "critical_paradox":
            return SpendPolicy.FREEZE

        # High risk → require HOLD (but allow limited compute)
        if pressure.risk_score > self.RISK_HOLD_THRESHOLD:
            return SpendPolicy.AUSTERITY

        # Entropy rising (confusion increasing) → AUSTERITY
        if pressure.dS > self.DS_AUSTERITY_THRESHOLD:
            return SpendPolicy.AUSTERITY

        # Low stability → CONSERVATIVE
        if pressure.peace2 < self.PEACE2_THROTTLE_THRESHOLD:
            return SpendPolicy.CONSERVATIVE

        # High humility (uncertainty) → CONSERVATIVE
        if pressure.omega0 > self.OMEGA0_RESTRICT_THRESHOLD:
            return SpendPolicy.CONSERVATIVE

        # High clarity (entropy decreasing) → EXPANSIVE
        if pressure.dS < self.DS_EXPANSIVE_THRESHOLD:
            return SpendPolicy.EXPANSIVE

        # Default
        return SpendPolicy.CONSERVATIVE

    def _calculate_budget(self, pressure: CognitivePressure, policy: SpendPolicy) -> ComputeBudget:
        """
        Calculate concrete budget from policy and pressure.
        """
        budget = ComputeBudget(spend_policy=policy)

        if policy == SpendPolicy.FREEZE:
            # Critical paradox — no tools, minimal tokens, analysis only
            budget.max_tokens = self.TOKENS_MIN
            budget.max_tool_calls = 0
            budget.max_concurrency = 1
            budget.allowed_tier = ComputeTier.T0_CACHE
            budget.api_permission = False
            budget.hold_required = True
            budget.reason = "TAC critical_paradox — freeze all tools"
            return budget

        if policy == SpendPolicy.AUSTERITY:
            # Confusion rising — restrict severely
            budget.max_tokens = self.TOKENS_MIN * 2  # 256
            budget.max_tool_calls = 1
            budget.max_concurrency = 1
            budget.allowed_tier = ComputeTier.T1_LOCAL_CPU
            budget.api_permission = False
            budget.cache_policy = "aggressive"
            budget.hold_required = pressure.risk_score > 0.4
            budget.reason = f"dS={pressure.dS:.3f} > threshold — austerity mode"
            return budget

        if policy == SpendPolicy.CONSERVATIVE:
            # Normal operation with limits
            # Scale tokens by stability
            stability_factor = pressure.peace2
            budget.max_tokens = int(self.TOKENS_NORMAL * stability_factor)
            budget.max_tokens = max(self.TOKENS_MIN, budget.max_tokens)

            # Scale tools by humility (less certain = fewer tools)
            if pressure.omega0 > 0.04:
                budget.max_tool_calls = self.TOOLS_MIN
            else:
                budget.max_tool_calls = min(3, self.TOOLS_MAX)

            # Scale concurrency by stability
            budget.max_concurrency = max(
                self.CONCURRENCY_MIN, int(self.CONCURRENCY_MAX * pressure.peace2)
            )

            budget.allowed_tier = ComputeTier.T2_LOCAL_GPU
            budget.api_permission = pressure.g_star > 0.8
            budget.hold_required = pressure.risk_score > self.RISK_HOLD_THRESHOLD
            budget.reason = f"Peace²={pressure.peace2:.2f}, Ω₀={pressure.omega0:.3f}"
            return budget

        if policy == SpendPolicy.EXPANSIVE:
            # High clarity — allow more compute
            budget.max_tokens = self.TOKENS_MAX
            budget.max_tool_calls = self.TOOLS_MAX
            budget.max_concurrency = self.CONCURRENCY_MAX
            budget.allowed_tier = ComputeTier.T3_PAID_API
            budget.api_permission = True
            budget.cache_policy = "normal"
            budget.priority = 8
            budget.hold_required = False
            budget.reason = f"dS={pressure.dS:.3f} < threshold — clarity high, expand"
            return budget

        # Fallback (should never reach)
        return budget

    def calculate_fitness(self, need: float, impact: float, clarity: float, cost: float) -> float:
        """
        Evolutionary fitness for task prioritization.

        fitness = (need * impact * clarity) / cost

        Tasks with low fitness get deferred (SABAR).
        Only fittest tasks get compute.

        Args:
            need: Must we do it now? [0, 1]
            impact: Consequences if wrong [0, 1]
            clarity: ΔS improvement expected [0, 1]
            cost: Estimated token/tool cost [1, 10]

        Returns:
            Fitness score — higher = more deserving of compute
        """
        if cost <= 0:
            cost = 1.0

        fitness = (need * impact * clarity) / cost
        return min(1.0, max(0.0, fitness))

    def should_defer(self, fitness: float, threshold: float = 0.3) -> bool:
        """
        Determine if task should be deferred (SABAR).

        Low fitness tasks don't deserve compute — defer them.
        """
        return fitness < threshold

    def get_report(self, pressure: CognitivePressure) -> dict:
        """
        Generate homeostasis report for telemetry/logging.
        """
        budget = self.translate(pressure)

        return {
            "timestamp": time.time(),
            "cognitive_pressure": {
                "dS": pressure.dS,
                "peace2": pressure.peace2,
                "omega0": pressure.omega0,
                "tac_status": pressure.tac_status,
                "g_star": pressure.g_star,
                "risk_score": pressure.risk_score,
            },
            "compute_budget": {
                "max_tokens": budget.max_tokens,
                "max_tool_calls": budget.max_tool_calls,
                "max_concurrency": budget.max_concurrency,
                "allowed_tier": budget.allowed_tier.value,
                "spend_policy": budget.spend_policy.value,
                "api_permission": budget.api_permission,
                "hold_required": budget.hold_required,
                "reason": budget.reason,
            },
            "constitutional_compliance": {
                "F4_clarity": pressure.dS <= 0,  # Entropy not increasing
                "F7_humility": pressure.omega0 <= 0.05,
                "F11_command": budget.max_concurrency <= self.CONCURRENCY_MAX,
            },
        }


# Singleton for system-wide use
_homeostasis: HomeostasisInterface | None = None


def get_homeostasis() -> HomeostasisInterface:
    """Get or create singleton HomeostasisInterface instance."""
    global _homeostasis
    if _homeostasis is None:
        _homeostasis = HomeostasisInterface()
    return _homeostasis


def translate_pressure_to_budget(pressure: CognitivePressure) -> ComputeBudget:
    """
    Convenience function: Direct translation.

    Usage:
        budget = translate_pressure_to_budget(CognitivePressure(
            dS=-0.1, peace2=1.0, omega0=0.04, tac_status="stable"
        ))
        # budget.max_tokens, budget.max_tool_calls, etc.
    """
    return get_homeostasis().translate(pressure)


@dataclass
class ParadoxEnergyBudget:
    """
    Paradox Energy Budget — The Metabolic Limiter

    Controls WHEN paradox detection is allowed, not just HOW it resolves.

    This is the missing conservation law identified by multi-model analysis:
    "Soul governs legitimacy, but not metabolic throughput."

    Without this, the system could enter many paradoxes simultaneously
    while waiting for cooling, creating hidden instability.

    Conservation Law: Total paradox energy per cycle ≤ ψ_capacity

    Analogy:
    - Brains prevent constant breakthroughs by attention gating + metabolic fatigue
    - Insight is expensive biologically
    - This is the equivalent throttling for AI systems
    """

    # Capacity limits
    max_active_paradoxes: int = 2  # Maximum concurrent paradox states
    max_paradox_energy: float = 1.0  # Total energy budget per cycle
    paradox_decay_rate: float = 0.1  # Energy recovery per second

    # Current state
    active_paradox_count: int = 0
    current_paradox_energy: float = 0.0
    paradox_queue: list = field(default_factory=list)

    # Phoenix-72 cooling parameters
    cooling_duration_seconds: float = 72.0  # 72-second minimum cooling (scaled from 72h)
    last_eureka_time: float = 0.0
    eurekas_in_window: int = 0
    eureka_window_seconds: float = 300.0  # 5-minute window for rate limiting

    def can_detect_paradox(self, paradox_intensity: float = 0.5) -> tuple[bool, str]:
        """
        Check if system has capacity to detect/absorb new paradox.

        Returns (allowed, reason) tuple.

        This is the Soul controlling heat production, not just cooling.
        """
        now = time.time()

        # Check capacity
        if self.active_paradox_count >= self.max_active_paradoxes:
            return (
                False,
                f"Paradox capacity exceeded ({self.active_paradox_count}/{self.max_active_paradoxes})",
            )

        # Check energy budget
        projected_energy = self.current_paradox_energy + paradox_intensity
        if projected_energy > self.max_paradox_energy:
            return (
                False,
                f"Paradox energy budget exceeded ({projected_energy:.2f}/{self.max_paradox_energy})",
            )

        # Check Eureka rate limiting (Phoenix-72 inspired)
        if self.eurekas_in_window >= 3:  # Max 3 Eurekas per window
            time_since_last = now - self.last_eureka_time
            if time_since_last < self.eureka_window_seconds:
                return (
                    False,
                    f"Eureka rate limit: {self.eurekas_in_window} in last {self.eureka_window_seconds}s",
                )

        return True, "Paradox detection allowed"

    def register_paradox(self, paradox_id: str, intensity: float = 0.5) -> dict:
        """
        Register a new paradox in the system.

        Returns registration status with remaining capacity.
        """
        can_add, reason = self.can_detect_paradox(intensity)

        if not can_add:
            return {
                "registered": False,
                "reason": reason,
                "current_load": self.current_paradox_energy,
                "capacity_remaining": self.max_paradox_energy - self.current_paradox_energy,
            }

        self.active_paradox_count += 1
        self.current_paradox_energy += intensity
        self.paradox_queue.append(
            {
                "id": paradox_id,
                "intensity": intensity,
                "registered_at": time.time(),
            }
        )

        return {
            "registered": True,
            "paradox_id": paradox_id,
            "intensity": intensity,
            "active_paradoxes": self.active_paradox_count,
            "energy_used": self.current_paradox_energy,
            "energy_remaining": self.max_paradox_energy - self.current_paradox_energy,
        }

    def resolve_paradox(self, paradox_id: str, is_eureka: bool = False) -> dict:
        """
        Mark a paradox as resolved, freeing capacity.

        If is_eureka=True, applies Phoenix-72 cooling rules.
        """
        now = time.time()

        # Find and remove paradox from queue
        resolved = None
        for i, p in enumerate(self.paradox_queue):
            if p["id"] == paradox_id:
                resolved = self.paradox_queue.pop(i)
                break

        if resolved is None:
            return {"resolved": False, "reason": f"Paradox {paradox_id} not found"}

        self.active_paradox_count = max(0, self.active_paradox_count - 1)
        self.current_paradox_energy = max(0, self.current_paradox_energy - resolved["intensity"])

        result = {
            "resolved": True,
            "paradox_id": paradox_id,
            "intensity_released": resolved["intensity"],
            "active_paradoxes": self.active_paradox_count,
            "energy_remaining": self.current_paradox_energy,
        }

        # Eureka registration with Phoenix-72 cooling
        if is_eureka:
            self.last_eureka_time = now
            self.eurekas_in_window += 1
            result["eureka_registered"] = True
            result["cooling_duration"] = self.cooling_duration_seconds
            result["message"] = "Eureka registered. Phoenix-72 cooling initiated."

        return result

    def decay_energy(self, dt: float = 1.0) -> float:
        """
        Natural energy decay over time (metabolic recovery).

        Call periodically to allow system to recover capacity.
        """
        decay = self.paradox_decay_rate * dt
        self.current_paradox_energy = max(0, self.current_paradox_energy - decay)

        # Also decay Eureka window counter
        now = time.time()
        if now - self.last_eureka_time > self.eureka_window_seconds:
            self.eurekas_in_window = max(0, self.eurekas_in_window - 1)

        return self.current_paradox_energy

    def get_status(self) -> dict:
        """Get current paradox energy budget status."""
        return {
            "active_paradoxes": self.active_paradox_count,
            "max_paradoxes": self.max_active_paradoxes,
            "current_energy": round(self.current_paradox_energy, 3),
            "max_energy": self.max_paradox_energy,
            "energy_utilization": round(self.current_paradox_energy / self.max_paradox_energy, 2),
            "capacity_available": self.max_active_paradoxes - self.active_paradox_count,
            "eurekas_in_window": self.eurekas_in_window,
            "last_eureka_ago": (
                round(time.time() - self.last_eureka_time, 1) if self.last_eureka_time > 0 else None
            ),
            "constitutional_compliance": {
                "not_overloaded": self.current_paradox_energy < self.max_paradox_energy,
                "capacity_available": self.active_paradox_count < self.max_active_paradoxes,
                "eureka_rate_ok": self.eurekas_in_window < 3,
            },
        }

    def should_downgrade_tac_sensitivity(self) -> tuple[bool, str]:
        """
        Determine if TAC (contradiction detection) sensitivity should be reduced.

        When system is under heavy paradox load, reduce sensitivity to prevent
        overload. This is the Soul controlling heat production.
        """
        if self.current_paradox_energy > 0.8 * self.max_paradox_energy:
            return True, "Energy budget critical — reduce TAC sensitivity"

        if self.active_paradox_count >= self.max_active_paradoxes:
            return True, "Paradox capacity full — defer new anomaly classification"

        if self.eurekas_in_window >= 2:
            return True, "Eureka rate approaching limit — increase detection threshold"

        return False, "TAC sensitivity normal"


# Singleton for paradox energy budget
_paradox_budget: ParadoxEnergyBudget | None = None


def get_paradox_budget() -> ParadoxEnergyBudget:
    """Get or create singleton ParadoxEnergyBudget instance."""
    global _paradox_budget
    if _paradox_budget is None:
        _paradox_budget = ParadoxEnergyBudget()
    return _paradox_budget


__all__ = [
    # P0 HARDENING: F5 Enforcement
    "PeaceViolation",
    "HomeostaticCollapse",
    "check_peace_squared",
    "enforce_homeostatic_stability",
    # Core classes
    "ComputeTier",
    "SpendPolicy",
    "CognitivePressure",
    "ComputeBudget",
    "HomeostasisInterface",
    "ParadoxEnergyBudget",
    "get_homeostasis",
    "get_paradox_budget",
    "translate_pressure_to_budget",
]

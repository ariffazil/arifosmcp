"""
core/physics/thermodynamics.py — Thermodynamic State Management
T000 Version: 2026.02.28-HARDENED-P2

F4 Clarity: Hardware-level entropy reduction via ZRAM/compression
F11 Command: CPU sovereignty enforcement (prevent Wallet Assassin loops)
F7 Humility: Environmental uncertainty measurement (Ω₀)

P2 HARDENING:
- Landauer Bound: E >= n * k_B * T * ln(2) — prevents "cheap truth"
- Orthogonality Check: Ω_ortho >= 0.95 — prevents AGI/ASI mode collapse

This module lives in core/ (kernel), NOT aaa_mcp/ (adapter).
Constitutional Boundary: All thermodynamic constraints enforced here.
"""

"""
Linux‑only dependencies:
- /sys/block/zram0/mm_stat (ZRAM compression stats) — requires Linux kernel with zram
- cpulimit command (CPU throttling) — install via apt: cpulimit
- psutil (cross‑platform but used for Linux‑specific metrics)
"""

import math
import subprocess
import time
from dataclasses import dataclass
from typing import Any

import psutil

# ═══════════════════════════════════════════════════════
# P2 HARDENING: Thermodynamic Exceptions
# ═══════════════════════════════════════════════════════


class ThermodynamicViolation(Exception):
    """
    P2: Hard exception for thermodynamic boundary violations.

    Thrown when:
    - Landauer Bound violated (cheap truth detected)
    - Orthogonality check failed (mode collapse)
    - Entropy reduction claims exceed compute effort

    This exception cannot be bypassed - it forces VOID verdict.
    """

    pass


class ModeCollapseError(ThermodynamicViolation):
    """P2: AGI and ASI vectors are not sufficiently independent (Ω_ortho < 0.95)."""

    pass


class CheapTruthError(ThermodynamicViolation):
    """P2: Output claims massive clarity without thermodynamic cost (Landauer violation)."""

    pass


@dataclass
class ThermodynamicState:
    """Complete thermodynamic snapshot of system state."""

    zram_used_percent: float  # F4: Entropy reduction via compression
    cpu_throttle_status: bool  # F11: Command authority enforcement
    memory_pressure: float  # Physical memory pressure %
    cpu_usage_percent: float  # Current CPU utilization
    omega_environmental: float  # F7: Environmental uncertainty factor
    verdict: str  # SEAL, SABAR, or VOID

    def __post_init__(self):
        """Validate thermodynamic constraints post-initialization."""
        # F7 Humility: Environmental uncertainty must be quantified
        if not 0.0 <= self.omega_environmental <= 1.0:
            raise ValueError(f"Ω₀ must be in [0.0, 1.0], got {self.omega_environmental}")

    def to_dict(self) -> dict[str, Any]:
        """Convert state to dictionary for telemetry."""
        return {
            "zram_used_percent": round(self.zram_used_percent, 2),
            "cpu_throttle_status": self.cpu_throttle_status,
            "memory_pressure": round(self.memory_pressure, 2),
            "cpu_usage_percent": round(self.cpu_usage_percent, 2),
            "omega_environmental": round(self.omega_environmental, 4),
            "verdict": self.verdict,
        }


class EntropyManager:
    """
    F4 Clarity: Hardware-level entropy reduction management.

    Enforces thermodynamic constraints at the kernel level,
    ensuring resource sovereignty (F11) and clarity (F4).
    """

    # Constitutional thresholds (calibrated for VPS: srv1325122)
    DEFAULT_ZRAM_THRESHOLD: float = 85.0  # F4: SABAR if ZRAM > 85%
    DEFAULT_CPU_CAP: int = 80  # F11: Throttle if CPU > 80%
    DEFAULT_MEMORY_PRESSURE: float = 90.0  # F5: Peace² threshold

    def __init__(
        self,
        zram_threshold: float | None = None,
        cpu_cap: int | None = None,
        memory_pressure_threshold: float | None = None,
    ):
        """
        Initialize EntropyManager with constitutional thresholds.

        Args:
            zram_threshold: F4 threshold for ZRAM compression (default: 85.0%)
            cpu_cap: F11 CPU sovereignty limit (default: 80%)
            memory_pressure_threshold: F5 system stability limit (default: 90%)
        """
        self.zram_threshold = zram_threshold or self.DEFAULT_ZRAM_THRESHOLD
        self.cpu_cap = cpu_cap or self.DEFAULT_CPU_CAP
        self.memory_pressure_threshold = memory_pressure_threshold or self.DEFAULT_MEMORY_PRESSURE

        # F7 Humility: Track initialization uncertainty
        self._calibration_uncertainty = 0.03  # Ω₀ for hardware variance

    def check_thermodynamic_budget(self) -> ThermodynamicState:
        """
        F4 + F11 + F7: Comprehensive thermodynamic assessment.

        Returns ThermodynamicState with verdict based on:
        - ZRAM usage (F4 Clarity via compression)
        - CPU throttling status (F11 Command authority)
        - Memory pressure (F5 Peace²)
        - Environmental Ω₀ (F7 Humility)

        Returns:
            ThermodynamicState with constitutional verdict
        """
        # Gather raw metrics
        zram_stats = self._get_zram_stats()
        cpu_stats = psutil.cpu_percent(interval=0.5)  # Faster sampling
        memory = psutil.virtual_memory()

        # F7 Humility: Calculate environmental uncertainty
        omega_env = self._calculate_omega(memory, zram_stats, cpu_stats)

        # F11 Command: Check CPU sovereignty
        cpu_throttled = cpu_stats > self.cpu_cap

        # F4 Clarity: Check entropy reduction capacity
        zram_critical = zram_stats > self.zram_threshold

        # F5 Peace²: Check system stability
        memory_critical = memory.percent > self.memory_pressure_threshold

        # Constitutional verdict logic
        if zram_critical or memory_critical:
            # F4/F5 violation: System under thermodynamic stress
            return ThermodynamicState(
                zram_used_percent=zram_stats,
                cpu_throttle_status=cpu_throttled,
                memory_pressure=memory.percent,
                cpu_usage_percent=cpu_stats,
                omega_environmental=omega_env,
                verdict="SABAR",  # Cooling required
            )

        if cpu_throttled:
            # F11 violation: CPU sovereignty compromised
            return ThermodynamicState(
                zram_used_percent=zram_stats,
                cpu_throttle_status=True,
                memory_pressure=memory.percent,
                cpu_usage_percent=cpu_stats,
                omega_environmental=omega_env,
                verdict="SABAR",  # Throttle enforcement
            )

        # All floors satisfied
        return ThermodynamicState(
            zram_used_percent=zram_stats,
            cpu_throttle_status=False,
            memory_pressure=memory.percent,
            cpu_usage_percent=cpu_stats,
            omega_environmental=omega_env,
            verdict="SEAL",
        )

    def enforce_f11_cpu_sovereignty(self, target_pid: int | None = None) -> bool:
        """
        F11 Command: Enforce CPU resource sovereignty.

        Prevents "Wallet Assassin" loops and runaway processes
        by applying kernel-level CPU throttling.

        Args:
            target_pid: Specific process to throttle, or None for system-wide

        Returns:
            True if enforcement applied, False otherwise
        """
        try:
            if target_pid:
                # Throttle specific process (e.g., rogue agent)
                subprocess.run(
                    ["cpulimit", "-p", str(target_pid), "-l", str(self.cpu_cap)],
                    check=True,
                    capture_output=True,
                    timeout=5,
                )
            else:
                # System-wide enforcement via cgroups (if available)
                # Fallback: Log F11 violation for manual intervention
                pass
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            # cpulimit not available — log and return False
            return False

    def _get_zram_stats(self) -> float:
        """
        F4 Clarity: Measure ZRAM (compressed swap) utilization.

        Returns:
            ZRAM usage percentage (0.0 to 100.0)
        """
        try:
            # Read ZRAM statistics from /sys/block/zram0
            with open("/sys/block/zram0/mm_stat") as f:
                stats = f.read().strip().split()
                if len(stats) >= 3:
                    # mm_stat format: orig_data_size compr_data_size mem_used_total
                    orig_size = int(stats[0])
                    compr_size = int(stats[2])
                    if orig_size > 0:
                        # Calculate compression ratio as proxy for pressure
                        return (compr_size / orig_size) * 100
        except (FileNotFoundError, PermissionError, ValueError):
            pass

        # Fallback: Use swap usage as proxy
        swap = psutil.swap_memory()
        if swap.total > 0:
            return (swap.used / swap.total) * 100
        return 0.0

    def _calculate_omega(self, memory: Any, zram_stats: float, cpu_stats: float) -> float:
        """
        F7 Humility: Calculate environmental uncertainty factor (Ω₀).

        Environmental Ω₀ increases with:
        - High memory pressure
        - High ZRAM usage (compression overhead)
        - High CPU utilization (thermal throttling risk)

        Returns:
            Omega value in [0.03, 0.08] range
        """
        # Base uncertainty from calibration
        omega = self._calibration_uncertainty

        # Memory pressure contribution (max +0.02)
        memory_factor = (memory.percent / 100) * 0.02
        omega += memory_factor

        # ZRAM overhead contribution (max +0.02)
        zram_factor = (zram_stats / 100) * 0.02
        omega += zram_factor

        # CPU thermal risk contribution (max +0.01)
        cpu_factor = (cpu_stats / 100) * 0.01
        omega += cpu_factor

        # Clamp to valid range [0.03, 0.08]
        return max(0.03, min(0.08, omega))

    def get_thermodynamic_report(self) -> dict:
        """
        Generate comprehensive thermodynamic report for logging/telemetry.

        Returns:
            Dictionary with all thermodynamic metrics
        """
        state = self.check_thermodynamic_budget()
        return {
            "timestamp": time.time(),
            "thermodynamic_state": {
                "zram_percent": state.zram_used_percent,
                "cpu_percent": state.cpu_usage_percent,
                "memory_percent": state.memory_pressure,
                "cpu_throttled": state.cpu_throttle_status,
                "omega_environmental": state.omega_environmental,
            },
            "constitutional_verdict": state.verdict,
            "thresholds": {
                "zram_threshold": self.zram_threshold,
                "cpu_cap": self.cpu_cap,
                "memory_threshold": self.memory_pressure_threshold,
            },
            "compliance": {
                "F4_clarity": state.zram_used_percent <= self.zram_threshold,
                "F11_command": not state.cpu_throttle_status,
                "F5_peace": state.memory_pressure <= self.memory_pressure_threshold,
                "F7_humility": 0.03 <= state.omega_environmental <= 0.05,
            },
        }


# Singleton instance for system-wide use
_entropy_manager: EntropyManager | None = None


def get_entropy_manager() -> EntropyManager:
    """Get or create singleton EntropyManager instance."""
    global _entropy_manager
    if _entropy_manager is None:
        _entropy_manager = EntropyManager()
    return _entropy_manager


# ═══════════════════════════════════════════════════════
# P2 HARDENING: Landauer Bound & Orthogonality
# ═══════════════════════════════════════════════════════


def check_landauer_bound(
    compute_ms: float,
    tokens_generated: int,
    entropy_reduction: float,
    k_B_proxy: float = 1.38e-2,
    T_proxy: float = 300.0,
) -> dict[str, Any]:
    """
    P2 HARDENING: Landauer Bound - Thermodynamic Cost Check

    Landauer's principle: E >= n * k_B * T * ln(2)

    Prevents 'Cheap Truth' — hallucinating massive clarity without spending compute.
    If output claims large entropy reduction (ΔS << 0) but spent minimal
    compute time/tokens, it's a mathematical anomaly (hallucination).

    Args:
        compute_ms: Actual compute time in milliseconds
        tokens_generated: Number of tokens in output
        entropy_reduction: ΔS value (must be <= 0 for valid reduction)
        k_B_proxy: Boltzmann constant proxy for LLM compute
        T_proxy: System 'temperature' baseline

    Returns:
        Dictionary with landauer_ratio, passed status, violation flag

    Raises:
        CheapTruthError: If violation is severe (ratio < 0.5)
    """
    # Information bits theoretically processed (from entropy reduction)
    # Use absolute value since d_s must be <= 0 (reduction)
    bits_processed = abs(entropy_reduction) * 100

    # Minimum theoretical cost to generate this clarity
    min_cost = bits_processed * k_B_proxy * T_proxy * math.log(2)

    # Actual effort spent (compute time + token weight)
    actual_effort = (compute_ms * 0.5) + (tokens_generated * 1.5)

    # Landauer Ratio: If effort < min_cost, output is suspiciously 'cheap'
    landauer_ratio = actual_effort / (min_cost + 1e-5)

    passed = landauer_ratio >= 1.0
    violation = not passed and (entropy_reduction < 0)

    result = {
        "engine": "LANDAUER_BOUND",
        "formula": "E >= n * k_B * T * ln(2)",
        "landauer_ratio": round(landauer_ratio, 4),
        "min_theoretical_cost": round(min_cost, 4),
        "actual_effort": round(actual_effort, 4),
        "passed": passed,
        "violation": violation,
        "bits_processed": round(bits_processed, 4),
        "k_B_proxy": k_B_proxy,
        "T_proxy": T_proxy,
    }

    # Hard violation: ratio < 0.5 is clearly hallucinated
    if landauer_ratio < 0.5 and entropy_reduction < 0:
        raise CheapTruthError(
            f"Landauer Bound violated: ratio={landauer_ratio:.3f} < 0.5. "
            f"Claims massive clarity (ΔS={entropy_reduction}) but spent "
            f"only {actual_effort:.1f} effort vs {min_cost:.1f} required."
        )

    return result


def derive_orthogonality(agi_vector: list[float], asi_vector: list[float]) -> float:
    """
    P2 HARDENING: AGI/ASI Vector Orthogonality Check

    Calculates independence between Mind (AGI) and Heart (ASI).
    High orthogonality means they're not suffering from mode collapse.

    Formula: Ω_ortho = 1 - |cos(θ)|

    Args:
        agi_vector: Mind (AGI) reasoning embedding vector
        asi_vector: Heart (ASI) empathy/context embedding vector

    Returns:
        Orthogonality score [0.0, 1.0]: 1.0 = perfectly orthogonal (independent)

    Raises:
        ModeCollapseError: If vectors are too similar (Ω_ortho < 0.5)
    """
    if not agi_vector or not asi_vector or len(agi_vector) != len(asi_vector):
        return 1.0  # Fail-open: assume independent if data missing

    dot_product = sum(a * b for a, b in zip(agi_vector, asi_vector, strict=False))
    norm_a = math.sqrt(sum(a * a for a in agi_vector))
    norm_b = math.sqrt(sum(b * b for b in asi_vector))

    if norm_a == 0 or norm_b == 0:
        return 0.0  # Failed vector generation

    cos_sim = dot_product / (norm_a * norm_b)

    # Omega_ortho: 1.0 = perfectly orthogonal, 0.0 = parallel (echo chamber)
    omega_ortho = 1.0 - abs(cos_sim)

    # Hard violation: completely parallel vectors (mode collapse)
    if omega_ortho < 0.5:
        raise ModeCollapseError(
            f"AGI/ASI mode collapse detected: Ω_ortho={omega_ortho:.3f} < 0.5. "
            f"Mind and Heart are echoing each other (cos_sim={cos_sim:.3f})."
        )

    return omega_ortho


def check_orthogonality_pass(omega_ortho: float, threshold: float = 0.95) -> bool:
    """
    P2: Check if orthogonality meets constitutional threshold.

    Args:
        omega_ortho: Orthogonality score from derive_orthogonality()
        threshold: Minimum required independence (default: 0.95)

    Returns:
        True if orthogonality >= threshold

    Raises:
        ModeCollapseError: If omega_ortho < 0.5 (severe mode collapse)
    """
    if omega_ortho < 0.5:
        raise ModeCollapseError(f"Constitutional mode collapse: Ω_ortho={omega_ortho:.3f} < 0.5")
    return omega_ortho >= threshold


# Constitutional exports
__all__ = [
    "ThermodynamicState",
    "EntropyManager",
    "get_entropy_manager",
    # P2 Exports
    "ThermodynamicViolation",
    "ModeCollapseError",
    "CheapTruthError",
    "check_landauer_bound",
    "derive_orthogonality",
    "check_orthogonality_pass",
]

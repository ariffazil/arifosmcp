# core/telemetry.py
# v64.2 — Constitutional Telemetry & Live Observability
# Q3 Verdict: TELEMETRY FIRST with LIVE METRICS INTEGRATION

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

ADAPTATION_LOCK_DAYS = 30
ADAPTATION_DRIFT_THRESHOLD = 0.15  # 15% drift required


def _utcnow() -> datetime:
    """Timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


@dataclass
class ConstitutionalTelemetry:
    """
    v64.1 Telemetry-only feedback loop.

    Q3 Architectural Decision:
    - Log metrics only (no adaptation) for first 30 days
    - Calculate drift weekly
    - Adaptation requires: 30 days + drift < threshold + human approval

    This prevents noise-driven governance drift.
    """

    session_id: str
    timestamp: str = field(default_factory=lambda: _utcnow().isoformat())

    # L7: Gate activations
    omega_0: float = 0.0
    irreversibility_index: float = 0.0
    gate_activated: bool = False
    gate_reason: str = ""

    # L8: Human interactions
    human_override_requested: bool = False
    human_override_received: bool = False
    human_decision: str = ""  # "approved" | "denied" | "modified"

    # L4: Uncertainty misprediction
    predicted_risk: float = 0.0
    observed_outcome: float = 0.0
    misprediction_delta: float = 0.0

    # L6: Governance events
    escalation_count: int = 0
    void_count: int = 0
    sabar_count: int = 0
    seal_count: int = 0

    # L9: Drift tracking
    drift_score: float = 0.0  # |predicted - observed|


class TelemetryStore:
    """Store and analyze constitutional telemetry."""

    def __init__(self, storage_path: str = "telemetry/constitutional"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

        # Q3: Track first telemetry date
        self.first_telemetry_file = os.path.join(storage_path, ".first_telemetry")
        self.first_telemetry_date = self._load_first_date()

    def _load_first_date(self) -> datetime | None:
        """Load first telemetry date (adaptation lock)."""
        if os.path.exists(self.first_telemetry_file):
            with open(self.first_telemetry_file) as f:
                date_str = f.read().strip()
                parsed = datetime.fromisoformat(date_str)
                if parsed.tzinfo is None:
                    # Backward compatibility for legacy naive timestamps.
                    parsed = parsed.replace(tzinfo=timezone.utc)
                return parsed
        return None

    def _save_first_date(self, date: datetime):
        """Save first telemetry date."""
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
        with open(self.first_telemetry_file, "w") as f:
            f.write(date.isoformat())

    def log(self, telemetry: ConstitutionalTelemetry):
        """Log telemetry event."""
        # Set first date if not set
        if self.first_telemetry_date is None:
            self.first_telemetry_date = _utcnow()
            self._save_first_date(self.first_telemetry_date)

        # Append to daily log
        date_str = _utcnow().strftime("%Y-%m-%d")
        log_file = os.path.join(self.storage_path, f"telemetry-{date_str}.jsonl")

        with open(log_file, "a") as f:
            f.write(
                json.dumps(
                    {
                        "session_id": telemetry.session_id,
                        "timestamp": telemetry.timestamp,
                        "omega_0": telemetry.omega_0,
                        "irreversibility_index": telemetry.irreversibility_index,
                        "gate_activated": telemetry.gate_activated,
                        "human_override_requested": telemetry.human_override_requested,
                        "human_decision": telemetry.human_decision,
                        "predicted_risk": telemetry.predicted_risk,
                        "observed_outcome": telemetry.observed_outcome,
                        "misprediction_delta": telemetry.misprediction_delta,
                        "verdict_counts": {
                            "escalation": telemetry.escalation_count,
                            "void": telemetry.void_count,
                            "sabar": telemetry.sabar_count,
                            "seal": telemetry.seal_count,
                        },
                        "drift_score": telemetry.drift_score,
                    }
                )
                + "\n"
            )

    def get_telemetry_days(self) -> int:
        """Q3: Days since first telemetry (adaptation lock check)."""
        if self.first_telemetry_date is None:
            return 0
        return (_utcnow() - self.first_telemetry_date).days

    def can_adapt(self) -> dict[str, any]:
        """
        Q3: Check if adaptation is allowed.

        Returns:
            Dict with can_adapt (bool) and reasons (list)
        """
        days = self.get_telemetry_days()
        drift = self._calculate_weekly_drift()

        reasons = []

        # Check 1: 30 days minimum
        if days < ADAPTATION_LOCK_DAYS:
            reasons.append(f"Insufficient telemetry: {days}/{ADAPTATION_LOCK_DAYS} days")

        # Check 2: Drift stability
        if drift > ADAPTATION_DRIFT_THRESHOLD:
            reasons.append(f"Drift too high: {drift:.2f} > {ADAPTATION_DRIFT_THRESHOLD}")

        # Check 3: Human approval (always required)
        reasons.append("Human approval required (888 Judge)")

        return {
            "can_adapt": days >= ADAPTATION_LOCK_DAYS and drift <= ADAPTATION_DRIFT_THRESHOLD,
            "days": days,
            "drift": drift,
            "reasons": reasons,
            "human_approval_required": True,
        }

    def _calculate_weekly_drift(self) -> float:
        """Calculate average misprediction drift over last 7 days."""
        drift_scores = []

        for i in range(7):
            date = _utcnow() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            log_file = os.path.join(self.storage_path, f"telemetry-{date_str}.jsonl")

            if os.path.exists(log_file):
                with open(log_file) as f:
                    for line in f:
                        try:
                            data = json.loads(line.strip())
                            drift_scores.append(abs(data.get("misprediction_delta", 0)))
                        except json.JSONDecodeError:
                            continue

        return sum(drift_scores) / len(drift_scores) if drift_scores else 0.0

    def calculate_hysteresis_penalty(self, window_days: int = 7) -> float:
        """
        Calculate the Hysteresis Penalty (h) based on past failures.
        Scars (VOID/SABAR) accumulate and slowly decay.

        Formula: h = sum(void * 0.1 + sabar * 0.02) * decay(t)
        Max h = 1.0 (Wisdom collapse)
        """
        total_penalty = 0.0

        for i in range(window_days):
            date = _utcnow() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            log_file = os.path.join(self.storage_path, f"telemetry-{date_str}.jsonl")

            # Time decay: older scars hurt less
            # day 0: 1.0, day 6: 0.25
            decay = 1.0 - (i / window_days) * 0.75

            if os.path.exists(log_file):
                with open(log_file) as f:
                    for line in f:
                        try:
                            data = json.loads(line.strip())
                            counts = data.get("verdict_counts", {})

                            # Weighting: VOID is a deep scar, SABAR is a bruise
                            v_count = counts.get("void", 0)
                            s_count = counts.get("sabar", 0)

                            total_penalty += (v_count * 0.15 + s_count * 0.03) * decay
                        except (json.JSONDecodeError, KeyError):
                            continue

        return round(max(0.0, min(1.0, total_penalty)), 4)

    def generate_weekly_report(self) -> dict:
        """Generate weekly telemetry report."""
        days = self.get_telemetry_days()
        drift = self._calculate_weekly_drift()
        adaptation_status = self.can_adapt()

        return {
            "report_date": _utcnow().isoformat(),
            "telemetry_days": days,
            "adaptation_lock_status": "LOCKED" if days < ADAPTATION_LOCK_DAYS else "UNLOCKED",
            "weekly_drift": round(drift, 4),
            "can_adapt": adaptation_status["can_adapt"],
            "adaptation_requirements": adaptation_status["reasons"],
            "q3_compliance": "TELEMETRY_FIRST",
        }


# Global telemetry store
telemetry_store = TelemetryStore()


def log_telemetry(
    session_id: str,
    omega_0: float,
    irreversibility_index: float,
    gate_activated: bool = False,
    human_override: bool = False,
    verdict: str = "",
    predicted_risk: float = 0.0,
    observed_outcome: float = 0.0,
) -> None:
    """Convenience function for logging telemetry."""
    telemetry = ConstitutionalTelemetry(
        session_id=session_id,
        omega_0=omega_0,
        irreversibility_index=irreversibility_index,
        gate_activated=gate_activated,
        gate_reason=(
            "uncertainty"
            if omega_0 > 0.06
            else "irreversibility"
            if irreversibility_index > 0.6
            else ""
        ),
        human_override_requested=human_override,
        predicted_risk=predicted_risk,
        observed_outcome=observed_outcome,
        misprediction_delta=abs(predicted_risk - observed_outcome),
    )

    # Update verdict counts
    if verdict == "VOID":
        telemetry.void_count = 1
    elif verdict == "SABAR":
        telemetry.sabar_count = 1
    elif verdict == "SEAL":
        telemetry.seal_count = 1
    elif verdict == "888_HOLD":
        telemetry.escalation_count = 1

    telemetry_store.log(telemetry)


def check_adaptation_status() -> dict:
    """Check if constitutional adaptation is allowed."""
    return telemetry_store.can_adapt()


# ... (rest of imports)


def get_current_hysteresis() -> float:
    """Retrieve the current hysteresis penalty score."""
    return telemetry_store.calculate_hysteresis_penalty()


def get_system_vitals() -> dict[str, float]:
    """
    Retrieve machine-level performance metrics (The Machine).
    These represent the underlying 'bio-mass' of the intelligence.
    """
    try:
        import psutil

        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return {
            "cpu_percent": cpu,
            "memory_percent": mem.percent,
            "memory_used_gb": round(mem.used / (1024**3), 2),
            "memory_total_gb": round(mem.total / (1024**3), 2),
            "disk_percent": disk.percent,
            "load_avg": getattr(os, "getloadavg", lambda: (0, 0, 0))(),
        }
    except Exception:
        return {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "disk_percent": 0.0,
            "load_avg": (0, 0, 0),
        }


def get_actual_joules(duration_ms: float) -> float:
    """
    HARDWARE GROUNDING: Estimate actual Joules consumed by the CPU.
    On Windows, uses a high-fidelity proxy based on load and TDP.
    """
    # 1. Base TDP (Thermal Design Power) - typical laptop/workstation
    # In a real implementation, this would use NVML (GPU) or RAPL (CPU)
    base_tdp = 45.0  # Watts
    idle_power = 5.0  # Watts

    try:
        import psutil

        # 2. Get real-time CPU load
        # We use a short interval for fresh measurement or None for instant
        load_factor = psutil.cpu_percent(interval=None) / 100.0
        
        # 3. High-fidelity proxy: Load-dependent wattage
        # Actual_Watts = Idle + (TDP-Idle) * Load
        actual_watts = idle_power + (base_tdp - idle_power) * load_factor

        # 4. Energy = Power * Time (Seconds)
        joules = actual_watts * (duration_ms / 1000.0)
        return round(joules, 6)
    except Exception:
        # Fallback to conservative estimate (TDP * time)
        return (base_tdp * 0.5) * (duration_ms / 1000.0)

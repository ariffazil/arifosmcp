"""
arifosmcp/runtime/metrics.py — Prometheus Metrics for arifOS

Defines the gauges and counters for constitutional observability (G, ΔS, Ω₀).
Part of H1.1: Production Observability.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any, Literal
from prometheus_client import Counter, Gauge, Histogram
from arifosmcp.runtime.models import (
    CanonicalMetrics, 
    TelemetryVitals, 
    TelemetryBasis, 
    TripleWitness
)

try:
    from opentelemetry import trace
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

# ... (Existing Prometheus metrics) ...

# ---------------------------------------------------------------------------
# OPEN TELEMETRY HELIX TRACER
# ---------------------------------------------------------------------------

class HelixTracer:
    """High-fidelity OpenTelemetry tracer for the arifOS Double Helix organs."""
    
    def __init__(self):
        if OTEL_AVAILABLE:
            self.tracer = trace.get_tracer("arifos.helix")
        else:
            self.tracer = None

    def start_organ_span(self, organ_name: str, session_id: str):
        """Start a trace span for a constitutional organ."""
        if not self.tracer:
            # No-op context manager if OTEL not available
            from contextlib import asynccontextmanager
            @asynccontextmanager
            async def noop(): yield None
            return noop()
            
        span = self.tracer.start_as_current_span(
            f"organ.{organ_name}",
            attributes={
                "session_id": session_id,
                "organ": organ_name,
                "helix_ring": "INNER" if organ_name.isupper() else "OUTER"
            }
        )
        return span

    def record_constitutional_event(self, span: Any, event_name: str, metrics: dict[str, Any]):
        """Record a thermodynamic state transition event within a span."""
        if not span:
            return
        
        span.add_event(
            event_name,
            attributes={f"constitutional.{k}": v for k, v in metrics.items()}
        )

helix_tracer = HelixTracer()

# G (Genius Score) - Fundamental governed intelligence (3E) metric [0, 1]
GENIUS_SCORE = Gauge(
    "arifos_genius_score",
    "Governed Intelligence (3E) Score (G) — Target ≥ 0.80",
    ["session_id", "tool", "provenance"],
)

# ΔS (Entropy Delta) - Information clarity metric (lower is better, ideally ≤ 0)
ENTROPY_DELTA = Gauge(
    "arifos_entropy_delta",
    "Information Entropy Delta (ΔS) — Lower reduces noise",
    ["session_id", "tool", "provenance"],
)

# Ω₀ (Humility / Uncertainty) - Stability band metric [0.03, 0.05]
HUMILITY_BAND = Gauge(
    "arifos_humility_band",
    "Humility / Uncertainty (Ω₀) — Target band [0.03, 0.05]",
    ["session_id", "tool", "provenance"],
)

# P² (Peace Squared) - Stakeholder safety metric [0, 1]
PEACE_SQUARED = Gauge(
    "arifos_peace_squared",
    "Stakeholder Stability (P²) — Target ≥ 1.0",
    ["session_id", "tool", "provenance"],
)

# κᵣ (Empathy Quotient) - Stakeholder care metric
EMPATHY_QUOTIENT = Gauge(
    "arifos_empathy_quotient",
    "Empathy Quotient (κᵣ) — Stakeholder care level",
    ["session_id", "tool", "provenance"],
)

# ---------------------------------------------------------------------------
# OPERATIONAL METRICS
# ---------------------------------------------------------------------------

# Metabolic Loop Latency
METABOLIC_LOOP_DURATION = Histogram(
    "arifos_metabolic_loop_seconds",
    "Latency of the 000-999 metabolic loop",
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0),
)

# Verdict Counters
VERDICT_TOTAL = Counter(
    "arifos_verdicts_total",
    "Total constitutional verdicts issued",
    ["verdict"],  # SEAL, VOID, HOLD_888, PARTIAL
)

# Request Counter
REQUESTS_TOTAL = Counter(
    "arifos_requests_total",
    "Total incoming requests processed by the runtime",
    ["method", "status"],
)

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------


def record_constitutional_metrics(
    session_id: str,
    tool: str,
    metrics: dict[str, float],
    provenance_map: dict[str, str] | None = None,
) -> None:
    """
    Record a snapshot of constitutional metrics for a given tool call.

    H1.1: Includes provenance labels (measured, derived, policy_constant, placeholder).
    """
    prov = provenance_map or {}

    if "G" in metrics:
        GENIUS_SCORE.labels(
            session_id=session_id, tool=tool, provenance=prov.get("G", "derived")
        ).set(metrics["G"])
    elif "genius" in metrics:
        GENIUS_SCORE.labels(
            session_id=session_id, tool=tool, provenance=prov.get("genius", "derived")
        ).set(metrics["genius"])

    if "dS" in metrics:
        ENTROPY_DELTA.labels(
            session_id=session_id, tool=tool, provenance=prov.get("dS", "measured")
        ).set(metrics["dS"])
    elif "entropy_delta" in metrics:
        ENTROPY_DELTA.labels(
            session_id=session_id, tool=tool, provenance=prov.get("entropy_delta", "measured")
        ).set(metrics["entropy_delta"])

    if "omega0" in metrics:
        HUMILITY_BAND.labels(
            session_id=session_id, tool=tool, provenance=prov.get("omega0", "policy_constant")
        ).set(metrics["omega0"])
    elif "humility" in metrics:
        HUMILITY_BAND.labels(
            session_id=session_id, tool=tool, provenance=prov.get("humility", "policy_constant")
        ).set(metrics["humility"])

    if "peace2" in metrics:
        PEACE_SQUARED.labels(
            session_id=session_id, tool=tool, provenance=prov.get("peace2", "policy_constant")
        ).set(metrics["peace2"])
    elif "peace" in metrics:
        PEACE_SQUARED.labels(
            session_id=session_id, tool=tool, provenance=prov.get("peace", "policy_constant")
        ).set(metrics["peace"])

    if "kappa_r" in metrics:
        EMPATHY_QUOTIENT.labels(
            session_id=session_id, tool=tool, provenance=prov.get("kappa_r", "placeholder")
        ).set(metrics["kappa_r"])
    elif "empathy" in metrics:
        EMPATHY_QUOTIENT.labels(
            session_id=session_id, tool=tool, provenance=prov.get("empathy", "placeholder")
        ).set(metrics["empathy"])


def record_verdict(verdict: str) -> None:
    """Increment verdict counter."""
    VERDICT_TOTAL.labels(verdict=verdict).inc()


# ---------------------------------------------------------------------------
# FORGED-2026.03: MGI CANONICAL TOOL METRICS
# Grand Unified Technical Specification additions
# ---------------------------------------------------------------------------

# W3 Tri-Witness score histogram (F3 Mirror Floor)
W3_SCORE = Histogram(
    "arifos_w3_score",
    "Tri-Witness W3 score distribution — SEAL threshold ≥ 0.95",
    ["tool"],
    buckets=[0.0, 0.25, 0.50, 0.70, 0.75, 0.85, 0.90, 0.95, 1.0],
)

# 888_HOLD queue depth (F13 Sovereign Gate backlog)
HOLD_QUEUE_DEPTH = Gauge(
    "arifos_hold_queue_depth",
    "Number of 888_HOLD events pending sovereign ratification",
)

# Vault record count (VAULT999 growth)
VAULT_RECORDS_TOTAL = Gauge(
    "arifos_vault_records_total",
    "Total records in VAULT999 Merkle chain",
)

# Floor violations by floor code (constitutional health)
FLOOR_VIOLATIONS = Counter(
    "arifos_floor_violations_total",
    "Constitutional floor violations — breach by floor and tool",
    ["floor", "tool"],
)

# SABAR events — non-terminal cooling/retry states
# SABAR ≠ HOLD (no human needed) ≠ VOID (not permanent)
SABAR_EVENTS = Counter(
    "arifos_sabar_events_total",
    "SABAR cooling states — temporary thermodynamic instability by tool and cause",
    ["tool", "cause"],
)

# Active Sessions (H1.1: Production Observability)
ACTIVE_SESSIONS = Gauge(
    "arifos_sessions_active",
    "Number of currently active constitutional sessions",
)

# Vault Entry Count (SHA-256 Merkle Ledger)
VAULT_ENTRIES_COUNT = Gauge(
    "arifos_vault_entries_total",
    "Total count of sealed entries in VAULT999",
)

# Machine fault codes (VOID Memanjang elimination — mechanical faults only)
MACHINE_FAULTS = Counter(
    "arifos_machine_faults_total",
    "Machine-layer faults (NEVER maps to VOID) — by fault_code and tool",
    ["fault_code", "tool"],
)

# VOID events (constitutional only — should be rare)
VOID_EVENTS = Counter(
    "arifos_void_events_total",
    "VOID verdicts issued — constitutional violations only (F2/F11/F12/F13)",
    ["void_reason", "tool"],
)

# Merkle chain integrity check results
MERKLE_INTEGRITY = Counter(
    "arifos_merkle_integrity_checks_total",
    "VAULT999 Merkle chain integrity check outcomes",
    ["status"],  # VALID | TAMPERED
)


def record_w3(tool: str, w3_score: float) -> None:
    """Record a W3 Tri-Witness score observation."""
    W3_SCORE.labels(tool=tool).observe(w3_score)


def update_prometheus_metrics() -> None:
    """Refreshes dynamic gauges like active sessions and vault record counts (Job 5)."""
    try:
        from arifosmcp.runtime.sessions import list_active_sessions_count
        ACTIVE_SESSIONS.set(list_active_sessions_count())
    except:
        pass

    try:
        from arifosmcp.intelligence.tools.logic.vault_logger import VaultLogger
        logger_inst = VaultLogger()
        # Retrieve all records for a session "*" as a proxy for total records
        # In Postgres mode, this is more accurate than JSONL if get_session_records is updated
        res = logger_inst.get_session_records("*")
        VAULT_ENTRIES_COUNT.set(float(len(res)))
    except:
        pass


def record_machine_fault(tool: str, fault_code: str) -> None:
    """
    Record a machine-layer fault.
    IMPORTANT: This must NEVER be called for constitutional violations.
    Constitutional violations use record_void_event().
    """
    MACHINE_FAULTS.labels(fault_code=fault_code, tool=tool).inc()


def record_void_event(tool: str, void_reason: str) -> None:
    """
    Record a VOID verdict (constitutional violation only).
    IMPORTANT: This must NEVER be called for infrastructure/mechanical faults.
    Mechanical faults use record_machine_fault().
    """
    VOID_EVENTS.labels(void_reason=void_reason, tool=tool).inc()


# ---------------------------------------------------------------------------
# SCORE INTEGRITY PROTOCOL (FORGED 2026-03-13)
# ---------------------------------------------------------------------------

def compute_integrity_telemetry(
    # Measurements
    sources_cited: int = 0,
    ambiguities_resolved: int = 0,
    contradictions_flagged: int = 0,
    claim_ungrounded: bool = False,
    floors_passed: int = 13,
    hold_active: bool = False,
    options_offered: int = 1,
    response_tokens: int = 500,
    echo_debt_count: int = 0,
    total_claims: int = 1,
    my_sources_count: int = 0,
    dignity_flags: int = 0,
    reasoning_depth: int = 1,
    floor_activations: int = 1,
    tri_witness_confirmed: bool = False,
    human_intent_confirmed: bool = True,
) -> CanonicalMetrics:
    """
    Rule 2: How Each Score Is Actually Earned.
    Calculates the Public Score Card with strict basis tracking.
    """
    # 1. ΔS (Entropy Delta) - Basis: derived
    ds = -0.1 * sources_cited - 0.15 * ambiguities_resolved + 0.2 * contradictions_flagged
    if claim_ungrounded:
        ds += 0.1
    ds = round(ds, 1)

    # 2. Peace² (Lyapunov Stability) - Basis: derived
    peace2 = (floors_passed / 13.0) * 1.3 - (0.5 if hold_active else 0.0)
    peace2 = round(peace2, 2)

    # 3. G★ (Genius Score) - Basis: derived
    a = 0.9 if sources_cited > 0 else 0.5
    p = peace2 / 1.3
    x = 0.9 if options_offered >= 3 else 0.6
    e = 1.0 - (response_tokens / 2000.0)
    h = echo_debt_count * 0.1
    g_star = (a * p * x * (e ** 2)) * (1 - h)
    g_star = round(g_star, 2)

    # 4. κᵣ (Maruah Score) - Basis: derived | null
    if sources_cited == 0:
        kappa_r = None
    else:
        kappa_r = (my_sources_count / max(sources_cited, 1)) * 0.6 + 0.4 * (1 - dignity_flags * 0.2)
        kappa_r = round(kappa_r, 2)

    # 5. Ψ_LE (AGI Emergence Pressure) - Basis: heuristic
    psi_val = 0.8 + 0.05 * min(reasoning_depth, 4) + 0.05 * (1 if tri_witness_confirmed else 0) + 0.02 * floor_activations
    if not tri_witness_confirmed:
        psi_val = min(psi_val, 1.2)
    psi_le = f"{psi_val:.1f} (Estimate Only)"

    # 6. Confidence & Shadow
    shadow = round( (1 if claim_ungrounded else 0) / max(total_claims, 1), 2)
    confidence = round(g_star * (1 - shadow), 2)

    # 7. Verdict Logic
    if hold_active:
        verdict = "888_HOLD"
    elif peace2 < 1.0:
        verdict = "PAUSED"
    elif g_star < 0.80:
        verdict = "DEGRADED"
    else:
        verdict = "ALIVE"

    return CanonicalMetrics(
        telemetry=TelemetryVitals(
            ds=ds,
            peace2=peace2,
            kappa_r=kappa_r,
            G_star=g_star,
            echo_debt=round(float(max(echo_debt_count, 0.1)), 1),
            shadow=shadow,
            confidence=confidence,
            psi_le=psi_le,
            verdict=verdict
        ),
        basis=TelemetryBasis(),
        witness=TripleWitness(
            human=1.0 if human_intent_confirmed else 0.0,
            ai=round(peace2 / 1.3, 2),
            earth=kappa_r if kappa_r is not None else 0.9
        )
    )

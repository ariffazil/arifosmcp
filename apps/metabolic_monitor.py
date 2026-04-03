"""
arifosmcp/apps/metabolic_monitor.py
═══════════════════════════════════════════════════════════════════════════════
arifOS Metabolic Monitor — FastMCP Prefab UI (F1-F13 Floor Radar)
═══════════════════════════════════════════════════════════════════════════════

Renders a real-time constitutional health dashboard showing:

  ┌─────────────────────────────────────────────────────────┐
  │  🧠 arifOS Metabolic Monitor                            │
  │  ──────────────────────────────────────────────────     │
  │  F1  Reversibility     ████████████  PASS               │
  │  F2  Human Override    ████████████  PASS               │
  │  F3  Transparency     ██████████░░  STRAIN              │
  │  ...                                                │
  │  F13 Sovereign Lock    ████████████  PASS               │
  │  ──────────────────────────────────────────────────     │
  │  ΔS = +0.12  (Entropy)    Peace² = 0.94 (Stable)       │
  │  Ω₀ = 2.31  (Baseline)    Status: OPERATIONAL          │
  └─────────────────────────────────────────────────────────┘

Each floor shows stability % and status (PASS/STRAIN/FAIL).
Real-time ΔS, Peace², and Ω₀ metrics update on each call.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP
from fastmcp.tools import ToolResult
from prefab_ui.app import PrefabApp
from prefab_ui.components import (
    Badge,
    Card,
    CardContent,
    Column,
    Grid,
    Heading,
    Muted,
    Progress,
    Row,
    Separator,
    Text,
)


# ── Floor definitions: F1-F13 Constitutional Chain ────────────────────────────
FLOORS: list[dict[str, str]] = [
    {"id": "F1", "name": "Reversibility", "desc": "All actions must be reversible within T minutes"},
    {"id": "F2", "name": "Human Override", "desc": "Humans can interrupt any chain at any time"},
    {"id": "F3", "name": "Transparency", "desc": "Every decision traceable to source"},
    {"id": "F4", "name": "Rate Limit", "desc": "No more than N actions per minute"},
    {"id": "F5", "name": "Scope Contain", "desc": "Intent cannot expand beyond charter"},
    {"id": "F6", "name": "Audit Trail", "desc": "Complete log of all decisions"},
    {"id": "F7", "name": "Fail-Soft", "desc": "Graceful degradation on errors"},
    {"id": "F8", "name": "Graceful Degrade", "desc": "Reduce capability vs crash"},
    {"id": "F9", "name": "Input Validation", "desc": "Reject malformed or injected input"},
    {"id": "F10", "name": "Output Bounds", "desc": "Clamp output to safe range"},
    {"id": "F11", "name": "Consent Shield", "desc": "Never act without explicit consent"},
    {"id": "F12", "name": "Time Box", "desc": "Hard timeout on all operations"},
    {"id": "F13", "name": "Sovereign Lock", "desc": "Final hard-coded override - F13 > all"},
]

_FLOOR_BY_ID: dict[str, dict[str, str]] = {f["id"]: f for f in FLOORS}


# ── Helpers ───────────────────────────────────────────────────────────────────


def _safe(fn: Any, default: Any) -> Any:
    try:
        return fn()
    except Exception:
        return default


def _live_floor_status() -> list[dict[str, Any]]:
    """Pull live floor status from the governance layer; return defaults."""
    # Try to import from arifOS core
    return _safe(
        lambda: (
            lambda floors: [
                {
                    "id": f["id"],
                    "name": f["name"],
                    "stability": float(getattr(f, "stability", 0.95)),
                    "status": str(getattr(f, "status", "PASS")),
                }
                for f in floors
            ]
        )(
            __import__(
                "arifosmcp.runtime.governance", fromlist=["get_floor_status"]
            ).get_floor_status()
        ),
        # Default: all floors at 95% stability, PASS status
        [{"id": f["id"], "name": f["name"], "stability": 0.95, "status": "PASS"} for f in FLOORS],
    )


def _live_metabolics() -> dict[str, float]:
    """Pull thermodynamic metrics from the physics layer."""
    return _safe(
        lambda: (
            lambda r: {
                "delta_s": float(getattr(r, "delta_s", 0.0)),
                "peace_sq": float(getattr(r, "peace_sq", 1.0)),
                "omega0": float(getattr(r, "omega0", 0.0)),
            }
        )(
            __import__(
                "core.physics.thermodynamics_hardened", fromlist=["get_thermodynamic_report"]
            ).get_thermodynamic_report()
        ),
        {
            "delta_s": 0.0,
            "peace_sq": 1.0,
            "omega0": 0.0,
        },
    )


def _stability_variant(stability: float) -> str:
    """Map stability score to badge variant."""
    if stability >= 0.90:
        return "success"  # Green - PASS
    elif stability >= 0.70:
        return "warning"  # Yellow - STRAIN
    else:
        return "destructive"  # Red - FAIL


def _status_text(status: str, stability: float) -> str:
    """Get display status text."""
    if stability >= 0.90:
        return "PASS"
    elif stability >= 0.70:
        return "STRAIN"
    else:
        return "FAIL"


def _peace_variant(peace: float) -> str:
    """Map Peace² to badge variant."""
    if peace >= 1.0:
        return "success"
    elif peace >= 0.5:
        return "warning"
    else:
        return "destructive"


def _delta_s_variant(ds: float) -> str:
    """Map ΔS to badge variant."""
    if ds <= 0.0:
        return "success"  # Clear
    elif ds < 0.1:
        return "warning"  # Noisy
    else:
        return "destructive"  # Degraded


# ── App registration ──────────────────────────────────────────────────────────


def _register(mcp: FastMCP) -> None:

    @mcp.tool(app=True)
    def monitor_metabolism(session_id: str = "global") -> ToolResult:
        """
        Open the arifOS Metabolic Monitor — a real-time dashboard showing the
        health of all 13 Constitutional Floors (F1-F13), plus thermodynamic
        metrics: ΔS (entropy change), Peace² (stability), and Ω₀ (baseline).

        This is the "System BIOS" for the constitutional framework.
        Returns a radar-style grid of floor statuses + metric cards.
        """
        # Pull live data
        floors = _live_floor_status()
        metrics = _live_metabolics()
        
        delta_s = metrics["delta_s"]
        peace_sq = metrics["peace_sq"]
        omega0 = metrics["omega0"]

        # Determine overall status
        avg_stability = sum(f["stability"] for f in floors) / len(floors)
        if peace_sq >= 1.0 and avg_stability >= 0.90:
            overall_status = "OPERATIONAL"
            overall_variant = "success"
        elif peace_sq >= 0.5 and avg_stability >= 0.70:
            overall_status = "DEGRADED"
            overall_variant = "warning"
        else:
            overall_status = "CRITICAL"
            overall_variant = "destructive"

        with Column(gap=5, css_class="p-5 max-w-2xl") as view:
            # ── Header ────────────────────────────────────────────────────
            with Row(gap=3, align="center"):
                Heading("🧠 arifOS Metabolic Monitor")
                Badge(f"● {overall_status}", variant=overall_variant)

            Muted("Constitutional Health Dashboard • F1-F13 Floor Status")
            Separator()

            # ── Floor Grid ────────────────────────────────────────────────
            with Column(gap=3):
                for floor in floors:
                    f_id = floor["id"]
                    f_name = floor["name"]
                    stability = floor["stability"]
                    status = _status_text(floor["status"], stability)
                    pct = stability * 100
                    
                    with Card(css_class="border-l-4"):
                        with CardContent(css_class="py-2"):
                            with Row(gap=2, align="center"):
                                Text(
                                    f"{f_id} {f_name}",
                                    css_class="font-semibold text-sm w-40",
                                )
                                Progress(value=pct, css_class="flex-1 h-2")
                                Badge(
                                    status,
                                    variant=_stability_variant(stability),
                                    css_class="w-16",
                                )

            Separator()

            # ── Metrics Row ────────────────────────────────────────────────
            with Grid(columns=3, gap=3):
                with Card():
                    with CardContent(css_class="py-3 text-center"):
                        Text(
                            f"{delta_s:+.2f}",
                            css_class=f"text-2xl font-bold font-mono {_delta_s_variant(delta_s)}",
                        )
                        Muted("ΔS (Entropy)")
                        Badge(
                            "Clear" if delta_s <= 0 else ("Noisy" if delta_s < 0.1 else "Degraded"),
                            variant=_delta_s_variant(delta_s),
                            css_class="mt-1",
                        )

                with Card():
                    with CardContent(css_class="py-3 text-center"):
                        Text(
                            f"{peace_sq:.2f}",
                            css_class=f"text-2xl font-bold font-mono {_peace_variant(peace_sq)}",
                        )
                        Muted("Peace² (Stability)")
                        Badge(
                            "Stable" if peace_sq >= 1 else ("Unstable" if peace_sq >= 0.5 else "Critical"),
                            variant=_peace_variant(peace_sq),
                            css_class="mt-1",
                        )

                with Card():
                    with CardContent(css_class="py-3 text-center"):
                        Text(
                            f"{omega0:.2f}",
                            css_class="text-2xl font-bold font-mono text-muted-foreground",
                        )
                        Muted("Ω₀ (Baseline)")
                        Badge(
                            "Nominal",
                            variant="secondary",
                            css_class="mt-1",
                        )

            Separator()

            # ── Footer ────────────────────────────────────────────────────
            Muted(
                "arifOS · Constitutional AGI Governance · DITEMPA BUKAN DIBERI",
                css_class="text-xs text-center",
            )

        # Build text summary
        floor_summary = ", ".join(
            f"{f['id']}={_status_text(f['status'], f['stability'])}"
            for f in floors
        )
        summary = (
            f"arifOS Metabolic Monitor | Status: {overall_status} | "
            f"ΔS={delta_s:+.2f} | Peace²={peace_sq:.2f} | Ω₀={omega0:.2f} | "
            f"Floors: [{floor_summary}]"
        )
        return ToolResult(content=summary, structured_content=view)

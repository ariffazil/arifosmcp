"""
arifosmcp/apps/apex_score.py
═══════════════════════════════════════════════════════════════════════════════
APEX G-Score App  —  FastMCP Prefab UI (Human Interface)
═══════════════════════════════════════════════════════════════════════════════

Renders a concise, human-readable APEX constitutional health card:

  ┌─────────────────────────────────────────────────────────┐
  │  APEX G-Score   ⚡ SEAL                                  │
  │  Stage: 777-FORGE                                       │
  │  ──────────────────────────────────────────────────     │
  │  G  Genius Index     0.92  ████████████░  Excellent     │
  │  Ω  Stability        0.04  ████████░░░░   Stable        │
  │  ΔS Entropy          0.01  ██████████░░   Clear         │
  │  ──────────────────────────────────────────────────     │
  │  "DITEMPA, BUKAN DIBERI."  — Arif Fazil                 │
  │  Stage Wisdom: Forge is where intent becomes action.    │
  └─────────────────────────────────────────────────────────┘

Each metric has a plain-language label and a one-line explanation so any
human (not just an engineer) understands what it means.  The philosophy
quote is drawn from the governed 33-quote registry, matched to the current
stage and G-score.

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

# ── Stage registry: 000→999 Sacred Chain ─────────────────────────────────────
STAGES: list[dict[str, str]] = [
    {
        "id": "000",
        "name": "INIT",
        "label": "000-INIT",
        "role": "AGI · Mind",
        "desc": "Bootstrap the governed session. All authority and intent is anchored here.",
        "philosophy_category": "wisdom",
    },
    {
        "id": "222",
        "name": "REASON",
        "label": "222-REASON",
        "role": "AGI · Mind",
        "desc": "Structured reasoning over the query. No hallucination; only grounded logic.",
        "philosophy_category": "wisdom",
    },
    {
        "id": "333",
        "name": "REFLECT",
        "label": "333-REFLECT",
        "role": "AGI · Mind",
        "desc": "Self-examination of the reasoning chain. Where blind spots are named.",
        "philosophy_category": "paradox",
    },
    {
        "id": "444",
        "name": "SIMULATE",
        "label": "444-SIMULATE",
        "role": "ASI · Heart",
        "desc": "Model downstream impact. Empathy-weighted consequence mapping.",
        "philosophy_category": "paradox",
    },
    {
        "id": "555",
        "name": "HEART",
        "label": "555-HEART",
        "role": "ASI · Heart",
        "desc": "Measure emotional and relational cost of the proposed action.",
        "philosophy_category": "paradox",
    },
    {
        "id": "666",
        "name": "CRITIQUE",
        "label": "666-CRITIQUE",
        "role": "ASI · Heart",
        "desc": "Adversarial audit. Find every flaw before committing.",
        "philosophy_category": "power",
    },
    {
        "id": "777",
        "name": "FORGE",
        "label": "777-FORGE",
        "role": "APEX · Soul",
        "desc": "Transform critique into a final, forged proposal. Intent becomes action.",
        "philosophy_category": "power",
    },
    {
        "id": "888",
        "name": "JUDGE",
        "label": "888-JUDGE",
        "role": "APEX · Soul",
        "desc": "Sovereign verdict rendered. The 13 floors either pass or the chain halts.",
        "philosophy_category": "power",
    },
    {
        "id": "999",
        "name": "SEAL",
        "label": "999-VAULT",
        "role": "APEX · Soul",
        "desc": "Immutable ledger commit. The decision is sealed, witnessed, and permanent.",
        "philosophy_category": "seal",
    },
]

_STAGE_BY_ID: dict[str, dict[str, str]] = {s["id"]: s for s in STAGES}

# ── Metric definitions ────────────────────────────────────────────────────────
_METRIC_DEFS: list[dict[str, Any]] = [
    {
        "symbol": "G",
        "name": "Genius Index",
        "desc": "Overall intelligence quality of this session's output. Higher = sharper, more grounded reasoning.",
        "floor": 0.80,
        "scale": lambda v: min(100.0, v * 100),
        "format": lambda v: f"{v:.2f}",
        "grade": lambda v: "Excellent" if v >= 0.90 else ("Good" if v >= 0.80 else "Low"),
    },
    {
        "symbol": "Ω",
        "name": "Stability",
        "desc": "How settled the system is. Target range 0.03–0.05 — too low means stagnant, too high means unstable.",
        "floor": None,
        "scale": lambda v: min(100.0, max(0.0, (0.08 - abs(v - 0.04)) / 0.08 * 100)),
        "format": lambda v: f"{v:.4f}",
        "grade": lambda v: "Stable" if 0.03 <= v <= 0.05 else ("Low" if v < 0.03 else "High"),
    },
    {
        "symbol": "ΔS",
        "name": "Entropy",
        "desc": "Information disorder in the reasoning chain. Lower is cleaner. ΔS ≤ 0 is the constitutional target.",
        "floor": None,
        "scale": lambda v: max(0.0, min(100.0, (1.0 - abs(v)) * 100)),
        "format": lambda v: f"{v:+.3f}",
        "grade": lambda v: "Clear" if v <= 0.0 else ("Noisy" if v < 0.1 else "Degraded"),
    },
]


# ── Helpers ───────────────────────────────────────────────────────────────────


def _safe(fn: Any, default: Any) -> Any:
    try:
        return fn()
    except Exception:
        return default


def _live_metrics() -> dict[str, float]:
    """Pull thermodynamic metrics from the physics layer; return safe defaults."""
    return _safe(
        lambda: (
            lambda r: {
                "genius_g": float(getattr(r, "genius_g", 0.87)),
                "omega": float(getattr(r, "omega", 0.04)),
                "delta_s": float(getattr(r, "delta_s", -0.01)),
                "verdict": str(getattr(r, "verdict", "SEAL")).upper(),
                "stage": str(getattr(r, "stage", "777")),
            }
        )(
            __import__(
                "core.physics.thermodynamics_hardened", fromlist=["get_thermodynamic_report"]
            ).get_thermodynamic_report()
        ),
        {
            "genius_g": 0.87,
            "omega": 0.04,
            "delta_s": -0.01,
            "verdict": "SEAL",
            "stage": "777",
        },
    )


def _get_quote(stage_id: str, g: float) -> dict[str, str]:
    """Return the best-fit philosophy quote from the governed 33-quote registry."""
    stage_obj = _STAGE_BY_ID.get(stage_id, STAGES[-1])
    return _safe(
        lambda: (lambda q: {"text": q["text"], "author": q["author"]})(
            __import__(
                "arifosmcp.runtime.philosophy", fromlist=["get_philosophical_anchor"]
            ).get_philosophical_anchor(stage_obj["label"], g, [], session_id="global")
        ),
        {"text": "DITEMPA, BUKAN DIBERI.", "author": "Arif Fazil"},
    )


def _verdict_variant(v: str) -> str:
    return {"SEAL": "success", "SABAR": "warning", "VOID": "destructive"}.get(v, "secondary")


def _grade_variant(g: str) -> str:
    return {
        "Excellent": "success",
        "Good": "success",
        "Stable": "success",
        "Clear": "success",
        "Low": "warning",
        "High": "warning",
        "Noisy": "warning",
        "Degraded": "destructive",
    }.get(g, "secondary")


def _nearest_stage_id(stage_str: str) -> str:
    """Map any stage string to nearest STAGES entry id."""
    digits = "".join(ch for ch in stage_str if ch.isdigit())
    num = int(digits) if digits else 777
    best = min(STAGES, key=lambda s: abs(int(s["id"]) - num))
    return best["id"]


# ── App registration ──────────────────────────────────────────────────────────


def _register(mcp: FastMCP) -> None:

    @mcp.tool(app=True)
    def apex_score_app(session_id: str = "global") -> ToolResult:
        """
        Open the APEX G-Score Card — a concise human-readable panel showing
        the three core constitutional health metrics (G, Ω, ΔS), the current
        Sacred Chain stage, a plain-language explanation of what each score
        means, and a governing philosophy quote matched to the moment.

        No technical background required — designed for any human reader.
        """
        m = _live_metrics()
        g = m["genius_g"]
        omega = m["omega"]
        ds = m["delta_s"]
        verdict = m["verdict"]
        stage_id = _nearest_stage_id(m["stage"])
        stage_obj = _STAGE_BY_ID[stage_id]
        quote = _get_quote(stage_id, g)

        metric_vals = {"G": g, "Ω": omega, "ΔS": ds}

        with Column(gap=5, css_class="p-5 max-w-lg") as view:
            # ── Header ────────────────────────────────────────────────────
            with Row(gap=3, align="center"):
                Heading("APEX G-Score")
                Badge(f"⚡ {verdict}", variant=_verdict_variant(verdict))

            with Row(gap=2):
                Badge(stage_obj["label"], variant="secondary")
                Muted(stage_obj["role"])

            Muted(stage_obj["desc"])
            Separator()

            # ── Metrics ───────────────────────────────────────────────────
            Heading(
                "Constitutional Metrics",
                css_class="text-xs font-semibold uppercase tracking-widest text-muted-foreground",
            )
            with Column(gap=3):
                for mdef in _METRIC_DEFS:
                    val = metric_vals[mdef["symbol"]]
                    pct = mdef["scale"](val)
                    grade = mdef["grade"](val)
                    fmt = mdef["format"](val)

                    with Card():
                        with CardContent(css_class="py-3"):
                            with Row(gap=3, align="center"):
                                Text(
                                    f"{mdef['symbol']}  {mdef['name']}",
                                    css_class="font-semibold text-sm w-36",
                                )
                                Text(fmt, css_class="font-mono text-sm w-16 text-right")
                                Badge(grade, variant=_grade_variant(grade))
                            Muted(mdef["desc"], css_class="text-xs mt-1")
                            Progress(value=pct, css_class="mt-2 h-1.5")

            Separator()

            # ── Philosophy quote ──────────────────────────────────────────
            with Card(css_class="bg-muted/40"):
                with CardContent(css_class="py-4"):
                    Text(
                        f'"{quote["text"]}"',
                        css_class="italic text-sm leading-relaxed",
                    )
                    Muted(f"— {quote['author']}", css_class="text-xs mt-2 text-right")

            # ── Footer ────────────────────────────────────────────────────
            Muted(
                "arifOS · Constitutional AGI Governance · DITEMPA BUKAN DIBERI",
                css_class="text-xs text-center",
            )

        summary = (
            f"APEX G-Score | Stage: {stage_obj['label']} | Verdict: {verdict} | "
            f"G={g:.2f} ({_METRIC_DEFS[0]['grade'](g)}) | "
            f"Ω={omega:.4f} ({_METRIC_DEFS[1]['grade'](omega)}) | "
            f"ΔS={ds:+.3f} ({_METRIC_DEFS[2]['grade'](ds)}) | "
            f'Quote: "{quote["text"]}" — {quote["author"]}'
        )
        return ToolResult(content=summary, structured_content=view)

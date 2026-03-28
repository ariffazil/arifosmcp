"""
arifosmcp/apps/stage_pipeline.py
═══════════════════════════════════════════════════════════════════════════════
000→999 Sacred Chain Pipeline App  —  FastMCP Prefab UI (Human Interface)
═══════════════════════════════════════════════════════════════════════════════

Renders a visual, human-readable pipeline of the complete arifOS Sacred Chain:

  000-INIT  →  222-REASON  →  333-REFLECT  →  444-SIMULATE
  →  555-HEART  →  666-CRITIQUE  →  777-FORGE  →  888-JUDGE  →  999-SEAL

Each stage card shows:
  • Stage number + name
  • Organ tier: AGI (Mind) / ASI (Heart) / APEX (Soul)
  • One-sentence plain-English explanation of what happens at that stage
  • Status badge: ACTIVE (current) / COMPLETE / PENDING
  • The governing philosophy quote for this stage

The currently active stage is highlighted.  Completed stages show a check.
The whole panel updates in real-time from the live session state.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP
from fastmcp.tools import ToolResult
from prefab_ui.app import PrefabApp
from prefab_ui.components import (
    Accordion,
    AccordionItem,
    Badge,
    Card,
    CardContent,
    Column,
    Heading,
    Muted,
    Row,
    Separator,
    Text,
)

# ── Full Sacred Chain definition ──────────────────────────────────────────────
CHAIN: list[dict[str, Any]] = [
    {
        "id": "000", "name": "INIT",     "label": "000-INIT",
        "tier": "AGI · Mind",
        "color": "secondary",
        "desc": "Session anchor. Intent, authority, and actor identity are locked in. Nothing runs without this.",
        "what": "The system wakes up, checks who is asking and why, and commits the session to the governed chain.",
        "quote_id": "W9",   # Francis Bacon — "Knowledge itself is power."
        "quote": "Knowledge itself is power.",
        "author": "Francis Bacon",
    },
    {
        "id": "222", "name": "REASON",   "label": "222-REASON",
        "tier": "AGI · Mind",
        "color": "secondary",
        "desc": "Structured reasoning. The AGI works through the problem with logic, not assumption.",
        "what": "Like a judge reading every clause before ruling — no shortcuts, no guessing.",
        "quote_id": "W8",   # Carl Sagan
        "quote": "Extraordinary claims require extraordinary evidence.",
        "author": "Carl Sagan",
    },
    {
        "id": "333", "name": "REFLECT",  "label": "333-REFLECT",
        "tier": "AGI · Mind",
        "color": "secondary",
        "desc": "Self-audit of the reasoning chain. The system looks for its own blind spots.",
        "what": "What did I miss? What assumption did I make? Naming the gap before it becomes a mistake.",
        "quote_id": "W1",   # Socrates
        "quote": "The only true wisdom is in knowing you know nothing.",
        "author": "Socrates",
    },
    {
        "id": "444", "name": "SIMULATE", "label": "444-SIMULATE",
        "tier": "ASI · Heart",
        "color": "secondary",
        "desc": "Consequence mapping. Every downstream effect of the proposed action is modelled.",
        "what": "If we do this — who is affected? How? Playing it forward before pulling the trigger.",
        "quote_id": "R5",   # Kierkegaard
        "quote": "Life can only be understood backwards; but it must be lived forwards.",
        "author": "Søren Kierkegaard",
    },
    {
        "id": "555", "name": "HEART",    "label": "555-HEART",
        "tier": "ASI · Heart",
        "color": "secondary",
        "desc": "Empathy layer. The emotional and relational cost of the action is measured.",
        "what": "Not just 'is this correct?' but 'is this kind?' The kr Empathy coefficient scores this.",
        "quote_id": "R4",   # Pascal
        "quote": "The heart has its reasons which reason knows nothing of.",
        "author": "Blaise Pascal",
    },
    {
        "id": "666", "name": "CRITIQUE", "label": "666-CRITIQUE",
        "tier": "ASI · Heart",
        "color": "secondary",
        "desc": "Adversarial audit. The system tries to break its own proposal before committing.",
        "what": "Red-team mode: find every flaw, every risk, every way this could go wrong. Fix it first.",
        "quote_id": "R7",   # Bertrand Russell
        "quote": "The trouble with the world is that the stupid are cocksure and the intelligent are full of doubt.",
        "author": "Bertrand Russell",
    },
    {
        "id": "777", "name": "FORGE",    "label": "777-FORGE",
        "tier": "APEX · Soul",
        "color": "secondary",
        "desc": "Synthesis. Critique is hammered into a final, forged proposal. Intent becomes action.",
        "what": "DITEMPA BUKAN DIBERI — Forged, Not Given. This is where the raw idea becomes a finished artefact.",
        "quote_id": "P5",   # Edison
        "quote": "Genius is one percent inspiration and ninety-nine percent perspiration.",
        "author": "Thomas Edison",
    },
    {
        "id": "888", "name": "JUDGE",    "label": "888-JUDGE",
        "tier": "APEX · Soul",
        "color": "secondary",
        "desc": "Sovereign verdict. All 13 constitutional floors are evaluated. Pass = proceed; Fail = halt.",
        "what": "The final checkpoint. The 888-Judge has no sympathy for incomplete work. SEAL or SABAR or VOID.",
        "quote_id": "P6",   # Churchill
        "quote": "Success is not final, failure is not fatal: it is the courage to continue that counts.",
        "author": "Winston Churchill",
    },
    {
        "id": "999", "name": "SEAL",     "label": "999-VAULT",
        "tier": "APEX · Soul",
        "color": "success",
        "desc": "Immutable commit. The verdict is sealed into the VAULT999 Merkle-hash chain. Permanent.",
        "what": "The ledger remembers. Every sealed decision is a brick in the constitutional record.",
        "quote_id": "S1",   # Arif Fazil
        "quote": "DITEMPA, BUKAN DIBERI.",
        "author": "Arif Fazil",
    },
]

_TIER_VARIANT: dict[str, str] = {
    "AGI · Mind":  "secondary",
    "ASI · Heart": "warning",
    "APEX · Soul": "success",
}


def _safe(fn: Any, default: Any) -> Any:
    try:
        return fn()
    except Exception:
        return default


def _live_stage() -> str:
    """Return the current stage id string from the physics layer, or '777'."""
    return _safe(
        lambda: str(getattr(
            __import__(
                "core.physics.thermodynamics_hardened",
                fromlist=["get_thermodynamic_report"],
            ).get_thermodynamic_report(),
            "stage", "777",
        )),
        "777",
    )


def _live_g() -> float:
    return _safe(
        lambda: float(getattr(
            __import__(
                "core.physics.thermodynamics_hardened",
                fromlist=["get_thermodynamic_report"],
            ).get_thermodynamic_report(),
            "genius_g", 0.87,
        )),
        0.87,
    )


def _nearest_stage_id(stage_str: str) -> str:
    digits = "".join(ch for ch in stage_str if ch.isdigit())
    num = int(digits) if digits else 777
    return min(CHAIN, key=lambda s: abs(int(s["id"]) - num))["id"]


def _stage_status(stage_id: str, active_id: str) -> tuple[str, str]:
    """Return (status_label, badge_variant) for a stage relative to active."""
    s = int(stage_id)
    a = int(active_id)
    if s < a:
        return "✓ DONE",    "success"
    if s == a:
        return "◉ ACTIVE",  "default"
    return "○ PENDING", "secondary"


# ── App registration ──────────────────────────────────────────────────────────

def _register(mcp: FastMCP) -> None:

    @mcp.tool(app=True)
    def stage_pipeline_app(session_id: str = "global") -> ToolResult:
        """
        Open the 000→999 Sacred Chain Pipeline — a full visual map of the
        nine arifOS governance stages from INIT to SEAL, each explained in
        plain English with its role (AGI Mind / ASI Heart / APEX Soul),
        current status, and the philosophy quote that governs it.

        Designed for any human reader — no technical knowledge required.
        """
        raw_stage = _live_stage()
        active_id = _nearest_stage_id(raw_stage)
        g         = _live_g()
        active    = next(s for s in CHAIN if s["id"] == active_id)

        with Column(gap=5, css_class="p-5") as view:

            # ── Header ─────────────────────────────────────────────────────
            Heading("Sacred Chain  000 → 999")
            with Row(gap=2):
                Badge(f"Active: {active['label']}", variant="default")
                Badge(active["tier"], variant=_TIER_VARIANT[active["tier"]])
                Badge(f"G = {g:.2f}", variant="secondary")

            Muted(
                "The arifOS Sacred Chain is the mandatory governance pipeline every "
                "AI action must complete before being sealed into the immutable ledger.",
            )
            Separator()

            # ── Stage accordion ────────────────────────────────────────────
            with Accordion(multiple=False):
                for stage in CHAIN:
                    status_label, status_variant = _stage_status(stage["id"], active_id)
                    is_active = stage["id"] == active_id

                    # Accordion header: "777-FORGE  ◉ ACTIVE  APEX · Soul"
                    header_text = (
                        f"{stage['label']}  {status_label}  ·  {stage['tier']}"
                    )

                    with AccordionItem(header_text):
                        with Card(css_class="border-0 shadow-none bg-muted/30" if not is_active else "border border-primary/40"):
                            with CardContent(css_class="py-3"):

                                # Role badge + status
                                with Row(gap=2, css_class="mb-2"):
                                    Badge(status_label, variant=status_variant)
                                    Badge(stage["tier"], variant=_TIER_VARIANT[stage["tier"]])

                                # Plain-English description
                                Text(stage["desc"], css_class="text-sm font-medium")
                                Muted(stage["what"], css_class="text-xs mt-1 leading-relaxed")

                                Separator(css_class="my-2")

                                # Philosophy quote
                                Muted(
                                    f'"{stage["quote"]}"',
                                    css_class="text-xs italic",
                                )
                                Muted(
                                    f"— {stage['author']}",
                                    css_class="text-xs text-right",
                                )

            Separator()
            Muted(
                "arifOS · Constitutional AGI Governance · DITEMPA BUKAN DIBERI",
                css_class="text-xs text-center",
            )

        completed = sum(1 for s in CHAIN if int(s["id"]) < int(active_id))
        summary = (
            f"Sacred Chain Pipeline | Active: {active['label']} ({active['tier']}) | "
            f"G={g:.2f} | {completed}/9 stages complete | "
            f"Quote: \"{active['quote']}\" — {active['author']}"
        )
        return ToolResult(content=summary, structured_content=view)

"""
arifosmcp/apps — FastMCP Prefab UI Apps for arifOS.

Human-interface layer: concise APEX G-score metrics, stage pipeline,
philosophy quotes, and constitutional floor explanations rendered as
interactive Prefab UI iframes inside the MCP host conversation.

Apps
----
apex_score_app       — APEX G-score panel: stage, metrics, philosophy, verdict
stage_pipeline_app   — 000→999 Sacred Chain visualiser with per-stage status
metabolic_monitor    — F1-F13 floor radar with ΔS, Peace², Ω₀ metrics

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from .apex_score import _register as register_apex_score
from .stage_pipeline import _register as register_stage_pipeline
from .metabolic_monitor import _register as register_metabolic_monitor

__all__ = [
    "register_apex_score",
    "register_stage_pipeline",
    "register_metabolic_monitor",
]

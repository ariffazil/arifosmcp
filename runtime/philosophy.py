"""
arifosmcp/runtime/philosophy.py — arifOS Philosophy Atlas

27-zone philosophical coordinate system for governed intelligence.
S × G × Ω = 3D space for deterministic quote selection.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
from pathlib import Path
from typing import Any, TypedDict

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# ATLAS LOADING
# ═══════════════════════════════════════════════════════════════════════════════

ATLAS_PATH = Path(__file__).resolve().parents[2] / "data" / "philosophy_atlas.json"
_ATLAS_CACHE: dict[str, Any] | None = None


def _load_atlas() -> dict[str, Any]:
    """Load the philosophy atlas from JSON."""
    global _ATLAS_CACHE
    if _ATLAS_CACHE is not None:
        return _ATLAS_CACHE

    if not ATLAS_PATH.exists():
        logger.warning(f"Philosophy atlas not found at {ATLAS_PATH}")
        return {"zones": [], "motto": {}}

    with open(ATLAS_PATH, encoding="utf-8") as f:
        _ATLAS_CACHE = json.load(f)
    return _ATLAS_CACHE


# ═══════════════════════════════════════════════════════════════════════════════
# SCORE COMPUTATION
# ═══════════════════════════════════════════════════════════════════════════════


class AtlasScores(TypedDict):
    """Score inputs for philosophy selection."""

    delta_s: float  # Entropy delta: ≤0 = +1 (alive), >0 = -1 (void)
    g_score: float  # G-score: 0-1 (Genius/Vitality)
    omega_score: float  # Humility score: 0-1 (F7 band)
    lyapunov_sign: str  # "increasing" | "decreasing" | "stable"
    verdict: str  # "SEAL" | "SABAR" | "HOLD" | "VOID"
    session_stage: str  # "INIT" | "SEAL" | normal stage string


def compute_S(delta_s: float) -> int:
    """Compute S (Ultimate Survival) from delta_s."""
    # ΔS ≤ 0 → S = +1 (clarity, entropy controlled, alive)
    # ΔS > 0 → S = -1 (entropy violated, void)
    return 1 if delta_s <= 0 else -1


def compute_G(g_score: float) -> float:
    """Compute G (Genius) from g_score."""
    # Map g_score 0-1 to atlas G values: 0, 0.5, 1
    if g_score < 0.33:
        return 0.0
    elif g_score < 0.66:
        return 0.5
    else:
        return 1.0


def compute_Omega(omega_score: float, g_score: float, verdict: str) -> float:
    """Compute Ω (Humility) using hybrid mapping."""
    # Hybrid: continuous score mapped to binary buckets (High/Med/Low)
    # But we use 0, 0.5, 1 for atlas coordinates

    # Base Ω on omega_score (F7 band proxy)
    if omega_score < 0.03:
        raw_omega = 0.0  # Certainty bias
    elif omega_score < 0.05:
        raw_omega = 0.5  # Within F7 band
    else:
        raw_omega = 1.0  # High uncertainty

    # Adjust based on G and verdict for contrast
    if g_score >= 0.8 and verdict == "SEAL":
        # High capability + success → slightly lower humility (confident)
        return max(0.0, raw_omega - 0.5)
    elif verdict in ("VOID", "HOLD"):
        # Failure states → higher humility acknowledgment
        return min(1.0, raw_omega + 0.5)
    else:
        return raw_omega


def compute_3d_coordinates(scores: AtlasScores) -> tuple[float, float, float]:
    """Compute the 3D coordinate (S, G, Ω) from score inputs."""
    S = float(compute_S(scores["delta_s"]))
    G = compute_G(scores["g_score"])
    Omega = compute_Omega(scores["omega_score"], scores["g_score"], scores["verdict"])
    return (S, G, Omega)


# ═══════════════════════════════════════════════════════════════════════════════
# DISTANCE AND SELECTION
# ═══════════════════════════════════════════════════════════════════════════════


def euclidean_distance_3d(
    coord1: tuple[float, float, float], coord2: tuple[float, float, float]
) -> float:
    """Compute 3D Euclidean distance."""
    return math.sqrt(
        (coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2 + (coord1[2] - coord2[2]) ** 2
    )


def find_nearest_zone(
    atlas: dict[str, Any], target_coord: tuple[float, float, float]
) -> dict[str, Any]:
    """Find the zone with minimum distance to target coordinate."""
    zones = atlas.get("zones", [])
    if not zones:
        return {"id": "Z01", "name": "Humble Sovereign", "quotes": []}

    best_zone = zones[0]
    best_distance = float("inf")

    for zone in zones:
        zone_coord = (zone.get("S", 0), zone.get("G", 0), zone.get("Omega", 0))
        distance = euclidean_distance_3d(target_coord, zone_coord)
        if distance < best_distance:
            best_distance = distance
            best_zone = zone

    return best_zone


def deterministic_select_from_zone(
    zone: dict[str, Any], session_id: str, context: str = "", contrast_override: str | None = None
) -> dict[str, Any]:
    """Deterministically select a quote from a zone using session_id hash."""
    quotes = zone.get("quotes", [])
    if not quotes:
        return {
            "quote_id": "NONE",
            "quote": "The silence between words holds truth.",
            "author": "arifOS Atlas",
            "category": zone.get("name", "Unknown"),
            "zone_id": zone.get("id", "Z??"),
            "source": "atlas_fallback",
        }

    # If contrast_override specified, try to find matching contrast
    if contrast_override:
        for q in quotes:
            if q.get("contrast") == contrast_override:
                return _format_quote(q, zone)

    # Deterministic selection using hash
    seed_string = f"{session_id}:{context}:{zone.get('id', 'Z00')}"
    seed_hash = hashlib.sha256(seed_string.encode()).hexdigest()
    idx = int(seed_hash[:8], 16) % len(quotes)

    return _format_quote(quotes[idx], zone)


def _format_quote(quote: dict[str, Any], zone: dict[str, Any]) -> dict[str, Any]:
    """Format a quote for output."""
    return {
        "quote_id": quote.get("id", "UNKNOWN"),
        "quote": quote.get("text", ""),
        "author": quote.get("author", "Unknown"),
        "source": quote.get("source", ""),
        "year": quote.get("year", ""),
        "category": zone.get("name", "Unknown"),
        "zone_id": zone.get("id", "Z??"),
        "contrast": quote.get("contrast", ""),
        "S": zone.get("S", 0),
        "G": zone.get("G", 0),
        "Omega": zone.get("Omega", 0),
        "character": zone.get("character", ""),
        "source_type": "atlas_27",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC API: ATLAS-BASED PHILOSOPHY SELECTION
# ═══════════════════════════════════════════════════════════════════════════════


def select_atlas_philosophy(
    scores: AtlasScores,
    session_id: str = "global",
    context: str = "",
    contrast_override: str | None = None,
) -> dict[str, Any]:
    """
    Select philosophical anchor using 27-zone atlas.

    Algorithm:
    1. Compute (S, G, Ω) from score metrics
    2. Find nearest zone via 3D Euclidean distance
    3. Deterministic quote selection within zone
    4. Special handling for INIT/SEAL sessions
    """
    atlas = _load_atlas()

    # Special handling: INIT and SEAL sessions get motto
    if scores.get("session_stage") in ("INIT", "SEAL") or scores.get("verdict") == "SEAL":
        motto = atlas.get("motto", {})
        if motto:
            # Return motto as primary, plus a zone quote
            return {
                "motto": {
                    "text": motto.get("text", "DITEMPA, BUKAN DIBERI."),
                    "author": motto.get("author", "Arif Fazil"),
                    "note": motto.get("note", "For INIT and SEAL sessions"),
                    "is_motto": True,
                },
                "primary_quote": _get_zone_quote_for_motto(atlas, session_id, "Z01"),
                "zone": atlas["zones"][0] if atlas.get("zones") else {},
                "coordinates": (1.0, 1.0, 1.0),  # Z01 coordinates
                "selection_type": "init_seal_motto",
            }

    # Compute 3D coordinates from scores
    coordinates = compute_3d_coordinates(scores)
    S, G, Omega = coordinates

    # Find nearest zone
    zone = find_nearest_zone(atlas, coordinates)

    # Select quote from zone
    quote = deterministic_select_from_zone(zone, session_id, context, contrast_override)

    return {
        "motto": None,
        "primary_quote": quote,
        "zone": {
            "id": zone.get("id"),
            "name": zone.get("name"),
            "character": zone.get("character"),
            "S": zone.get("S"),
            "G": zone.get("G"),
            "Omega": zone.get("Omega"),
        },
        "coordinates": coordinates,
        "score_inputs": {
            "delta_s": scores.get("delta_s", 0),
            "g_score": scores.get("g_score", 0.5),
            "omega_score": scores.get("omega_score", 0.05),
            "verdict": scores.get("verdict", "SABAR"),
        },
        "selection_type": "atlas_27",
    }


def _get_zone_quote_for_motto(
    atlas: dict[str, Any], session_id: str, zone_id: str = "Z01"
) -> dict[str, Any]:
    """Get a philosophical quote to accompany motto for INIT/SEAL."""
    zones = atlas.get("zones", [])
    zone = next((z for z in zones if z.get("id") == zone_id), zones[0] if zones else {})
    return deterministic_select_from_zone(zone, session_id, "motto_accompaniment")


# ═══════════════════════════════════════════════════════════════════════════════
# LEGACY COMPATIBILITY
# ═══════════════════════════════════════════════════════════════════════════════

# Keep legacy constants for backward compatibility
LOCAL_99_LABELS: tuple[str, ...] = (
    "scar",
    "triumph",
    "paradox",
    "wisdom",
    "power",
    "love",
    "seal",
)

PHILOSOPHY_REGISTRY: list[dict[str, str]] = [
    {
        "id": "W1",
        "category": "wisdom",
        "author": "Socrates",
        "text": "The only true wisdom is in knowing you know nothing.",
    },
    {
        "id": "W2",
        "category": "wisdom",
        "author": "Aristotle",
        "text": "Knowing yourself is the beginning of all wisdom.",
    },
    {
        "id": "P1",
        "category": "power",
        "author": "Napoleon Bonaparte",
        "text": "Impossible is a word to be found only in the dictionary of fools.",
    },
    {
        "id": "R1",
        "category": "paradox",
        "author": "Heraclitus",
        "text": "The only constant in life is change.",
    },
    {
        "id": "V1",
        "category": "void",
        "author": "Kurt Gödel",
        "text": "Either mathematics is too big for the human mind, or the human mind is more than a machine.",
    },
    {"id": "S1", "category": "seal", "author": "Arif Fazil", "text": "DITEMPA, BUKAN DIBERI."},
]


class Quote(TypedDict):
    id: str
    category: str
    author: str
    text: str


class PhilosophySelection(TypedDict):
    apex_mode: str
    role: str
    stage: str
    g_score: float
    label: str
    label_source: str
    semantic_backend: str
    is_pseudo: bool
    available_categories: dict[str, list[str]]
    agi: dict[str, Any] | None
    asi: dict[str, Any] | None
    apex: dict[str, Any] | None


# Legacy function - now wraps atlas selection
def select_governed_philosophy(
    context: str = "",
    stage: str = "444",
    verdict: str = "SABAR",
    g_score: float = 0.5,
    failed_floors: list[str] | None = None,
    session_id: str = "global",
    delta_s: float = 0.0,
    omega_score: float = 0.05,
) -> PhilosophySelection:
    """
    Legacy API for backward compatibility.
    Now delegates to atlas-based selection.
    """
    scores = AtlasScores(
        delta_s=delta_s,
        g_score=g_score,
        omega_score=omega_score,
        lyapunov_sign="stable",
        verdict=verdict,
        session_stage=stage,
    )

    result = select_atlas_philosophy(scores, session_id, context)

    # Convert to legacy format
    primary = result.get("primary_quote", {})

    return {
        "apex_mode": "atlas_27",
        "role": _infer_role_from_stage(stage),
        "stage": stage,
        "g_score": g_score,
        "label": result.get("zone", {}).get("name", "Unknown"),
        "label_source": "atlas_27",
        "semantic_backend": "euclidean_3d",
        "is_pseudo": False,
        "available_categories": {
            "atlas_zones": [z["id"] for z in _load_atlas().get("zones", [])],
            "legacy_33": ["wisdom", "power", "paradox", "void", "seal"],
        },
        "agi": primary if result.get("zone", {}).get("id", "").startswith("Z1") else None,
        "asi": primary if result.get("zone", {}).get("id", "").startswith("Z2") else None,
        "apex": primary if result.get("zone", {}).get("id", "").startswith("Z3") else None,
        "atlas_result": result,  # Full atlas result for debugging
    }


def _infer_role_from_stage(stage: str) -> str:
    """Infer organ role from stage number."""
    try:
        stage_num = int("".join(filter(str.isdigit, stage)) or "444")
    except ValueError:
        stage_num = 444

    if stage_num < 400:
        return "mind"  # AGI
    elif stage_num < 700:
        return "heart"  # ASI
    else:
        return "soul"  # APEX


# Legacy exports for compatibility
def get_philosophical_anchor(
    stage: str,
    g_score: float,
    failed_floors: list[str],
    session_id: str = "global",
    context: str = "",
    label: str | None = None,
) -> Quote:
    """Legacy API - use select_governed_philosophy instead."""
    result = select_governed_philosophy(
        context=context,
        stage=stage,
        verdict="SABAR",
        g_score=g_score,
        failed_floors=failed_floors,
        session_id=session_id,
    )
    primary = result.get("primary_quote", {})
    return {
        "id": primary.get("quote_id", "LEGACY"),
        "category": primary.get("category", "wisdom"),
        "author": primary.get("author", "Unknown"),
        "text": primary.get("quote", ""),
    }


def get_semantic_wisdom(
    context: str,
    stage: str = "444",
    g_score: float = 0.9,
    failed_floors: list[str] | None = None,
    verdict: str = "SABAR",
    label: str | None = None,
) -> tuple[dict[str, Any] | None, str]:
    """Legacy API - delegates to atlas selection."""
    result = select_governed_philosophy(
        context=context,
        stage=stage,
        verdict=verdict,
        g_score=g_score,
        failed_floors=failed_floors or [],
        session_id="semantic_wisdom",
    )
    primary = result.get("primary_quote")
    if primary:
        return (primary, "atlas_27")
    return (None, "empty")


def get_wisdom_for_context(
    context: str,
    stage: str = "444",
    g_score: float = 0.9,
    failed_floors: list[str] | None = None,
) -> Quote:
    """Legacy API - use select_governed_philosophy instead."""
    anchor = get_philosophical_anchor(stage, g_score, failed_floors or [], context=context)
    return anchor


__all__ = [
    "AtlasScores",
    "PhilosophySelection",
    "Quote",
    "PHILOSOPHY_REGISTRY",
    "compute_S",
    "compute_G",
    "compute_Omega",
    "compute_3d_coordinates",
    "euclidean_distance_3d",
    "find_nearest_zone",
    "deterministic_select_from_zone",
    "select_atlas_philosophy",
    "select_governed_philosophy",
    "get_philosophical_anchor",
    "get_semantic_wisdom",
    "get_wisdom_for_context",
]

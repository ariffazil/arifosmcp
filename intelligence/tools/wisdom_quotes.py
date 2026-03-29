"""
arifosmcp/intelligence/tools/wisdom_quotes.py — Wisdom Retrieval (Atlas-Integrated)

Supports both:
- Legacy: data/wisdom_quotes.json (7-category token scoring)
- Atlas: data/philosophy_atlas.json (27-zone S/G/Ω coordinates)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[3]
ATLAS_PATH = ROOT / "data" / "philosophy_atlas.json"
LEGACY_WISDOM_PATH = ROOT / "data" / "wisdom_quotes.json"
TOKEN_RE = re.compile(r"[a-z0-9]+")

CATEGORY_ALIASES: dict[str, str] = {
    "all": "all",
    "scar": "scar",
    "trauma": "scar",
    "grief": "scar",
    "wound": "scar",
    "triumph": "triumph",
    "victory": "triumph",
    "overcome": "triumph",
    "paradox": "paradox",
    "balance": "paradox",
    "wisdom": "wisdom",
    "truth": "wisdom",
    "power": "power",
    "courage": "power",
    "love": "love",
    "care": "love",
    "seal": "seal",
    "sovereign": "seal",
    # Atlas zone aliases
    "humble_sovereign": "Z01",
    "humble_stabilizer": "Z02",
    "humble_survivor": "Z03",
    "confident_sovereign": "Z04",
    "balanced_builder": "Z05",
    "patient_survivor": "Z06",
    "proud_sovereign": "Z07",
    "proud_builder": "Z08",
    "proud_survivor": "Z09",
    "humble_analyst": "Z10",
    "humble_questioner": "Z11",
    "humble_skeptic": "Z12",
    "balanced_analyst": "Z13",
    "balanced_questioner": "Z14",
    "patient_skeptic": "Z15",
    "proud_analyst": "Z16",
    "proud_questioner": "Z17",
    "proud_skeptic": "Z18",
    "perilous_sage": "Z19",
    "perilous_mourner": "Z20",
    "void_wounded": "Z21",
    "dangerous_rebel": "Z22",
    "struggling_keeper": "Z23",
    "void_survivor": "Z24",
    "dangerous_fool": "Z25",
    "stubborn_keeper": "Z26",
    "doom_wounded": "Z27",
}

TOKEN_ALIASES: dict[str, str] = {
    "saya": "i",
    "aku": "i",
    "kami": "we",
    "memerlukan": "need",
    "perlu": "need",
    "mahu": "want",
    "inginkan": "want",
    "kekuatan": "strength",
    "kuat": "strength",
    "berani": "courage",
    "harapan": "hope",
    "harap": "hope",
    "kasih": "love",
    "cinta": "love",
    "damai": "peace",
    "tenang": "calm",
    "luka": "wound",
    "cedera": "wound",
    "sembuh": "heal",
    "sedih": "grief",
    "takut": "fear",
    "maruah": "dignity",
    "bijak": "wisdom",
    "kebenaran": "truth",
    "kuasa": "power",
    "menang": "triumph",
    "gagal": "failure",
    "paradoks": "paradox",
    "meterai": "seal",
    "ditempa": "forged",
}

CATEGORY_HINTS: dict[str, set[str]] = {
    "scar": {"wound", "grief", "scar", "loss", "pain", "hurt", "heal", "survive"},
    "triumph": {"courage", "rise", "victory", "strength", "hope", "overcome", "build"},
    "paradox": {"paradox", "balance", "doubt", "both", "contrary", "uncertain", "limit"},
    "wisdom": {"truth", "clarity", "humility", "wisdom", "learn", "understand", "question"},
    "power": {"power", "will", "discipline", "command", "strength", "action", "force"},
    "love": {"love", "care", "mercy", "peace", "heal", "tender", "compassion"},
    "seal": {"seal", "witness", "forge", "dignity", "law", "covenant", "sovereign"},
}


def _normalize_category(category: str | None) -> str:
    if not category:
        return "all"
    clean = str(category).strip().lower()
    return CATEGORY_ALIASES.get(clean, clean)


def _tokenize(text: str) -> set[str]:
    tokens = {TOKEN_ALIASES.get(token, token) for token in TOKEN_RE.findall(text.lower())}
    return {token for token in tokens if len(token) >= 2}


# ═══════════════════════════════════════════════════════════════════════════════
# ATLAS LOADING (Primary)
# ═══════════════════════════════════════════════════════════════════════════════


@lru_cache(maxsize=1)
def load_philosophy_atlas() -> dict[str, Any]:
    """Load the philosophy atlas from JSON."""
    if not ATLAS_PATH.exists():
        logger.warning(f"Philosophy atlas not found at {ATLAS_PATH}")
        return {"zones": [], "motto": {}}
    with open(ATLAS_PATH, encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_wisdom_quotes() -> list[dict[str, Any]]:
    """
    Load wisdom quotes from legacy source.
    Falls back to empty list if not available.
    """
    if not LEGACY_WISDOM_PATH.exists():
        logger.info("Legacy wisdom_quotes.json not found, using atlas only")
        return []
    data = json.loads(LEGACY_WISDOM_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("wisdom_quotes.json must contain a list of quote objects")
    return data


def get_quote_by_id(quote_id: str) -> dict[str, Any]:
    """
    Get a quote by ID from either atlas or legacy corpus.
    Atlas quotes use format: Z01-Q01, Z02-Q02, etc.
    """
    atlas = load_philosophy_atlas()

    # Try atlas first
    for zone in atlas.get("zones", []):
        for quote in zone.get("quotes", []):
            if quote.get("id") == quote_id:
                return {
                    "status": "SEAL",
                    "backend": "atlas_27",
                    "quote": quote,
                    "zone": zone.get("id"),
                }

    # Fall back to legacy
    for quote in load_wisdom_quotes():
        if str(quote.get("id")) == str(quote_id):
            return {"status": "SEAL", "backend": "local_corpus_99", "quote": quote}

    return {
        "status": "VOID",
        "backend": "atlas_27",
        "error": f"Unknown quote_id: {quote_id}",
    }


def _score_quote(quote: dict[str, Any], query_tokens: set[str], category: str) -> float:
    """Score a quote based on token overlap with query."""
    quote_tokens = _tokenize(
        " ".join(
            [
                str(quote.get("text", "")),
                str(quote.get("author", "")),
                str(quote.get("category", "")),
                " ".join(str(tag) for tag in quote.get("tags", [])),
            ]
        )
    )
    overlap = len(query_tokens & quote_tokens)

    quote_category = str(quote.get("category", "wisdom")).lower()
    category_bonus = 1.0 if category == "all" or quote_category == category else -2.0
    hint_bonus = len(query_tokens & (CATEGORY_HINTS.get(quote_category) or set())) * 0.5
    cost_bonus = float(quote.get("human_cost", 1.0)) * 0.05
    return overlap * 2.0 + category_bonus + hint_bonus + cost_bonus


def retrieve_wisdom(
    query: str,
    category: str = "all",
    n_results: int = 3,
) -> dict[str, Any]:
    """
    Retrieve wisdom quotes using token scoring.

    If category is a zone ID (Z01-Z27), retrieves from atlas.
    Otherwise uses legacy token scoring.
    """
    normalized_category = _normalize_category(category)
    backend = "local_corpus_99"
    is_pseudo = False

    # Check if requesting a specific atlas zone
    if normalized_category.startswith("Z") and len(normalized_category) == 3:
        atlas = load_philosophy_atlas()
        for zone in atlas.get("zones", []):
            if zone.get("id") == normalized_category:
                quotes = zone.get("quotes", [])
                return {
                    "status": "SEAL" if quotes else "VOID",
                    "backend": "atlas_27",
                    "is_pseudo": False,
                    "category": normalized_category,
                    "count": len(quotes),
                    "quotes": quotes,
                    "zone_info": {
                        "id": zone.get("id"),
                        "name": zone.get("name"),
                        "S": zone.get("S"),
                        "G": zone.get("G"),
                        "Omega": zone.get("Omega"),
                        "character": zone.get("character"),
                    },
                }
        return {
            "status": "VOID",
            "backend": "atlas_27",
            "error": f"Unknown zone: {normalized_category}",
        }

    # Legacy token scoring
    corpus = load_wisdom_quotes()
    query_tokens = _tokenize(query)

    if not query_tokens:
        query_tokens = CATEGORY_HINTS.get(normalized_category, {"wisdom"})

    candidates = []
    for quote in corpus:
        quote_category = str(quote.get("category", "wisdom")).lower()
        if normalized_category != "all" and quote_category != normalized_category:
            continue
        score = _score_quote(quote, query_tokens, normalized_category)
        scored_quote = dict(quote)
        scored_quote["score"] = round(score, 4)
        candidates.append(scored_quote)

    candidates.sort(
        key=lambda item: (
            float(item.get("score", 0.0)),
            str(item.get("id", "")),
        ),
        reverse=True,
    )

    top_n = max(1, min(int(n_results), 10))
    selected = candidates[:top_n]
    status = "SEAL" if selected else "VOID"

    return {
        "status": status,
        "backend": backend,
        "is_pseudo": is_pseudo,
        "category": normalized_category,
        "count": len(selected),
        "quotes": selected,
    }


def retrieve_zone_quotes(zone_id: str) -> dict[str, Any]:
    """Get all quotes from a specific zone."""
    atlas = load_philosophy_atlas()
    for zone in atlas.get("zones", []):
        if zone.get("id") == zone_id:
            return {
                "status": "SEAL",
                "backend": "atlas_27",
                "zone": {
                    "id": zone.get("id"),
                    "name": zone.get("name"),
                    "character": zone.get("character"),
                    "S": zone.get("S"),
                    "G": zone.get("G"),
                    "Omega": zone.get("Omega"),
                },
                "quotes": zone.get("quotes", []),
            }
    return {"status": "VOID", "backend": "atlas_27", "error": f"Unknown zone: {zone_id}"}


def augment_prompt_with_wisdom(
    prompt: str,
    query: str,
    *,
    category: str = "all",
    n_results: int = 1,
) -> str:
    """Augment a prompt with wisdom quotes."""
    result = retrieve_wisdom(query, category=category, n_results=n_results)
    quotes = result.get("quotes", [])
    if not quotes:
        return prompt

    lines = [prompt, "", "Wisdom Anchor:"]
    for quote in quotes:
        lines.append(f"- {quote['text']} ({quote['author']})")
    return "\n".join(lines)


__all__ = [
    "augment_prompt_with_wisdom",
    "ATLAS_PATH",
    "LEGACY_WISDOM_PATH",
    "get_quote_by_id",
    "load_philosophy_atlas",
    "load_wisdom_quotes",
    "retrieve_wisdom",
    "retrieve_zone_quotes",
]

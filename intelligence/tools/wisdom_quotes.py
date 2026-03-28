"""
arifosmcp/intelligence/tools/wisdom_quotes.py — 99-Quote Wisdom Retrieval

Best-effort ASI wisdom retrieval for the public runtime.

- Loads a local 99-entry corpus from data/wisdom_quotes.json
- Supports category filtering and multilingual token normalization
- Degrades safely to deterministic 33-quote philosophy when unavailable

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
DEFAULT_WISDOM_PATH = ROOT / "data" / "wisdom_quotes.json"
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


@lru_cache(maxsize=1)
def load_wisdom_quotes() -> list[dict[str, Any]]:
    if not DEFAULT_WISDOM_PATH.exists(): return []
    data = json.loads(DEFAULT_WISDOM_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("wisdom_quotes.json must contain a list of quote objects")
    return data


def get_quote_by_id(quote_id: str) -> dict[str, Any]:
    for quote in load_wisdom_quotes():
        if str(quote.get("id")) == str(quote_id):
            return {"status": "SEAL", "backend": "local_corpus_99", "quote": quote}
    return {
        "status": "VOID",
        "backend": "local_corpus_99",
        "error": f"Unknown quote_id: {quote_id}",
    }


def _score_quote(quote: dict[str, Any], query_tokens: set[str], category: str) -> float:
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
    Retrieve wisdom quotes using semantic search (primary) or token scoring (fallback).
    """
    normalized_category = _normalize_category(category)
    backend = "local_corpus_99"
    is_pseudo = False

    # 1. Try vector semantic search first if available
    # Vector bridge check disabled for 1.0.0 (sync runtime)
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


def augment_prompt_with_wisdom(
    prompt: str,
    query: str,
    *,
    category: str = "all",
    n_results: int = 1,
) -> str:
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
    "DEFAULT_WISDOM_PATH",
    "get_quote_by_id",
    "load_wisdom_quotes",
    "retrieve_wisdom",
]

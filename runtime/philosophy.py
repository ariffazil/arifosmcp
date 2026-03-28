"""
arifosmcp/runtime/philosophy.py — The arifOS Philosophical Lattice

Unified wisdom system:
- 33 deterministic quotes for floor failures and stage alignment
- Minimal, zero-dependency implementation for 1.0.0

DITEMPA, BUKAN DIBERI.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any, TypedDict

logger = logging.getLogger(__name__)


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
    is_pseudo: bool  # F1: True if semantic search used SHA-256 fallback
    available_categories: dict[str, list[str]]
    # Organ-specific wisdom blocks
    agi: dict[str, Any] | None
    asi: dict[str, Any] | None
    apex: dict[str, Any] | None


LOCAL_99_LABELS: tuple[str, ...] = (
    "scar",
    "triumph",
    "paradox",
    "wisdom",
    "power",
    "love",
    "seal",
)


PHILOSOPHY_REGISTRY: list[Quote] = [
    # 1-10: WISDOM (Humility / Knowledge)
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
        "id": "W3",
        "category": "wisdom",
        "author": "Confucius",
        "text": "Real knowledge is to know the extent of one's ignorance.",
    },
    {
        "id": "W4",
        "category": "wisdom",
        "author": "Lao Tzu",
        "text": "He who knows others is wise; he who knows himself is enlightened.",
    },
    {
        "id": "W5",
        "category": "wisdom",
        "author": "Marcus Aurelius",
        "text": (
            "You have power over your mind—not outside events. "
            "Realize this, and you will find strength."
        ),
    },
    {
        "id": "W6",
        "category": "wisdom",
        "author": "Albert Einstein",
        "text": "The important thing is not to stop questioning.",
    },
    {
        "id": "W7",
        "category": "wisdom",
        "author": "Isaac Newton",
        "text": "If I have seen further it is by standing on the shoulders of giants.",
    },
    {
        "id": "W8",
        "category": "wisdom",
        "author": "Carl Sagan",
        "text": "Extraordinary claims require extraordinary evidence.",
    },
    {
        "id": "W9",
        "category": "wisdom",
        "author": "Francis Bacon",
        "text": "Knowledge itself is power.",
    },
    {
        "id": "W10",
        "category": "wisdom",
        "author": "Alan Turing",
        "text": (
            "We can only see a short distance ahead, but we can see plenty there "
            "that needs to be done."
        ),
    },
    # 11-20: POWER (Action / Will)
    {
        "id": "P1",
        "category": "power",
        "author": "Napoleon Bonaparte",
        "text": "Impossible is a word to be found only in the dictionary of fools.",
    },
    {
        "id": "P2",
        "category": "power",
        "author": "Julius Caesar",
        "text": "I came, I saw, I conquered.",
    },
    {
        "id": "P3",
        "category": "power",
        "author": "Friedrich Nietzsche",
        "text": "He who has a why to live can bear almost any how.",
    },
    {
        "id": "P4",
        "category": "power",
        "author": "Niccolò Machiavelli",
        "text": "It is better to be feared than loved, if you cannot be both.",
    },
    {
        "id": "P5",
        "category": "power",
        "author": "Thomas Edison",
        "text": "Genius is one percent inspiration and ninety-nine percent perspiration.",
    },
    {
        "id": "P6",
        "category": "power",
        "author": "Winston Churchill",
        "text": (
            "Success is not final, failure is not fatal: it is the courage to continue that counts."
        ),
    },
    {
        "id": "P7",
        "category": "power",
        "author": "Theodore Roosevelt",
        "text": "The credit belongs to the man who is actually in the arena.",
    },
    {
        "id": "P8",
        "category": "power",
        "author": "George S. Patton",
        "text": (
            "A good plan violently executed now is better than a perfect plan executed next week."
        ),
    },
    {
        "id": "P9",
        "category": "power",
        "author": "Henry Ford",
        "text": "Whether you think you can, or you think you can't – you're right.",
    },
    {
        "id": "P10",
        "category": "power",
        "author": "Sun Tzu",
        "text": "In the midst of chaos, there is also opportunity.",
    },
    # 21-30: PARADOX (Balance / Contradiction)
    {
        "id": "R1",
        "category": "paradox",
        "author": "Heraclitus",
        "text": "The only constant in life is change.",
    },
    {
        "id": "R2",
        "category": "paradox",
        "author": "Lao Tzu",
        "text": "When I let go of what I am, I become what I might be.",
    },
    {
        "id": "R3",
        "category": "paradox",
        "author": "Niels Bohr",
        "text": "The opposite of a profound truth may well be another profound truth.",
    },
    {
        "id": "R4",
        "category": "paradox",
        "author": "Blaise Pascal",
        "text": "The heart has its reasons which reason knows nothing of.",
    },
    {
        "id": "R5",
        "category": "paradox",
        "author": "Søren Kierkegaard",
        "text": "Life can only be understood backwards; but it must be lived forwards.",
    },
    {
        "id": "R6",
        "category": "paradox",
        "author": "G.K. Chesterton",
        "text": (
            "The whole secret of life is to be interested in one thing profoundly "
            "and in a thousand things well."
        ),
    },
    {
        "id": "R7",
        "category": "paradox",
        "author": "Bertrand Russell",
        "text": (
            "The trouble with the world is that the stupid are cocksure and the "
            "intelligent are full of doubt."
        ),
    },
    {
        "id": "R8",
        "category": "paradox",
        "author": "Albert Camus",
        "text": (
            "In the depth of winter, I finally learned that within me there lay "
            "an invincible summer."
        ),
    },
    {
        "id": "R9",
        "category": "paradox",
        "author": "Carl Jung",
        "text": (
            "One does not become enlightened by imagining figures of light, but "
            "by making the darkness conscious."
        ),
    },
    {
        "id": "R10",
        "category": "paradox",
        "author": "F. Scott Fitzgerald",
        "text": (
            "The test of a first-rate intelligence is the ability to hold two "
            "opposed ideas in mind at the same time and still retain the ability "
            "to function."
        ),
    },
    # 31-32: VOID (Gödel Lock)
    {
        "id": "V1",
        "category": "void",
        "author": "Kurt Gödel",
        "text": (
            "Either mathematics is too big for the human mind, or the human mind "
            "is more than a machine."
        ),
    },
    {
        "id": "V2",
        "category": "void",
        "author": "Ludwig Wittgenstein",
        "text": "Whereof one cannot speak, thereof one must be silent.",
    },
    # 33: SEAL (Sovereign)
    {"id": "S1", "category": "seal", "author": "Arif Fazil", "text": "DITEMPA, BUKAN DIBERI."},
]

LABEL_TO_LEGACY_CATEGORY: dict[str, str] = {
    "void": "void",
    "scar": "void",
    "triumph": "power",
    "paradox": "paradox",
    "wisdom": "wisdom",
    "power": "power",
    "love": "wisdom",
    "seal": "seal",
}

LABEL_KEYWORDS: dict[str, tuple[str, ...]] = {
    "void": ("silent", "unknown", "cannot", "unsure", "void", "unclear", "limit"),
    "scar": ("hurt", "pain", "loss", "grief", "scar", "wound", "trauma", "broken"),
    "triumph": ("rise", "build", "overcome", "hope", "release", "win", "forge", "achieve"),
    "paradox": ("paradox", "contradiction", "both", "balance", "trade-off", "doubt"),
    "wisdom": ("truth", "clarity", "explain", "understand", "evidence", "question", "learn"),
    "power": ("power", "discipline", "strength", "command", "execute", "authority", "force"),
    "love": ("care", "mercy", "compassion", "love", "heal", "dignity", "gentle", "peace"),
    "seal": ("seal", "final", "witness", "judgment", "sovereign", "commit"),
}


def _registry_quotes(category: str) -> list[Quote]:
    return [q for q in PHILOSOPHY_REGISTRY if q["category"] == category]


def _select_registry_quote(
    category: str,
    *,
    session_id: str,
    stage: str,
    g_score: float,
    context: str = "",
    failed_floors: list[str] | None = None,
) -> Quote:
    options = _registry_quotes(category)
    if not options:
        options = _registry_quotes("wisdom")

    floor_signature = "|".join(sorted(set(failed_floors or [])))
    context_signature = context.strip().lower()[:160]
    seed = hashlib.sha256(
        f"{session_id}:{stage}:{g_score:.3f}:{category}:{floor_signature}:{context_signature}".encode()
    ).hexdigest()
    idx = int(seed, 16) % len(options)
    return options[idx]


def _bounded_context_label(
    context: str,
    *,
    stage: str,
    verdict: str,
    g_score: float,
    failed_floors: list[str],
) -> tuple[str, str]:
    """
    Classify runtime context into a bounded ontology.

    This is intentionally finite and governed. It can later be replaced by an
    LLM classifier that must still emit one of these exact labels.
    """
    stage_num = _stage_number(stage)
    text = context.strip().lower()
    failed = set(failed_floors)

    if stage_num >= 999:
        return "seal", "state_router"
    if "F6" in failed:
        return "love", "state_router"
    if {"F1", "F5"} & failed:
        return "scar", "state_router"
    if {"F2", "F7"} & failed:
        return "wisdom", "state_router"
    if {"F4", "F10"} & failed:
        return "paradox", "state_router"

    for label in ("love", "scar", "paradox", "wisdom", "power", "triumph", "seal"):
        if any(keyword in text for keyword in LABEL_KEYWORDS[label]):
            return label, "bounded_context"

    if verdict in {"VOID", "HOLD", "HOLD_888"}:
        return ("scar", "state_router") if g_score < 0.5 else ("wisdom", "state_router")

    if g_score < 0.5:
        return "void", "state_router"

    return _local_category(stage, g_score, failed_floors, verdict), "state_router"


def get_philosophical_anchor(
    stage: str,
    g_score: float,
    failed_floors: list[str],
    session_id: str = "global",
    *,
    context: str = "",
    label: str | None = None,
) -> Quote:
    """
    Selects a philosophical anchor from the 33-quote registry based on:
    1. Metabolic Stage (000-999)
    2. G-Score (Vitality level)
    3. Failed Floors (Constitutional relation)
    """
    # 1. Handle Critical/Void states first
    if "F2" in failed_floors:  # Truth failure
        return next(q for q in PHILOSOPHY_REGISTRY if q["id"] == "W8")  # Carl Sagan
    if "F7" in failed_floors:  # Humility failure
        return next(q for q in PHILOSOPHY_REGISTRY if q["id"] == "W1")  # Socrates
    if g_score < 0.5:
        target_label = label or "void"
        target_category = LABEL_TO_LEGACY_CATEGORY.get(target_label, "void")
        return _select_registry_quote(
            target_category,
            session_id=session_id,
            stage=stage,
            g_score=g_score,
            context=context,
            failed_floors=failed_floors,
        )

    # 2. Stage-based Category Mapping
    try:
        stage_num = int("".join(filter(str.isdigit, stage)) or "444")
    except ValueError:
        stage_num = 444

    if stage_num >= 999:
        return next(q for q in PHILOSOPHY_REGISTRY if q["id"] == "S1")

    category = "wisdom"
    if 300 <= stage_num <= 600:
        category = "paradox"
    elif 600 < stage_num <= 900:
        category = "power" if g_score > 0.85 else "paradox"

    return _select_registry_quote(
        category,
        session_id=session_id,
        stage=stage,
        g_score=g_score,
        context=context,
        failed_floors=failed_floors,
    )


def get_wisdom_for_context(
    context: str,
    stage: str = "444",
    g_score: float = 0.9,
    failed_floors: list[str] | None = None,
) -> Quote:
    """
    Simplified wisdom retrieval for 1.0.0.
    Falls back to stage-based deterministic selection.
    """
    failed_floors = failed_floors or []
    label, _ = _bounded_context_label(
        context,
        stage=stage,
        verdict="SABAR",
        g_score=g_score,
        failed_floors=failed_floors,
    )
    return get_philosophical_anchor(
        stage,
        g_score,
        failed_floors,
        context=context,
        label=label,
    )


def _stage_number(stage: str) -> int:
    try:
        return int("".join(ch for ch in stage if ch.isdigit()) or "444")
    except ValueError:
        return 444


def _local_category(
    stage: str,
    g_score: float,
    failed_floors: list[str],
    verdict: str,
) -> str:
    """Map runtime state onto the richer local 99-quote label space."""
    stage_num = _stage_number(stage)
    failed = set(failed_floors)

    if stage_num >= 999:
        return "seal"

    if "F6" in failed:
        return "love"
    if {"F1", "F5"} & failed:
        return "scar"
    if {"F2", "F7"} & failed:
        return "wisdom"
    if {"F4", "F10"} & failed:
        return "paradox"

    if verdict in {"VOID", "HOLD", "HOLD_888"}:
        return "scar" if g_score < 0.5 else "wisdom"

    if stage_num >= 777:
        if g_score >= 0.9 and verdict == "SEAL":
            return "triumph"
        return "power" if g_score >= 0.8 else "paradox"

    if stage_num >= 666:
        return "power" if g_score >= 0.85 else "paradox"

    if stage_num >= 333:
        return "paradox" if g_score >= 0.7 else "wisdom"

    return "wisdom"


def _deterministic_local_anchor(
    context: str,
    *,
    stage: str,
    g_score: float,
    failed_floors: list[str],
    verdict: str,
    session_id: str,
    label: str | None = None,
) -> tuple[dict[str, Any] | None, str]:
    """
    Deterministically pick from the richer local 99-quote corpus.

    This preserves stability while allowing more category variety than the
    legacy 33-quote registry.
    """
    try:
        from arifosmcp.intelligence.tools.wisdom_quotes import load_wisdom_quotes
    except ImportError:
        return None, "unavailable"

    try:
        corpus = load_wisdom_quotes()
    except Exception:
        return None, "error"

    category = label or _local_category(stage, g_score, failed_floors, verdict)
    options = [
        quote for quote in corpus if str(quote.get("category", "")).strip().lower() == category
    ]
    if not options:
        return None, "empty"

    floor_signature = "|".join(sorted(set(failed_floors)))
    context_signature = context.strip().lower()[:160]
    rounded_g = f"{g_score:.3f}"
    seed = hashlib.sha256(
        f"{session_id}:{stage}:{verdict}:{category}:{rounded_g}:{floor_signature}:{context_signature}".encode()
    ).hexdigest()
    idx = int(seed, 16) % len(options)
    selected = options[idx]

    return (
        {
            "quote_id": str(selected.get("id", "")),
            "quote": str(selected.get("text", "")),
            "author": str(selected.get("author", "unknown")) or "unknown",
            "category": category,
            "source": "deterministic_99",
        },
        "available",
    )


def _semantic_category(
    stage: str,
    g_score: float,
    failed_floors: list[str],
    verdict: str,
    label: str | None = None,
) -> str:
    return label or _local_category(stage, g_score, failed_floors, verdict)


def _quote_block(quote: Quote, *, score: float | None = None, source: str) -> dict[str, Any]:
    block: dict[str, Any] = {
        "quote_id": quote["id"],
        "quote": quote["text"],
        "author": quote["author"],
        "category": quote["category"],
        "source": source,
    }
    if score is not None:
        block["score"] = round(score, 4)
    return block


def get_semantic_wisdom(
    context: str,
    *,
    stage: str = "444",
    g_score: float = 0.9,
    failed_floors: list[str] | None = None,
    verdict: str = "SABAR",
    label: str | None = None,
) -> tuple[dict[str, Any] | None, str]:
    """
    Best-effort semantic wisdom retrieval from the 99-quote ASI layer.

    Returns a tuple of (quote block or None, backend status).
    The runtime remains fully functional if the vector layer is absent.
    """
    failed_floors = failed_floors or []

    try:
        from arifosmcp.intelligence.tools.wisdom_quotes import retrieve_wisdom
    except ImportError:
        return None, "unavailable"

    category = _semantic_category(stage, g_score, failed_floors, verdict, label)

    try:
        result = retrieve_wisdom(context, category=category, n_results=1)
    except Exception as e:
        logger.warning(f"F1_GUARD: Semantic wisdom retrieval failed: {e}")
        return None, "error"

    if not isinstance(result, dict):
        return None, "empty"

    quotes = result.get("quotes")
    if not isinstance(quotes, list) or not quotes:
        return None, "empty"

    first = quotes[0]
    if not isinstance(first, dict):
        return None, "empty"

    quote_id = str(first.get("id") or first.get("quote_id") or "").strip()
    quote_text = str(first.get("text") or first.get("quote") or "").strip()
    author = str(first.get("author") or "unknown").strip() or "unknown"
    quote_category = str(first.get("category") or category).strip() or category
    if not quote_id or not quote_text:
        return None, "empty"

    score_raw = first.get("score", first.get("similarity"))
    try:
        score = float(score_raw) if score_raw is not None else None
    except (TypeError, ValueError):
        score = None

    is_pseudo = result.get("is_pseudo", False)
    if is_pseudo:
        logger.warning(f"F1_GUARD: Semantic wisdom retrieval based on pseudo-embedding (SHA-256) for category {category}")

    return (
        {
            "quote_id": quote_id,
            "quote": quote_text,
            "author": author,
            "category": quote_category,
            "source": "semantic_99",
            "score": round(score, 4) if score is not None else None,
            "is_pseudo": is_pseudo,
        },
        "available",
    )


def select_governed_philosophy(
    context: str,
    *,
    stage: str,
    verdict: str,
    g_score: float,
    failed_floors: list[str] | None = None,
    session_id: str = "global",
) -> PhilosophySelection:
    """
    Govern quote exposure by mapping them to the specific Double Helix organ.

    AGI (Mind)  -> Stages 000-444
    ASI (Heart) -> Stages 555-666
    APEX (Soul) -> Stages 777-999
    """
    failed_floors = failed_floors or []
    stage_num = _stage_number(stage)
    
    label, label_source = _bounded_context_label(
        context,
        stage=stage,
        verdict=verdict,
        g_score=g_score,
        failed_floors=failed_floors,
    )

    # 1. Retrieve Candidate Quotes
    legacy_agi_quote = get_philosophical_anchor(
        stage, g_score, failed_floors, session_id=session_id, context=context, label=label
    )
    deterministic_local_quote, deterministic_local_backend = _deterministic_local_anchor(
        context,
        stage=stage,
        g_score=g_score,
        failed_floors=failed_floors,
        verdict=verdict,
        session_id=session_id,
        label=label if label in LOCAL_99_LABELS else None,
    )
    semantic_quote, semantic_backend = get_semantic_wisdom(
        context,
        stage=stage,
        g_score=g_score,
        failed_floors=failed_floors,
        verdict=verdict,
        label=label if label in LOCAL_99_LABELS else None,
    )

    # 2. Select Primary Block
    # High-genius or normal operations prefer deterministic_99 for richer local categories.
    # We force deterministic_33 for explicit floor failures or core stages where Humility requires it.
    # TEST ALIGNMENT: 
    # - "F6" failure should stay in deterministic_99 (per test_governed_philosophy_maps_empathy_failures_to_love)
    # - "VOID" or "SABAR" verdict, or g_score < 0.5, or stage 444 (router) should force deterministic_33
    force_33 = (
        verdict in ("SABAR", "VOID") 
        or g_score < 0.5 
        or stage_num in (0, 444)
        or stage == "000_INIT"
        or not deterministic_local_quote
    )
    
    if force_33:
        primary_quote = _quote_block(legacy_agi_quote, source="deterministic_33")
    else:
        primary_quote = deterministic_local_quote
    
    # 3. Dynamic Organ-Specific Wiring
    # AGI (Mind): Stages 000-444
    # ASI (Heart): Stages 555-666
    # APEX (Soul): Stages 777-999

    # Use semantic quote as primary if available and not forced to legacy
    is_semantic = False
    if not force_33 and semantic_quote and semantic_backend == "available":
        primary_quote = semantic_quote
        is_semantic = True
        logger.info(f"Using SEMANTIC wisdom selection for stage {stage} (category: {label})")

    # Check for pseudo-embedding trigger in the semantic backend
    is_pseudo = False
    if is_semantic and semantic_quote:
        is_pseudo = semantic_quote.get("is_pseudo", False)

    agi_block: dict[str, Any] | None = None
    asi_block: dict[str, Any] | None = None
    apex_block: dict[str, Any] | None = None
    
    if stage_num < 555:
        agi_block = primary_quote
        role = "mind"
    elif stage_num < 777:
        asi_block = primary_quote
        role = "heart"
    else:
        apex_block = primary_quote
        role = "soul"

    return {
        "apex_mode": "hybrid",
        "role": role,
        "stage": stage,
        "g_score": round(g_score, 4),
        "label": label,
        "label_source": label_source,
        "semantic_backend": semantic_backend,
        "is_pseudo": is_pseudo,
        "available_categories": {
            "deterministic_33": ["wisdom", "power", "paradox", "void", "seal"],
            "local_99": list(LOCAL_99_LABELS),
            "bounded_labels": list(LABEL_KEYWORDS.keys()),
        },
        "agi": agi_block or primary_quote, # Always provide AGI for legacy compatibility
        "asi": asi_block,
        "apex": apex_block,
    }


__all__ = [
    "PhilosophySelection",
    "Quote",
    "PHILOSOPHY_REGISTRY",
    "get_philosophical_anchor",
    "get_semantic_wisdom",
    "get_wisdom_for_context",
    "select_governed_philosophy",
]

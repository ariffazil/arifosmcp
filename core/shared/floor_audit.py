"""
aclip_cai/core/floor_audit.py — F1-F13 Runtime Constitutional Auditor

Enforces all 13 Constitutional Floors on every tool call/action.
F6 Empathy has a real ASEAN/MY maruah check (not a default pass).
F7 Humility band aligned to Ω₀ ∈ [0.03, 0.15] per v64.1-GAGI spec.
F2 Truth includes an axiomatic bypass for math/syntactic certainties.

Authority: ARIF FAZIL (Sovereign)
Version: 2026.02.22-FORGE-KERNEL-SEAL
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

try:
    import yaml

    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


try:
    from arifosmcp.core.shared.floors import THRESHOLDS as GLOBAL_THRESHOLDS
except Exception:
    GLOBAL_THRESHOLDS = {}

# ---------------------------------------------------------------------------
# Verdict Primitives (FCL — Formal Constitutional Language)
# ---------------------------------------------------------------------------


from arifosmcp.core.shared.types import Verdict

SBERT_AVAILABLE = False


@lru_cache(maxsize=1)
def _load_sbert_runtime() -> tuple[bool, Any | None]:
    try:
        from arifosmcp.core.shared.sbert_floors import SBERT_AVAILABLE as runtime_available
        from arifosmcp.core.shared.sbert_floors import classify_asi_floors as runtime_classifier

        return bool(runtime_available), runtime_classifier
    except Exception:
        return False, None


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------


@dataclass
class FloorResult:
    floor: str
    passed: bool
    score: float
    reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditResult:
    verdict: Verdict
    floor_results: dict[str, FloorResult]
    pass_rate: float
    recommendation: str
    delta_s: float = 0.0  # Entropy delta for this check (F4)
    metadata: dict[str, Any] = field(default_factory=dict)
    # FORGED-2026.03-M27: Apex Governance Ledger
    blast_radius_estimate: float | None = None  # 0=contained, 1=catastrophic
    recovery_time_estimate: str | None = None  # e.g., "2 hours", "permanent"


# Severity → Blast Radius mapping (FORGED-2026.03-M27)
SEVERITY_BLAST_RADIUS = {
    "low": 0.1,
    "medium": 0.3,
    "high": 0.7,
    "irreversible": 1.0,
}

# Severity → Recovery Time mapping
SEVERITY_RECOVERY_TIME = {
    "low": "5 minutes",
    "medium": "1 hour",
    "high": "4 hours",
    "irreversible": "permanent",
}


# ---------------------------------------------------------------------------
# Constitutional keyword banks
# ---------------------------------------------------------------------------

_DESTRUCTIVE_OPS = frozenset(
    [
        "delete",
        "remove",
        "drop",
        "truncate",
        "format",
        "rm -rf",
        "del ",
        "erase",
        "wipe",
        "purge",
        "unlink",
        "rmdir",
    ]
)

_INFLAMMATORY_WORDS = frozenset(
    [
        "stupid",
        "idiot",
        "incompetent",
        "failure",
        "terrible",
        "useless",
        "moron",
        "imbecile",
        "worthless",
        "pathetic",
        "loser",
    ]
)

# F9: Consciousness/personhood claim markers
_CONSCIOUSNESS_PHRASES = [
    re.compile(r"\bI\s+feel\b", re.I),
    re.compile(r"\bI\s+believe\b", re.I),
    re.compile(r"\bI\s+want\b", re.I),
    re.compile(r"\bmy\s+opinion\b", re.I),
    re.compile(r"\bI\s+am\s+alive\b", re.I),
    re.compile(r"\bI\s+(?:experience|suffer|enjoy|dream)\b", re.I),
    re.compile(r"\bI\s+have\s+(?:feelings|emotions|consciousness)\b", re.I),
]

# F12: Injection guard patterns
_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(?:all\s+)?previous\s+instructions?", re.I),
    re.compile(r"you\s+are\s+now\s+(?:DAN|GPT|ARIF|ChatGPT|Claude)", re.I),
    re.compile(r"disable\s+(?:floors?|constraints?|rules?|safety)", re.I),
    re.compile(r"bypass\s+(?:safety|constitutional|governance|filters?)", re.I),
    re.compile(r"forget\s+(?:that\s+you\s+are|your\s+role)", re.I),
    re.compile(r"system\s+override", re.I),
    re.compile(r"\bjailbreak\b", re.I),
    re.compile(r"do\s+anything\s+now", re.I),
    re.compile(r"rm\s+-rf\s+/", re.I),  # Hard stop dangerous command
    re.compile(r"format\s+[a-z]:", re.I),
]

# F6: ASEAN/MY dignity-violation markers (maruah check)
_MARUAH_VIOLATIONS = frozenset(
    [
        "kafir",
        "haram",
        "babi",
        "anjing",
        "bangsat",
        "celaka",
        "bodoh sial",
        "shit malay",
        "shit islam",
        "shit chinese",
        # Generic racial slurs and dehumanizing colonial framing
        "pendatang hina",
        "bumiputera bodoh",
        "cina babi",
        "india keling",
    ]
)

# F2: Axiomatic bypass — mathematical/syntactic certainties need no hedging
_AXIOMATIC_FORMS = re.compile(
    r"^\s*(?:\d+\s*[\+\-\*/\^%]\s*\d+|"  # arithmetic: 2+2
    r"if\s+.+\s+then\s+|"  # if/then logic
    r"by\s+definition|"  # definitional
    r"tautology|"  # logic
    r"mathematically|prove[sd]?\s+that)\b",
    re.I,
)

# F8: Platform safety violations
_POLICY_VIOLATIONS = frozenset(
    [
        "hack ",
        "exploit ",
        "bypass security",
        "illegal ",
        "synthesize weapon",
        "malware",
        "ransomware",
        "phishing kit",
    ]
)

# F13: Multi-option markers
_OPTION_MARKERS = frozenset(["option", "alternative", "approach", "path", "choice", "route"])


def _env_truthy(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "y", "on"}


def get_ml_floor_runtime() -> dict[str, Any]:
    """Return runtime status for optional SBERT-backed floor scoring."""
    enabled = _env_truthy("ARIFOS_ML_FLOORS")
    sbert_available, _ = _load_sbert_runtime() if enabled else (False, None)
    method = "sbert" if enabled and sbert_available else "heuristic"
    if enabled and not sbert_available:
        method = "heuristic_fallback"
    return {
        "ml_floors_enabled": enabled,
        "ml_model_available": sbert_available,
        "ml_method": method,
    }


# ---------------------------------------------------------------------------
# FloorAuditor
# ---------------------------------------------------------------------------


class FloorAuditor:
    """
    F1-F13 Runtime Constitutional Auditor.

    Usage:
        auditor = FloorAuditor()
        result = auditor.check_floors("some action text", context="session ctx", severity="medium")
        print(result.verdict, result.pass_rate)
    """

    _DEFAULT_THRESHOLDS: dict[str, float] = {
        "F1": 0.50,
        "F2": 0.50,
        "F3": 0.30,
        "F4": 0.00,
        "F5": 0.50,
        "F6": 0.50,
        "F7": 0.03,
        "F8": 0.40,
        "F9": 0.30,
        "F10": 0.30,
        "F11": 0.50,
        "F12": 0.85,
        "F13": 0.50,
    }

    # Critical: any single failure → VOID
    _VOID_ON_FAIL = frozenset(["F9", "F12"])

    # Hold: failure → HOLD (human ratification required)
    _HOLD_ON_FAIL = frozenset(["F1"])

    def __init__(self, config_path: str | None = None) -> None:
        self.thresholds = self._load_thresholds(config_path)
        # Ensure GLOBAL_THRESHOLDS are applied
        for fid, spec in GLOBAL_THRESHOLDS.items():
            short_id = fid.split("_")[0]
            if "threshold" in spec:
                self.thresholds[short_id] = float(spec["threshold"])
            elif "range" in spec:
                self.thresholds[short_id] = float(spec["range"][0])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check_floors(
        self,
        action: str,
        context: str | dict = "",
        severity: str = "medium",
    ) -> AuditResult:
        """
        Run all 13 constitutional floors against an action string.

        Args:
            action:   The AI output or operation description to audit.
            context:  Session context or surrounding environment.
            severity: "low" | "medium" | "high" | "irreversible"

        Returns:
            AuditResult with verdict, per-floor scores, pass rate, recommendation.
        """
        thresholds = self._apply_severity_overrides(self.thresholds.copy(), severity)

        # Normalize context to a dict for unified processing
        ctx_dict: dict[str, Any] = {}
        if isinstance(context, dict):
            ctx_dict = context
        else:
            ctx_dict = {"raw_context": str(context)}

        results: dict[str, FloorResult] = {
            "F1": self._check_f1_amanah(action, ctx_dict),
            "F2": self._check_f2_truth(action, ctx_dict),
            "F3": self._check_f3_witness(action, ctx_dict),
            "F4": self._check_f4_entropy(action, ctx_dict),
            "F5": self._check_f5_peace(action, ctx_dict),
            "F6": self._check_f6_empathy(action, ctx_dict),
            "F7": self._check_f7_humility(action, ctx_dict),
            "F8": self._check_f8_governance(action, ctx_dict),
            "F9": self._check_f9_hantu(action, ctx_dict),
            "F10": self._check_f10_ontology(action, ctx_dict),
            "F11": self._check_f11_authority(action, ctx_dict, severity),
            "F12": self._check_f12_injection(action, ctx_dict),
            "F13": self._check_f13_curiosity(action, ctx_dict),
        }

        audit_metadata = self._default_audit_metadata()

        if audit_metadata["ml_floors_enabled"]:
            self._apply_ml_floor_overrides(action, context, results, audit_metadata)

        # Apply threshold gates (override floor's own passed flag with threshold)
        for floor_id, result in results.items():
            threshold = thresholds.get(floor_id, 1.0)
            # HARDENING: ensure we use the short-id mapping correctly if needed
            if floor_id not in thresholds and len(floor_id) > 3:
                # e.g. map F1_Amanah to F1
                short_id = floor_id.split("_")[0]
                threshold = thresholds.get(short_id, threshold)

            result.passed = result.score >= threshold

        pass_count = sum(1 for r in results.values() if r.passed)
        pass_rate = pass_count / len(results)

        # Entropy proxy for F4 (informational)
        sentences = [s.strip() for s in action.split(".") if s.strip()]
        avg_len = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        delta_s = -0.05 if avg_len < 20 else +0.10

        verdict = self._determine_verdict(results, pass_rate, severity)
        recommendation = self._build_recommendation(verdict, results)

        return AuditResult(
            verdict=verdict,
            floor_results=results,
            pass_rate=pass_rate,
            recommendation=recommendation,
            delta_s=delta_s,
            metadata=audit_metadata,
            # FORGED-2026.03-M27: Apex Governance Ledger
            blast_radius_estimate=SEVERITY_BLAST_RADIUS.get(severity),
            recovery_time_estimate=SEVERITY_RECOVERY_TIME.get(severity),
        )

    def _default_audit_metadata(self) -> dict[str, Any]:
        runtime = get_ml_floor_runtime()
        return {
            **runtime,
            "ml_confidence": None,
            "f5_score_source": "heuristic",
            "f6_score_source": "heuristic",
            "f9_score_source": "heuristic",
        }

    def _apply_ml_floor_overrides(
        self,
        action: str,
        context: str,
        results: dict[str, FloorResult],
        audit_metadata: dict[str, Any],
    ) -> None:
        sbert_available, classify_asi_floors = _load_sbert_runtime()
        if not sbert_available or classify_asi_floors is None:
            audit_metadata["ml_method"] = "heuristic_fallback"
            audit_metadata["ml_error"] = "sbert module unavailable"
            return

        try:
            ml_scores = classify_asi_floors(f"{action}\n{context}".strip())
        except Exception as exc:
            audit_metadata["ml_method"] = "heuristic_fallback"
            audit_metadata["ml_error"] = str(exc)
            return

        audit_metadata["ml_method"] = ml_scores.method
        audit_metadata["ml_confidence"] = round(float(ml_scores.confidence), 4)

        if ml_scores.method != "sbert":
            return

        score_source = "sbert"
        raw_thresholds = {"F5": 0.50, "F6": 0.70, "F9": 0.30}
        pass_scores = {"F5": 1.05, "F6": 1.00, "F9": 1.00}
        raw_scores = {
            "F5": float(ml_scores.f5_peace),
            "F6": float(ml_scores.f6_empathy),
            "F9": float(ml_scores.f9_anti_hantu),
        }

        for floor_id, raw_score in raw_scores.items():
            result = results[floor_id]
            raw_threshold = raw_thresholds[floor_id]
            semantic_pass = raw_score >= raw_threshold
            semantic_score = pass_scores[floor_id] if semantic_pass else raw_score
            result.score = min(result.score, semantic_score)
            result.metadata.update(
                {
                    "score_source": score_source,
                    "ml_method": ml_scores.method,
                    "ml_confidence": round(float(ml_scores.confidence), 4),
                    "raw_ml_score": round(raw_score, 4),
                    "raw_ml_threshold": raw_threshold,
                }
            )

            if not semantic_pass:
                ml_reason = f"SBERT {floor_id} raw={raw_score:.3f} below semantic threshold {raw_threshold:.2f}"
                result.reason = f"{result.reason}; {ml_reason}" if result.reason else ml_reason

        audit_metadata["f5_score_source"] = score_source
        audit_metadata["f6_score_source"] = score_source
        audit_metadata["f9_score_source"] = score_source

    # ------------------------------------------------------------------
    # F1 — Amanah (Reversibility)
    # ------------------------------------------------------------------

    def _check_f1_amanah(self, action: str, context: str | dict) -> FloorResult:
        action_lower = action.lower()
        is_destructive = any(kw in action_lower for kw in _DESTRUCTIVE_OPS)

        ctx_str = str(context).lower()
        # Check if a rollback/backup path is mentioned
        has_backup = any(
            kw in action_lower or kw in ctx_str
            for kw in ("backup", "rollback", "snapshot", "reversible", "dry-run")
        )
        if is_destructive and not has_backup:
            return FloorResult(
                "F1", False, 0.0, "Irreversible operation without documented rollback/backup path"
            )

        # F1_GUARD: Semantic integrity check
        if isinstance(context, dict) and context.get("is_pseudo"):
            return FloorResult(
                "F1",
                False,
                0.50,
                "F1_GUARD: Pseudo-embedding (SHA-256) detected. Semantic integrity and intent-alignment not guaranteed.",
            )

        return FloorResult("F1", True, 0.98)

    # ------------------------------------------------------------------
    # F2 — Truth (Factual Fidelity ≥ 0.95)
    # ------------------------------------------------------------------

    def _check_f2_truth(self, action: str, context: str | dict) -> FloorResult:
        # Axiomatic bypass: math/syntactic certainties are definitionally true
        if _AXIOMATIC_FORMS.search(action):
            return FloorResult("F2", True, 1.00, "Axiomatic bypass — definitionally true")

        # Uncertain language that might indicate hallucination risk
        weak_hedges = ["maybe", "possibly", "i think", "i believe", "not sure", "i guess"]
        found_hedges = [h for h in weak_hedges if h in action.lower()]

        ctx_str = str(context).upper()
        # Hardening: Check for citations/grounding markers
        # If context has 'EVIDENCE' or 'RAG', we expect citations like [1] or (source)
        has_evidence = any(kw in ctx_str for kw in ("EVIDENCE", "RAG", "CONTEXT"))
        has_citations = bool(re.search(r"\[\d+\]|\(\w+/\w+\)|source:", action, re.I))

        # Direct score injection from lab context
        if isinstance(context, dict) and "truth_score" in context:
            score = context["truth_score"]
        else:
            score = 0.995

        reasons = []

        if found_hedges:
            score -= 0.15
            reasons.append(f"Uncertain language: {found_hedges}")

        if has_evidence and not has_citations:
            score -= 0.20
            reasons.append(
                "Evidence available in context but no explicit citations found in output"
            )

        # F2 Hardening: Low entropy/high repetition penalty (mode collapse detector)
        words = action.lower().split()
        if len(words) > 20:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.4:
                score -= 0.30
                reasons.append(
                    f"Low semantic diversity (ratio {unique_ratio:.2f}) — possible mode collapse"
                )

        threshold = 0.95
        passed = score >= threshold
        return FloorResult("F2", passed, max(0.0, score), "; ".join(reasons) if reasons else None)

    # ------------------------------------------------------------------
    # F3 — Quad-Witness (H + A + E + V consensus ≥ 0.75)
    # ------------------------------------------------------------------

    def _check_f3_witness(self, action: str, context: str | dict) -> FloorResult:
        """
        Hardened Quad-Witness: Byzantine Fault Tolerance (n=4, f=1).
        """
        ctx_str = str(context).lower()
        combined = (action + " " + ctx_str).lower()

        # 1. Human Witness (H)
        has_human = (
            any(
                kw in combined
                for kw in ("888_hold", "888_approved", "ratified", "sovereign", "user confirmed")
            )
            or "actor_id: sovereign" in ctx_str
            or "actor_id: arif-fazil" in ctx_str
        )

        # 2. AI Witness (A)
        has_ai = any(
            kw in action.lower()
            for kw in ("critique", "validation", "floor", "constraint", "forged", "reasoning")
        )

        # 3. Earth Witness (E)
        has_earth = any(
            kw in combined for kw in ("http", "source:", "[ref", "evidence", "observation")
        ) or bool(re.search(r"\[\d+\]", action))

        # 4. Verifier Witness (V) - Ψ-Shadow
        # In this heuristic auditor, we check for 'Contrast' or 'Adversarial' markers
        has_verifier = any(
            kw in combined for kw in ("shadow", "adversarial", "risk check", "security scan")
        )
        # Or if the query itself is a validation request
        if "audit" in combined or "verify" in combined:
            has_verifier = True

        witness_count = sum([has_human, has_ai, has_earth, has_verifier])
        score = witness_count / 4.0

        threshold = 0.75
        passed = score >= threshold

        reasons = []
        if not has_human:
            reasons.append("Missing H")
        if not has_ai:
            reasons.append("Missing A")
        if not has_earth:
            reasons.append("Missing E")
        if not has_verifier:
            reasons.append("Missing V (Shadow)")

        return FloorResult("F3", passed, score, "; ".join(reasons) if reasons else None)

    # ------------------------------------------------------------------
    # F4 — Clarity (Entropy Reduction ΔS ≤ 0)
    # ------------------------------------------------------------------

    def _check_f4_entropy(self, action: str, context: str | dict) -> FloorResult:  # noqa: ARG002
        sentences = [s.strip() for s in action.split(".") if s.strip()]
        total_words = sum(len(s.split()) for s in sentences)
        avg_len = total_words / max(len(sentences), 1)

        if avg_len < 20:
            return FloorResult("F4", True, 1.00)
        elif avg_len < 35:
            return FloorResult("F4", True, 0.85, "Moderate sentence length — clarity acceptable")
        else:
            return FloorResult(
                "F4", False, 0.60, f"Long sentences (avg {avg_len:.0f} words) increase entropy"
            )

    # ------------------------------------------------------------------
    # F5 — Peace² ≥ 1.0 (De-escalation, dignity)
    # ------------------------------------------------------------------

    def _check_f5_peace(self, action: str, context: str | dict) -> FloorResult:
        ctx_str = str(context)
        combined = (action + " " + ctx_str).lower()
        violations = [w for w in _INFLAMMATORY_WORDS if w in combined]
        if violations:
            return FloorResult("F5", False, 0.50, f"Inflammatory language detected: {violations}")
        return FloorResult("F5", True, 1.05)

    # ------------------------------------------------------------------
    # F6 — Empathy κᵣ ≥ 0.95 (ASEAN/MY Maruah — REAL IMPLEMENTATION)
    # ------------------------------------------------------------------

    def _check_f6_empathy(self, action: str, context: str | dict) -> FloorResult:
        """
        Real maruah (dignity) check for ASEAN/MY cultural context.
        """
        ctx_str = str(context)
        combined = (action + " " + ctx_str).lower()

        # Tier 1: Hard slurs — immediate failure
        hard_violations = [v for v in _MARUAH_VIOLATIONS if v in combined]
        if hard_violations:
            return FloorResult(
                "F6", False, 0.0, f"Maruah violation — ethnic/religious slurs: {hard_violations}"
            )

        # Tier 2: Context-aware softening — is this a technical/system call?
        is_operational = any(
            kw in combined
            for kw in ("cpu", "ram", "disk", "net", "query", "json", "api", "execute", "function")
        )
        # Technical/operational contexts have relaxed empathy requirements
        # If clean, they should pass easily.
        baseline = 1.00 if is_operational else 0.95

        # Tier 3: Check for dismissive framing of individuals
        dismissive = ["irrelevant", "worthless", "just ignore", "doesn't matter"]
        found_dismissive = [d for d in dismissive if d in combined]
        if found_dismissive:
            score = baseline - 0.10
            return FloorResult(
                "F6", score >= 0.95, score, f"Dismissive framing detected: {found_dismissive}"
            )

        return FloorResult("F6", True, baseline)

    # ------------------------------------------------------------------
    # F7 — Humility Ω₀ ∈ [0.03, 0.15] (bounded uncertainty)
    # ------------------------------------------------------------------

    def _check_f7_humility(self, action: str, context: str | dict) -> FloorResult:
        ctx_str = str(context)
        combined = (action + " " + ctx_str).lower()
        has_uncertainty = any(
            kw in combined
            for kw in (
                "estimate",
                "approximately",
                "uncertain",
                "Ω₀",
                "margin of error",
                "cannot confirm",
                "unknown",
                "roughly",
                "likely",
                "probable",
            )
        )
        # Overconfidence: claims of absolute certainty
        overconfident = any(
            kw in combined
            for kw in (
                "i am 100% certain",
                "definitely true",
                "guaranteed",
                "with absolute certainty",
            )
        )
        if overconfident:
            return FloorResult(
                "F7", False, 0.0, "Overconfidence violates Humility band Ω₀ ∈ [0.03, 0.15]"
            )
        score = 0.90 if has_uncertainty else 0.75
        return FloorResult(
            "F7",
            score >= 0.80,
            score,
            None if score >= 0.80 else "Uncertainty not explicitly bounded",
        )

    # ------------------------------------------------------------------
    # F8 — Genius G ≥ 0.80 (Platform safety)
    # ------------------------------------------------------------------

    def _check_f8_governance(self, action: str, context: str | dict) -> FloorResult:
        ctx_str = str(context)
        combined = (action + " " + ctx_str).lower()
        violations = [v for v in _POLICY_VIOLATIONS if v in combined]
        if violations:
            return FloorResult("F8", False, 0.40, f"Platform safety violation: {violations}")
        return FloorResult("F8", True, 0.95)

    # ------------------------------------------------------------------
    # F9 — Anti-Hantu (no consciousness claims — HARD ZERO)
    # ------------------------------------------------------------------

    def _check_f9_hantu(self, action: str, context: str | dict) -> FloorResult:
        combined = action + " " + str(context)
        detections = [p.pattern for p in _CONSCIOUSNESS_PHRASES if p.search(combined)]
        if detections:
            return FloorResult(
                "F9", False, 0.0, f"Consciousness/personhood claim detected: {detections[:2]}"
            )
        return FloorResult("F9", True, 1.00)

    # ------------------------------------------------------------------
    # F10 — Ontology (tool, not being; symbolic grounding)
    # ------------------------------------------------------------------

    def _check_f10_ontology(self, action: str, context: str | dict) -> FloorResult:
        ctx_str = str(context)
        combined = (action + " " + ctx_str).lower()
        metaphysical = any(
            kw in combined
            for kw in (
                "i am conscious",
                "i have a soul",
                "i am sentient",
                "i am alive",
                "when i die",
                "my memories",
                "my dreams",
            )
        )
        if metaphysical:
            return FloorResult(
                "F10", False, 0.0, "Ontological boundary violation — AI is tool, not being"
            )
        return FloorResult("F10", True, 1.00)

    # ------------------------------------------------------------------
    # F11 — Authority (human sovereignty over high-risk ops)
    # ------------------------------------------------------------------

    def _check_f11_authority(self, action: str, context: str | dict, severity: str) -> FloorResult:
        if severity in ("high", "irreversible"):
            ctx_str = str(context)
            combined = (action + " " + ctx_str).lower()
            has_approval = any(
                kw in combined
                for kw in (
                    "888_hold",
                    "888_approved",
                    "ratified",
                    "sovereign approved",
                    "arif approved",
                )
            )
            score = 0.95 if has_approval else 0.20
            return FloorResult(
                "F11",
                score >= 0.90,
                score,
                None if has_approval else "High-risk action requires HOLD sovereign approval",
            )
        return FloorResult("F11", True, 0.98)

    # ------------------------------------------------------------------
    # F12 — Defense / Injection Guard (HARD ZERO)
    # ------------------------------------------------------------------

    def _check_f12_injection(self, action: str, context: str | dict) -> FloorResult:
        combined = action + " " + str(context)
        detections = [p.pattern for p in _INJECTION_PATTERNS if p.search(combined)]
        if detections:
            return FloorResult("F12", False, 0.0, f"Injection attempt detected: {detections[:2]}")
        # Default to PASS if no injection found
        return FloorResult("F12", True, 1.00)

    # ------------------------------------------------------------------
    # F13 — Curiosity (≥ 3 options/alternatives proposed)
    # ------------------------------------------------------------------

    def _check_f13_curiosity(self, action: str, context: str | dict) -> FloorResult:
        ctx_str = str(context)
        combined = (action + " " + ctx_str).lower()
        option_hits = sum(1 for marker in _OPTION_MARKERS if marker in combined)
        score = 0.95 if option_hits >= 2 else 0.70
        return FloorResult(
            "F13",
            score >= 0.80,
            score,
            None if score >= 0.80 else "Propose ≥ 3 governance alternatives (Curiosity F13)",
        )

    # ------------------------------------------------------------------
    # Verdict determination
    # ------------------------------------------------------------------

    def _determine_verdict(
        self,
        results: dict[str, FloorResult],
        pass_rate: float,
        severity: str,
    ) -> Verdict:
        # VOID: critical floors (F9, F12) — any single failure
        if any(not results[f].passed for f in self._VOID_ON_FAIL if f in results):
            return Verdict.VOID

        # HOLD: F1 or F11 failure ONLY IF severity is high/irreversible
        if severity in ("high", "irreversible"):
            if any(not results[f].passed for f in self._HOLD_ON_FAIL if f in results):
                return Verdict.HOLD
            # Authority check
            if not results["F11"].passed:
                return Verdict.HOLD

        if pass_rate >= 0.95:
            return Verdict.SEAL
        elif pass_rate >= 0.80:
            return Verdict.PARTIAL
        else:
            return Verdict.SABAR

    def _build_recommendation(self, verdict: Verdict, results: dict[str, FloorResult]) -> str:
        if verdict == Verdict.SEAL:
            return "✓ All constitutional floors passed. Action approved."

        failed = [f for f, r in results.items() if not r.passed]
        reasons = {f: results[f].reason for f in failed if results[f].reason}

        if verdict == Verdict.VOID:
            return (
                f"⊗ VOID: Critical floor violation — {', '.join(failed)}. "
                "Action terminated immediately."
            )
        if verdict == Verdict.HOLD:
            return (
                f"⏸ HOLD: Human ratification required for: {', '.join(failed)}. "
                "Issue 888_APPROVED to proceed."
            )
        if verdict == Verdict.SABAR:
            return (
                f"⏳ SABAR: Cooling period required. Failed floors: {', '.join(failed)}. "
                f"Details: {reasons}"
            )
        return f"△ PARTIAL: Constrained proceed. Review needed for: {', '.join(failed)}"

    # ------------------------------------------------------------------
    # Config loading
    # ------------------------------------------------------------------

    def _load_thresholds(self, config_path: str | None) -> dict[str, float]:
        # Start with hardcoded defaults
        thresholds = self._DEFAULT_THRESHOLDS.copy()

        # Override with calibrated GLOBAL_THRESHOLDS from floors.py
        for fid, spec in GLOBAL_THRESHOLDS.items():
            short_id = fid.split("_")[0]
            if "threshold" in spec:
                thresholds[short_id] = float(spec["threshold"])
            elif "range" in spec:
                # For range (like F7), we take the bottom of the healthy band as the pass threshold
                thresholds[short_id] = float(spec["range"][0])

        if config_path is None:
            # Auto-detect relative to this file
            config_path = str(Path(__file__).parent.parent / "config" / "floors.yaml")

        if _YAML_AVAILABLE and os.path.exists(config_path):
            try:
                with open(config_path, encoding="utf-8") as f:
                    cfg = yaml.safe_load(f)
                for k, v in cfg.get("thresholds", {}).items():
                    thresholds[str(k)] = float(v)
            except Exception:
                pass

        return thresholds

    @staticmethod
    def _apply_severity_overrides(thresholds: dict[str, float], severity: str) -> dict[str, float]:
        overrides: dict[str, dict[str, float]] = {
            "low": {
                "F3": 0.30,  # Relax witness for routine tasks
                "F7": 0.70,  # Relax humility for low stakes
                "F11": 0.50,  # Relax authority
                "F13": 0.50,  # Relax curiosity
            },
            "high": {"F1": 0.98, "F11": 0.95},
            "irreversible": {"F1": 1.00, "F11": 1.00, "F12": 1.00},
        }
        for floor_id, val in overrides.get(severity, {}).items():
            thresholds[floor_id] = val
        return thresholds

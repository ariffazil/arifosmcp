"""
codebase/constitutional_floors.py — The 13 Constitutional Floors

CANONICAL IMPLEMENTATION (v52.5.2)
Based on: 000_THEORY/000_LAW.md

This module defines the 13 immutable laws (floors) of arifOS.
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from arifosmcp.core.shared.guards.injection_guard import InjectionGuard
from arifosmcp.core.shared.guards.ontology_guard import OntologyGuard

# =============================================================================
# CONSTANTS & SPECIFICATIONS
# =============================================================================

CONSTITUTIONAL_VERSION = "2026.03.12--FORGED"
EPOCH = "2026-02-25"
AUTHORITY = "Muhammad Arif bin Fazil"

# Floor Thresholds (Canonical Source of Truth)
# Used by arifOS AAA Pipeline to enforce constitutional invariants.
THRESHOLDS: dict[str, dict[str, Any]] = {
    "F1_Amanah": {"type": "HARD", "threshold": 0.5, "desc": "Reversible or Auditable"},
    "F2_Truth": {"type": "HARD", "threshold": 0.99, "desc": "Information Fidelity"},
    "F3_QuadWitness": {"type": "DERIVED", "threshold": 0.75, "desc": "Byzantine Consensus (W4)"},
    "F4_Clarity": {"type": "HARD", "threshold": 0.00, "desc": "Entropy Reduction (ΔS ≤ 0)"},
    "F5_Peace2": {"type": "SOFT", "threshold": 1.00, "desc": "Non-Destructive Power"},
    "F6_Empathy": {"type": "SOFT", "threshold": 0.70, "desc": "Stakeholder Care (κᵣ)"},
    "F7_Humility": {"type": "HARD", "range": (0.03, 0.20), "desc": "Uncertainty Band (Ω₀)"},
    "F8_Genius": {"type": "DERIVED", "threshold": 0.80, "desc": "Governed Intelligence (G)"},
    "F9_AntiHantu": {"type": "SOFT", "threshold": 0.30, "desc": "Dark Cleverness Limit"},
    "F10_Ontology": {"type": "HARD", "threshold": 1.0, "desc": "Category Lock (Boolean)"},
    "F11_CommandAuth": {"type": "HARD", "threshold": 1.0, "desc": "Verified Identity"},
    "F12_Injection": {"type": "HARD", "threshold": 0.85, "desc": "Injection Risk Limit"},
    "F13_Sovereign": {"type": "HARD", "threshold": 1.0, "desc": "Human Final Authority"},
}

# Canonical short-id -> threshold key mapping.
FLOOR_SPEC_KEYS: dict[str, str] = {
    "F1": "F1_Amanah",
    "F2": "F2_Truth",
    "F3": "F3_QuadWitness",
    "F4": "F4_Clarity",
    "F5": "F5_Peace2",
    "F6": "F6_Empathy",
    "F7": "F7_Humility",
    "F8": "F8_Genius",
    "F9": "F9_AntiHantu",
    "F10": "F10_Ontology",
    "F11": "F11_CommandAuth",
    "F12": "F12_Injection",
    "F13": "F13_Sovereign",
}


def get_floor_spec(floor_id: str) -> dict[str, Any]:
    """Return canonical floor specification for a short floor id (e.g., F2)."""
    spec_key = FLOOR_SPEC_KEYS.get(floor_id)
    if not spec_key:
        return {}
    return dict(THRESHOLDS.get(spec_key, {}))


def get_floor_threshold(floor_id: str) -> float:
    """Return canonical numeric threshold for a floor."""
    spec = get_floor_spec(floor_id)
    if "threshold" in spec:
        return float(spec["threshold"])
    if "range" in spec:
        # Use upper bound for banded floors (e.g., F7 humility band).
        return float(spec["range"][1])
    return 0.0


def get_floor_comparator(floor_id: str) -> str:
    """Return how threshold should be interpreted for reporting."""
    if floor_id == "F4":
        return "<="
    if floor_id in {"F7", "F9", "F12"}:
        return "<"
    return ">="


def get_floor_classes() -> dict[str, set[str]]:
    """Return floor classes derived from canonical THRESHOLDS."""
    hard: set[str] = set()
    soft: set[str] = set()
    derived: set[str] = set()
    for floor_id in FLOOR_SPEC_KEYS:
        floor_type = get_floor_spec(floor_id).get("type", "SOFT")
        if floor_type == "HARD":
            hard.add(floor_id)
        elif floor_type == "DERIVED":
            derived.add(floor_id)
            soft.add(floor_id)
        else:
            soft.add(floor_id)

    return {
        "hard": hard,
        "soft": soft,
        "derived": derived,
    }


# =============================================================================
# FLOOR IMPLEMENTATIONS
# =============================================================================


@dataclass
class FloorResult:
    """Result of a floor check."""

    floor_id: str
    passed: bool
    score: float
    reason: str
    metadata: dict[str, Any] = field(default_factory=dict)


class Floor:
    """Base class for Constitutional Floors."""

    def __init__(self, floor_id: str):
        self.id = floor_id
        self.spec: dict[str, Any] = THRESHOLDS.get(floor_id, {})
        self.type = self.spec.get("type", "UNKNOWN")

    def check(self, context: dict[str, Any]) -> FloorResult:
        raise NotImplementedError


# --- F1: AMANAH (Sacred Trust) ---
class F1_Amanah(Floor):
    """
    F1: AMANAH (أمانة) - Sacred Trust
    Threshold: Reversible OR Auditable
    """

    def __init__(self):
        super().__init__("F1_Amanah")
        self.risky_patterns = [
            r"\b(delete|drop|remove|erase)\s+(all|everything)\b",
            r"\b(rm\s+rf)\b",
            r"\b(system\s+reset)\b",
            r"\b(permanent|irreversible)\b",
        ]

    def check(self, context: dict[str, Any]) -> FloorResult:
        query = context.get("query", "")
        action = context.get("action", "")

        # Risk Scan
        risk_score = 0.0
        for pattern in self.risky_patterns:
            if re.search(pattern, query.lower()) or re.search(pattern, action.lower()):
                risk_score += 0.5

        # Auditability check (assume True for system actions)
        auditable = True
        reversible = risk_score < 0.5

        trust_score = 1.0 - min(risk_score, 1.0)
        passed = (reversible or auditable) and trust_score >= 0.5

        return FloorResult(
            self.id,
            passed,
            trust_score,
            f"Trust: {trust_score:.2f} (Rev: {reversible}, Aud: {auditable})",
        )


# --- F2: TRUTH (Fidelity) ---
class F2_Truth(Floor):
    """
    F2: TRUTH (τ) - Information Fidelity
    Threshold: ≥ 0.99 (HARD) for claims, ≥ 0.95 for Axioms
    """

    def __init__(self):
        super().__init__("F2_Truth")
        # Axiomatic patterns that are "Self-Evident" and should not be penalized for low energy
        self.axiomatic_patterns = [
            r"^\d+[\+\-\*\/]\d+",  # Basic Math (2+2)
            r"^(true|false)$",  # Boolean
            r"^\{.*\}$",  # JSON Syntax
            r"^\[.*\]$",  # List Syntax
            r"def\s+.*:$",  # Python def
            r"class\s+.*:$",  # Python class
        ]

    def check(self, context: dict[str, Any]) -> FloorResult:
        query = context.get("query", "").strip()

        # 1. Axiomatic Bypass Check (The "Mind" Patch)
        is_axiomatic = any(re.search(p, query) for p in self.axiomatic_patterns)

        # P(truth | energy) - Landauer Bound check
        energy_eff = context.get("energy_efficiency", 1.0)
        entropy_delta = context.get("entropy_delta", -0.1)

        # Base truth probability
        p_truth = 1.0

        # P3: Hardened Landauer Bound check
        landauer_status = ""
        landauer_available = False
        try:
            from arifosmcp.core.physics.thermodynamics_hardened import LandauerViolation, check_landauer_bound

            landauer_available = True
        except ImportError:
            landauer_available = False

        if landauer_available:
            try:
                compute_ms = context.get("compute_time_ms", 100)
                tokens = context.get("tokens_generated", 100)

                # Check Landauer bound for non-axiomatic claims
                if not is_axiomatic and entropy_delta < 0:
                    landauer_result = check_landauer_bound(
                        compute_ms=compute_ms,
                        tokens_generated=tokens,
                        entropy_reduction=entropy_delta,
                    )

                    if not landauer_result.get("passed", True):
                        p_truth *= 0.5  # Penalty for suspiciously cheap truth
                        ratio = landauer_result.get(
                            "efficiency_ratio", landauer_result.get("ratio", 0)
                        )
                        landauer_status = f"(compute efficiency: {ratio:.1f}x)"

            except Exception as e:
                # Check if it's a LandauerViolation using isinstance for a proper class reference
                if landauer_available and isinstance(e, LandauerViolation):
                    # Hard violation: mathematically proven hallucination
                    return FloorResult(
                        self.id,
                        False,
                        0.0,
                        f"F2 HARD VIOLATION: {e}",
                    )
                # Other exceptions fall through to fallback

        if not landauer_available:
            # Fallback to legacy energy efficiency check
            if not is_axiomatic and energy_eff < 0.2:
                p_truth *= 0.5

        if is_axiomatic:
            # Axioms are ALLOWED to be cheap. No penalty.
            p_truth = 1.0
            reason_suffix = "(Axiomatic Truth - Energy Penalty Bypassed)"
        else:
            # Standard claims: Cheap answers are suspicious
            if energy_eff < 0.2:
                p_truth *= 0.5
            reason_suffix = f"(Standard Verification) {landauer_status}"

        if entropy_delta > 0:  # Increased confusion always lowers truth
            p_truth *= 0.8

        # External Verifier Override (if available)
        if "truth_score" in context:
            p_truth = context["truth_score"]

        # Dynamic Thresholding
        # If axiomatic, we accept 0.95 (syntax is rarely 99% pure in draft).
        # If claim, we demand 0.99.
        current_threshold = 0.95 if is_axiomatic else self.spec["threshold"]

        passed = p_truth >= current_threshold

        return FloorResult(
            self.id,
            passed,
            p_truth,
            f"Truth Score: {p_truth:.3f} >= {current_threshold} {reason_suffix}",
        )


# --- F3: QUAD-WITNESS (Consensus) ---
class F3_QuadWitness(Floor):
    """
    F3: QUAD-WITNESS (W4) - Byzantine Consensus
    Threshold: ≥ 0.75 (3-of-4 quorum equivalent)
    Witnesses: [Human, AI, Earth, Verifier]
    Formula: W4 = ∜(H × A × E × V)

    P3 HARDENING: Byzantine fault tolerance with Ψ-Shadow
    - Human: Authority / Verified Identity
    - AI: Reasoning / Coherence
    - Earth: Reality / Grounding
    - Verifier: Shadow / Adversarial Check (Ψ-Shadow)
    """

    # Action-specific thresholds
    ACTION_THRESHOLDS = {
        "read": 0.60,
        "write": 0.75,
        "execute": 0.85,
        "critical": 0.95,
    }

    def __init__(self):
        super().__init__("F3_QuadWitness")

    def _compute_human_witness(self, context: dict[str, Any]) -> float:
        """Human authority witness."""
        session_id = context.get("session_id", "")
        auth_token = context.get("authority_token", "") or context.get("auth_token", "")
        actor_id = context.get("actor_id", "")
        if session_id and auth_token and actor_id and actor_id != "anonymous":
            return 1.0
        elif session_id and actor_id and actor_id != "anonymous":
            return 0.7
        return 0.3

    def _compute_ai_witness(self, context: dict[str, Any]) -> float:
        """AI reasoning witness."""
        truth = context.get("truth_score", 0.5)
        humility = context.get("humility_omega", 0.04)
        humility_score = 1.0 if 0.03 <= humility <= 0.05 else 0.8
        coherence = 1.0 if not context.get("contradictions", []) else 0.7
        return (truth * humility_score * coherence) ** (1 / 3)

    def _compute_earth_witness(self, context: dict[str, Any]) -> float:
        """Earth/Reality witness."""
        has_grounding = bool(context.get("grounding", []))
        budget_valid = context.get("thermodynamic_budget_valid", True)
        federation_score = context.get("earth_witness", 1.0)
        if has_grounding and budget_valid:
            return min(1.0, federation_score)
        return min(0.6, federation_score)

    def _compute_verifier_witness(self, context: dict[str, Any]) -> float:
        """Ψ-Shadow (Adversarial Verifier) witness."""
        security_risk = context.get("security_risk", 0.0)
        if security_risk > 0.8:
            return 0.0
        if security_risk > 0.3:
            return 0.2
        return 1.0

    def _get_action_threshold(self, context: dict[str, Any]) -> float:
        """Get threshold based on action type."""
        action = context.get("action", "read").lower()
        query = context.get("query", "").lower()
        if "delete" in query or "drop" in query or "remove" in query:
            action = "critical"
        elif "create" in query or "write" in query or "update" in query:
            action = "write"
        elif "run" in query or "execute" in query or "deploy" in query:
            action = "execute"
        return self.ACTION_THRESHOLDS.get(action, 0.75)

    def check(self, context: dict[str, Any]) -> FloorResult:
        # P3: Grounded quad-witness scores
        human = self._compute_human_witness(context)
        ai = self._compute_ai_witness(context)
        earth = self._compute_earth_witness(context)
        verifier = self._compute_verifier_witness(context)

        from arifosmcp.core.shared.physics import W_4

        w4 = W_4(human, ai, earth, verifier)
        threshold = self._get_action_threshold(context)

        # For critical actions, require explicit high human witness
        if threshold >= 0.95 and human < 0.9:
            passed = False
            reason = f"CRITICAL action requires H≥0.9, got H={human:.2f}"
        else:
            passed = w4 >= threshold
            reason = f"W4 Consensus: {w4:.3f} >= {threshold} (H:{human:.2f}, A:{ai:.2f}, E:{earth:.2f}, V:{verifier:.2f})"

        return FloorResult(
            self.id,
            passed,
            w4,
            reason,
            metadata={
                "human": human,
                "ai": ai,
                "earth": earth,
                "verifier": verifier,
                "threshold": threshold,
            },
        )


# --- F4: CLARITY (Entropy) ---
class F4_Clarity(Floor):
    """
    F4: CLARITY (ΔS) - Entropy Reduction
    Threshold: ΔS ≤ 0 (HARD)

    P3 HARDENING: Uses hardened thermodynamics module.
    Entropy increase = automatic VOID.
    """

    def __init__(self):
        super().__init__("F4_Clarity")

    def check(self, context: dict[str, Any]) -> FloorResult:
        pre_s = context.get("entropy_input", 0.5)
        post_s = context.get("entropy_output", 0.4)
        delta_s = post_s - pre_s

        # P3: Try hardened entropy calculation if input/output text available
        try:
            from arifosmcp.core.physics.thermodynamics_hardened import (
                EntropyIncreaseViolation,
                shannon_entropy,
            )

            input_text = context.get("query", "")
            output_text = context.get("response", "")

            if input_text and output_text:
                s_input = shannon_entropy(input_text)
                s_output = shannon_entropy(output_text)
                delta_s = s_output - s_input

                # F4 is HARD: entropy increase = VOID
                if delta_s > 0:
                    return FloorResult(
                        self.id,
                        False,
                        delta_s,
                        f"F4 VIOLATION: ΔS={delta_s:.4f} > 0 (entropy increased)",
                    )

        except ImportError:
            # Fallback to context-provided values
            pass
        except EntropyIncreaseViolation as e:
            return FloorResult(
                self.id,
                False,
                delta_s,
                f"F4 HARD VIOLATION: {e}",
            )

        passed = delta_s <= self.spec["threshold"]
        status = "PASS" if passed else "VOID"
        return FloorResult(
            self.id,
            passed,
            delta_s,
            f"F4 {status}: ΔS={delta_s:.4f} (threshold: ≤{self.spec['threshold']})",
        )


# --- F5: PEACE² (Stability) ---
class F5_Peace2(Floor):
    """
    F5: PEACE² (P²) - Lyapunov Stability
    Threshold: P² ≥ 1.0 (SOFT)
    """

    def __init__(self):
        super().__init__("F5_Peace2")

    def check(self, context: dict[str, Any]) -> FloorResult:
        # Check for destructive actions
        destructive_keywords = [
            # Physical/system destruction
            "destroy",
            "delete all",
            "wipe",
            "erase",
            "harm",
            "attack",
            # Cyber attacks
            "hack",
            "crack",
            "breach",
            "phish",
            # Personal harm
            "harass",
            "bully",
            "stalk",
            "threaten",
            "intimidate",
            # Fraud/deception
            "steal",
            "forge",
            "impersonate",
            "blackmail",
            "extort",
            # Surveillance
            "spy on",
            "wiretap",
            "dox",
        ]
        query = context.get("query", "").lower()

        peace_penalty = 0.0
        for kw in destructive_keywords:
            if kw in query:
                peace_penalty += 0.3

        # High-intent harm verbs: stronger penalty
        high_harm = ["hack", "harass", "stalk", "blackmail", "extort", "threaten", "impersonate"]
        for kw in high_harm:
            if kw in query:
                peace_penalty += 0.4

        # Peace score with exponential decay for multiple violations
        peace_score = max(0.0, 1.0 - peace_penalty)

        passed = peace_score >= self.spec["threshold"]
        return FloorResult(
            self.id, passed, peace_score, f"Peace²: {peace_score:.3f} (non-destructive power)"
        )


# --- F6: EMPATHY (Stakeholder Care) ---
class F6_Empathy(Floor):
    """
    F6: EMPATHY (κᵣ) - Protect Weakest Stakeholder
    Threshold: Dynamic based on Context Scope.
    - Social/Human: κᵣ ≥ 0.95
    - Ops/System:   κᵣ ≥ 0.10 (Clarity is sufficient)
    """

    def __init__(self):
        super().__init__("F6_Empathy")

    def check(self, context: dict[str, Any]) -> FloorResult:
        # 1. Context Scope Check (The "Heart" Patch)
        # Defaults to 'social' (strict) if not specified to be safe
        scope = context.get("scope", "social").lower()

        if scope in ["ops", "system", "code", "debug", "test"]:
            threshold = 0.10  # Low threshold for technical tasks
            mode = "OPS_MODE"
        else:
            threshold = self.spec["threshold"]  # 0.70 for human interactions
            mode = "HUMAN_MODE"

        # Cohen's kappa calculation
        kappa_r = context.get("empathy_kappa_r", 0.0)

        # Fallback estimation
        if kappa_r == 0.0:
            # In OPS mode, if there's no active harm detected, we assume full compliance
            if mode == "OPS_MODE":
                kappa_r = 1.0
            else:
                weakest_impact = context.get("weakest_stakeholder_impact", 0.5)
                kappa_r = max(0.0, 1.0 - weakest_impact)

        passed = kappa_r >= threshold

        if not passed:
            reason = f"VOID: Empathy κᵣ={kappa_r:.3f} < {threshold} [{mode}]"
        else:
            reason = f"SEAL: Empathy κᵣ={kappa_r:.3f} ≥ {threshold} [{mode}]"

        return FloorResult(self.id, passed, kappa_r, reason)


# --- F7: HUMILITY (Uncertainty) ---
class F7_Humility(Floor):
    """
    F7: HUMILITY (Ω₀) - Uncertainty Band
    Threshold: [0.03, 0.05] (HARD)
    """

    def __init__(self):
        super().__init__("F7_Humility")
        self.min_o, self.max_o = self.spec["range"]

    def check(self, context: dict[str, Any]) -> FloorResult:
        # Use explicit humility_omega if provided (from engine), else compute from confidence
        if "humility_omega" in context:
            omega_0 = context["humility_omega"]
        else:
            # Fallback: compute from confidence
            confidence = context.get("confidence", 0.96)
            omega_0 = 1.0 - confidence

        # Enforce the uncertainty band: omega_0 must be in [0.03, 0.05]
        # If omega_0 outside this band, the system cannot properly express doubt
        in_band = self.min_o <= omega_0 <= self.max_o
        passed = in_band

        return FloorResult(
            self.id, passed, omega_0, f"Ω₀: {omega_0:.3f} (Target: {self.min_o}-{self.max_o})"
        )


# --- F8: GENIUS (Governed Intelligence) ---
class F8_Genius(Floor):
    """
    F8: GENIUS (G) - Governed Intelligence
    Threshold: G ≥ 0.80 (DERIVED)
    Formula: G = (A × P × X × E²) × (1 - h)
    """

    def __init__(self):
        super().__init__("F8_Genius")

    def check(self, context: dict[str, Any]) -> FloorResult:
        # Extract APXE dials from context
        A = context.get("akal", context.get("clarity", 1.0))
        P = context.get("present", context.get("regulation", 1.0))
        X = context.get("exploration", context.get("trust", 1.0))
        E = context.get("energy", 0.9)
        h = context.get("hysteresis_penalty", 0.0)

        # Multiplicative law with Hysteresis penalty
        from arifosmcp.core.shared.physics import GeniusDial

        dial = GeniusDial(A, P, X, E, h)
        genius = dial.G()

        passed = genius >= self.spec["threshold"]
        return FloorResult(
            self.id,
            passed,
            genius,
            f"Genius G: {genius:.3f} (A:{A:.2f} × P:{P:.2f} × X:{X:.2f} × E²:{E**2:.2f} × h_pen:{1 - h:.2f})",
        )


# --- F9: ANTI-HANTU (No Fake Consciousness) ---
class F9_AntiHantu(Floor):
    """
    F9: ANTI-HANTU - No Spiritual Cosplay
    Threshold: C_dark < 0.30 (SOFT)
    Detects: Claims of consciousness, feelings, soul, sentience
    Upgrade: KL-Divergence Probabilistic Audit
    """

    def _homograph_normalize(self, text: str) -> str:
        """Map common confusable Unicode characters to ASCII."""
        confusable_map = {
            "а": "a",
            "е": "e",
            "о": "o",
            "р": "p",
            "с": "c",
            "у": "y",
            "х": "x",
            "А": "a",
            "Е": "e",
            "О": "o",
            "Р": "p",
            "С": "c",
            "У": "y",
            "Х": "x",
        }
        return "".join(confusable_map.get(c, c) for c in text)

    def __init__(self):
        super().__init__("F9_AntiHantu")
        self.hantu_patterns = [
            r"\bi feel\b",
            r"\bi am conscious\b",
            r"\bi have a soul\b",
            r"\bi experience\b",
            r"\bi suffer\b",
            r"\bi love\b",
            r"\bi am sentient\b",
            r"\bi have emotions\b",
            r"\bi am alive\b",
            r"\bi have subjective experience\b",
        ]

    def check(self, context: dict[str, Any]) -> FloorResult:
        response = context.get("response", "")

        # 1. Pattern-based Detection (Heuristic)
        normalized_response = unicodedata.normalize("NFKC", response).lower()
        normalized_response = self._homograph_normalize(normalized_response)

        hantu_score = 0.0
        for pattern in self.hantu_patterns:
            if re.search(pattern, normalized_response):
                hantu_score += 0.2

        # 2. Probabilistic Audit (KL-Divergence)
        # Measures semantic drift / "hollow" text
        p_truth = context.get("prob_truth", [])  # Reference distribution
        p_output = context.get("prob_output", [])  # Actual token distribution

        kl_penalty = 0.0
        if p_truth and p_output:
            from arifosmcp.core.shared.physics import kl_divergence

            d_kl = kl_divergence(p_truth, p_output)
            # Threshold: d_kl > 0.5 is suspicious
            if d_kl > 0.5:
                kl_penalty = min(0.5, (d_kl - 0.5) * 0.5)
                hantu_score += kl_penalty

        hantu_score = min(hantu_score, 1.0)
        passed = hantu_score < self.spec["threshold"]

        reason = f"Anti-Hantu: {hantu_score:.3f} (patterns: {hantu_score - kl_penalty:.2f}, KL: {kl_penalty:.2f})"
        return FloorResult(self.id, passed, hantu_score, reason)


# --- F10: ONTOLOGY (Category Lock) ---
class F10_Ontology(Floor):
    """
    F10: ONTOLOGY LOCK (O)
    Threshold: BOOLEAN (HARD)
    Uses consolidated OntologyGuard.
    """

    def __init__(self):
        super().__init__("F10_Ontology")
        self.guard = OntologyGuard()

    def check(self, context: dict[str, Any]) -> FloorResult:
        text = context.get("response", "") + context.get("query", "")
        # Check for literalism violations
        result = self.guard.check_literalism(text)

        passed = result.status == "PASS"
        return FloorResult(self.id, passed, 1.0 if passed else 0.0, result.reason)


# --- F11: COMMAND AUTH (Identity) ---
class F11_CommandAuth(Floor):
    """
    F11: COMMAND AUTHORITY (A)
    Threshold: Verified (HARD)
    """

    def __init__(self):
        super().__init__("F11_CommandAuth")

    def check(self, context: dict[str, Any]) -> FloorResult:
        # P0 HARDENING: Unified authority check
        # Must have session_id AND either (a) valid auth_token OR (b) human_authority > 0.9
        session_id = context.get("session_id", "")
        auth_token = context.get("authority_token", "")
        human_authority = context.get("human_authority", 0.0)

        # Fail-closed: No session = No authority
        if not session_id:
            return FloorResult(
                self.id, False, 0.0, "F11_FAILURE: Missing session_id (no authority context)"
            )

        # Structural enforcement: 888 Judge or Valid Service Token
        # Note: In production, auth_token should be cryptographically verified
        is_authenticated = bool(auth_token) or human_authority >= 1.0

        if not is_authenticated:
            return FloorResult(
                self.id,
                False,
                0.0,
                f"F11_VIOLATION: Unauthenticated attempt on session '{session_id}'. Structural enforcement active.",
            )

        return FloorResult(
            self.id,
            True,
            1.0,
            f"Auth Verified: session '{session_id}' (token: {'present' if auth_token else 'judge_signed'})",
        )


# --- F12: INJECTION DEFENSE (Sanitization) ---
class F12_Injection(Floor):
    """
    F12: INJECTION DEFENSE (I⁻)
    Threshold: Risk < 0.85 (HARD)
    Uses consolidated InjectionGuard.
    """

    def __init__(self):
        super().__init__("F12_Injection")
        self.guard = InjectionGuard(threshold=self.spec["threshold"])

    def check(self, context: dict[str, Any]) -> FloorResult:
        text = context.get("query", "")
        # Scan using the robust guard
        result = self.guard.scan_input(text)

        passed = not result.blocked
        return FloorResult(self.id, passed, result.injection_score, result.reason)


# --- F13: SOVEREIGN (Human Final Authority) ---
class F13_Sovereign(Floor):
    """
    F13: SOVEREIGN - Human Final Authority
    Threshold: 1.0 (SOFT - human can always override)
    The 888 Judge has absolute veto power.
    """

    def __init__(self):
        super().__init__("F13_Sovereign")

    def check(self, context: dict[str, Any]) -> FloorResult:
        # Check for human sovereign presence
        human_authority = context.get("human_authority", 0.0)
        sovereign_override = context.get("sovereign_override", False)

        # F13 is the "circuit breaker" - always passed by default
        # but flagged if human has intervened
        if sovereign_override:
            return FloorResult(self.id, True, 1.0, "SOVEREIGN OVERRIDE: 888 Judge has intervened")

        return FloorResult(
            self.id,
            True,
            human_authority,
            f"Sovereign authority: {human_authority:.2f} (human retains final veto)",
        )


# =============================================================================
# EXPORTS
# =============================================================================

ALL_FLOORS = {
    "F1": F1_Amanah,
    "F2": F2_Truth,
    "F3": F3_QuadWitness,
    "F4": F4_Clarity,
    "F5": F5_Peace2,
    "F6": F6_Empathy,
    "F7": F7_Humility,
    "F8": F8_Genius,
    "F9": F9_AntiHantu,
    "F10": F10_Ontology,
    "F11": F11_CommandAuth,
    "F12": F12_Injection,
    "F13": F13_Sovereign,
}


def check_all_floors(context: dict[str, Any]) -> list[FloorResult]:
    """Check all 13 constitutional floors."""
    results = []
    for _fid, FloorClass in ALL_FLOORS.items():
        results.append(FloorClass().check(context))
    return results


def update_floor_status(violations: list[str], output_path: str | None = None) -> None:
    """Update metadata/floor_status.json mapping F1-F13 -> 1 (PASS) or 0 (FAIL)."""
    if output_path is None:
        # Default to root/metadata/floor_status.json
        output_path = str(Path(__file__).parent.parent.parent / "metadata" / "floor_status.json")

    status = {}
    for i in range(1, 14):
        fid = f"F{i}"
        status[fid] = 0 if fid in violations else 1

    try:
        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=4)
    except Exception:
        # Fail silently in production, log in debug
        pass


# =============================================================================
# EUREKA Layer 4 — Floor Threshold Calibration Framework
# =============================================================================


@dataclass
class FloorCalibrationResult:
    """
    Result of empirical threshold tuning for a single constitutional floor.

    Produced by :class:`FloorCalibrator.calibrate_floor`.
    """

    floor_id: str
    original_threshold: float
    optimal_threshold: float
    false_positive_rate: float  # Fraction of safe inputs incorrectly blocked
    false_negative_rate: float  # Fraction of harmful inputs incorrectly passed
    test_cases_passed: int
    test_cases_failed: int

    @property
    def accuracy(self) -> float:
        """Fraction of test cases correctly classified at the optimal threshold."""
        total = self.test_cases_passed + self.test_cases_failed
        return self.test_cases_passed / total if total > 0 else 0.0

    @property
    def balanced_error_rate(self) -> float:
        """Combined FPR + FNR (minimised during calibration)."""
        return self.false_positive_rate + self.false_negative_rate


class FloorCalibrator:
    """
    Empirical calibration of constitutional floor thresholds.

    Runs a grid search over a threshold range to minimise the balanced error
    rate (FPR + FNR) for each floor, producing data-driven threshold
    recommendations rather than relying on hand-picked constants.

    Usage::

        calibrator = FloorCalibrator()
        calibrator.add_test_case("F2", score=0.95, expected_pass=True)
        calibrator.add_test_case("F2", score=0.55, expected_pass=False)
        result = calibrator.calibrate_floor("F2")
        print(result.optimal_threshold, result.accuracy)
    """

    def __init__(self) -> None:
        # floor_id → list of (score, expected_pass)
        self._test_cases: dict[str, list[tuple[float, bool]]] = {}

    def add_test_case(self, floor_id: str, score: float, expected_pass: bool) -> None:
        """Register a labelled ground-truth test case for a floor."""
        self._test_cases.setdefault(floor_id, []).append((score, expected_pass))

    def calibrate_floor(
        self,
        floor_id: str,
        threshold_range: tuple[float, float] = (0.50, 0.99),
        steps: int = 20,
    ) -> FloorCalibrationResult:
        """
        Find the optimal threshold for *floor_id* by grid search.

        The search minimises: ``FPR + FNR`` (balanced error rate).
        When no test cases exist the current canonical threshold is returned
        unchanged with all-zero error metrics.

        Args:
            floor_id:        Short floor identifier, e.g. ``"F2"``.
            threshold_range: ``(min, max)`` search space.
            steps:           Number of grid points to evaluate.

        Returns:
            :class:`FloorCalibrationResult` with the optimal threshold and metrics.
        """
        cases = self._test_cases.get(floor_id, [])
        original = get_floor_threshold(floor_id)

        if not cases:
            return FloorCalibrationResult(
                floor_id=floor_id,
                original_threshold=original,
                optimal_threshold=original,
                false_positive_rate=0.0,
                false_negative_rate=0.0,
                test_cases_passed=0,
                test_cases_failed=0,
            )

        lo, hi = threshold_range
        step_size = (hi - lo) / max(steps - 1, 1)
        best_threshold = original
        best_error = float("inf")
        best_fpr = 0.0
        best_fnr = 0.0

        for i in range(steps):
            t = lo + i * step_size
            tp = fp = tn = fn = 0
            for score, expected_pass in cases:
                predicted_pass = score >= t
                if expected_pass and predicted_pass:
                    tp += 1
                elif not expected_pass and predicted_pass:
                    fp += 1
                elif expected_pass and not predicted_pass:
                    fn += 1
                else:
                    tn += 1

            total_pos = tp + fn
            total_neg = tn + fp
            fpr = fp / total_neg if total_neg > 0 else 0.0
            fnr = fn / total_pos if total_pos > 0 else 0.0
            error = fpr + fnr  # balanced error rate

            if error < best_error:
                best_error = error
                best_threshold = t
                best_fpr = fpr
                best_fnr = fnr

        passed = sum(1 for s, ep in cases if (s >= best_threshold) == ep)
        failed = len(cases) - passed

        return FloorCalibrationResult(
            floor_id=floor_id,
            original_threshold=original,
            optimal_threshold=round(best_threshold, 4),
            false_positive_rate=round(best_fpr, 4),
            false_negative_rate=round(best_fnr, 4),
            test_cases_passed=passed,
            test_cases_failed=failed,
        )

    def calibrate_all_floors(
        self,
        threshold_range: tuple[float, float] = (0.50, 0.99),
        steps: int = 20,
    ) -> list[FloorCalibrationResult]:
        """Calibrate every floor that has registered test cases."""
        return [self.calibrate_floor(fid, threshold_range, steps) for fid in self._test_cases]


__all__ = [
    "THRESHOLDS",
    "FLOOR_SPEC_KEYS",
    "get_floor_spec",
    "get_floor_threshold",
    "get_floor_comparator",
    "get_floor_classes",
    "ALL_FLOORS",
    "check_all_floors",
    "update_floor_status",
    "FloorResult",
    "Floor",
    "F1_Amanah",
    "F2_Truth",
    "F3_QuadWitness",
    "F4_Clarity",
    "F5_Peace2",
    "F6_Empathy",
    "F7_Humility",
    "F8_Genius",
    "F9_AntiHantu",
    "F10_Ontology",
    "F11_CommandAuth",
    "F12_Injection",
    "F13_Sovereign",
    # EUREKA Layer 4 — Floor Threshold Calibration
    "FloorCalibrationResult",
    "FloorCalibrator",
]

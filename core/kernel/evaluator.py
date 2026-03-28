"""
core/kernel/evaluator.py — Constitutional Evaluation Engine

Pure kernel logic for enforcing the 13 Constitutional Floors.
This engine is transport-agnostic and handles the pre/post execution
validation lifecycle.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    from arifosmcp.core.shared.floors import get_floor_classes, get_floor_comparator, get_floor_threshold

    _FLOOR_CLASSES = get_floor_classes()
except Exception:
    _FLOOR_CLASSES = {
        "hard": {"F1", "F2", "F4", "F7", "F10", "F11", "F12", "F13"},
        "soft": {"F3", "F5", "F6", "F8", "F9"},
        "derived": {"F3", "F8"},
    }

    def get_floor_threshold(_floor_id: str) -> float:
        return 0.0

    def get_floor_comparator(_floor_id: str) -> str:
        return ">="


# ─── Floor Classification ───────────────────────────────────────────────────

# Mandatory floors run on EVERY evaluation (the "immune system").
MANDATORY_PRE_FLOORS: set[str] = {"F12"}

# Pre-execution floors: validate INPUT before action
PRE_FLOORS: set[str] = {"F1", "F5", "F6", "F11", "F12", "F13"}

# Post-execution floors: validate OUTPUT after action
POST_FLOORS: set[str] = {"F2", "F3", "F4", "F7", "F8", "F9", "F10"}

# Hard floors: failure -> VOID (block)
# F4 (Clarity/ΔS) is hard: entropy must decrease. Confusion increase = hard fail.
HARD_FLOORS: set[str] = set(_FLOOR_CLASSES.get("hard", set()))

# Soft/Derived floors: failure -> PARTIAL (warn)
SOFT_FLOORS: set[str] = set(_FLOOR_CLASSES.get("soft", set()))


class ConstitutionalEvaluator:
    """
    Orchestrates the validation of constitutional floors.

    Can be used by decorators, API gateways, or internal pipelines.
    """

    def __init__(self):
        self._floor_cache: dict[str, Any] = {}
        self._floors_available: bool | None = None

    def _load_all_floors(self) -> dict[str, Any] | None:
        """Lazy-load ALL_FLOORS from arifosmcp.core.shared.floors."""
        if self._floors_available is False:
            return None
        try:
            from arifosmcp.core.shared.floors import ALL_FLOORS

            self._floors_available = True
            return ALL_FLOORS
        except Exception as e:
            self._floors_available = False
            logger.error(f"Failed to load constitutional_floors: {e}")
            return None

    def _get_floor(self, floor_id: str):
        """Get or create a cached floor validator instance."""
        if floor_id in self._floor_cache:
            return self._floor_cache[floor_id]

        all_floors = self._load_all_floors()
        if all_floors is None:
            return None

        floor_cls = all_floors.get(floor_id)
        if floor_cls is None:
            return None

        try:
            instance = floor_cls()
            self._floor_cache[floor_id] = instance
            return instance
        except Exception as e:
            logger.error(f"Failed to instantiate {floor_id}: {e}")
            return None

    def check_floor(self, floor_id: str, context: dict[str, Any]) -> dict[str, Any]:
        """Run a single floor check."""
        threshold = get_floor_threshold(floor_id)
        comparator = get_floor_comparator(floor_id)
        floor_type = "HARD" if floor_id in HARD_FLOORS else "SOFT"

        floor = self._get_floor(floor_id)
        if floor is None:
            return {
                "floor": floor_id,
                "passed": False,
                "score": 0.0,
                "reason": "Floor unavailable (fail-closed)",
                "threshold": threshold,
                "comparator": comparator,
                "type": floor_type,
            }

        try:
            result = floor.check(context)
            return {
                "floor": floor_id,
                "passed": result.passed,
                "score": result.score,
                "reason": result.reason,
                "threshold": threshold,
                "comparator": comparator,
                "type": floor_type,
            }
        except Exception as e:
            logger.error(f"Floor {floor_id} check error: {e}")
            return {
                "floor": floor_id,
                "passed": False,
                "score": 0.0,
                "reason": f"Floor check error (fail-closed): {e}",
                "threshold": threshold,
                "comparator": comparator,
                "type": floor_type,
            }

    def build_pre_context(
        self, query: str, context_overrides: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Build context dict for pre-execution floor checks."""
        ctx = {
            "query": query,
            "action": query,
            "session_id": "",
            "role": "ANONYMOUS",
            "authority_token": "",
        }
        if context_overrides:
            ctx.update(context_overrides)

        # F11 normalization: never auto-escalate authority from session_id alone.
        if ctx.get("session_id") and not ctx.get("authority_token"):
            ctx["role"] = "SESSION_UNVERIFIED"
            ctx["authority_token"] = ""
            ctx["f11_continuity"] = "MISSING_AUTH_TOKEN"

        if ctx.get("session_id") and ctx.get("authority_token"):
            if ctx.get("role") == "ANONYMOUS":
                ctx["role"] = "AGENT"
            else:
                ctx["role"] = ctx.get("role") or "AGENT"
            ctx["f11_continuity"] = "VERIFIED"

        return ctx

    def build_post_context(
        self, query: str, result: Any, context_overrides: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Build context dict for post-execution floor checks."""
        # Extract response text from result
        response = ""
        if isinstance(result, dict):
            for key in ("response", "result", "reasoning", "analysis", "output"):
                val = result.get(key, "")
                if val:
                    response = str(val)
                    break
            if not response:
                response = str(result)
        else:
            response = str(result)

        ctx = {
            "query": query,
            "response": response,
            "confidence": 0.96,
            "entropy_input": 0.5,
            "entropy_output": 0.45,
            "human_witness": 0.8,
            "ai_witness": 1.0,
            "earth_witness": 1.0,
        }

        if context_overrides:
            ctx.update(context_overrides)

        # Override defaults with explicit metrics from result
        if isinstance(result, dict):
            for key in (
                "truth_score",
                "confidence",
                "entropy_delta",
                "human_witness",
                "ai_witness",
                "earth_witness",
                "empathy_kappa_r",
                "weakest_stakeholder_impact",
                "entropy_input",
                "entropy_output",
                "humility_omega",
                "f2_threshold",
            ):
                if key in result:
                    ctx[key] = result[key]

            if "entropy_delta" in result and "entropy_input" in ctx:
                ctx["entropy_output"] = ctx["entropy_input"] + result["entropy_delta"]

        return ctx

    def accumulate_floor_scores(self, floor_details: list[dict[str, Any]]) -> dict[str, float]:
        """Normalize accumulated scores for Genius engine."""
        scores: dict[str, float] = {}
        for d in floor_details:
            fid = d["floor"]
            score = d.get("score", 0.0)
            if fid == "F7":
                scores[fid] = 1.0 - score  # omega_0 -> confidence
            elif fid == "F9":
                scores[fid] = 1.0 - score  # c_dark -> anti-hantu safety
            elif fid == "F12":
                scores[fid] = 1.0 - score  # injection prob -> defense
            else:
                scores[fid] = score
        return scores

    def evaluate_verdict(self, floor_details: list[dict[str, Any]]) -> str:
        """Compute aggregate verdict (VOID | PARTIAL | SEAL)."""
        hard_fails = [d for d in floor_details if not d["passed"] and d["floor"] in HARD_FLOORS]
        soft_fails = [d for d in floor_details if not d["passed"] and d["floor"] in SOFT_FLOORS]

        if hard_fails:
            return "VOID"
        elif soft_fails:
            return "PARTIAL"
        return "SEAL"

    def build_self_audit(self, floor_details: list[dict[str, Any]], verdict: str) -> dict[str, Any]:
        """Build deterministic self-audit metadata for ARIF TEST observability."""
        hard_fails = [
            d["floor"] for d in floor_details if not d["passed"] and d["floor"] in HARD_FLOORS
        ]
        soft_fails = [
            d["floor"] for d in floor_details if not d["passed"] and d["floor"] in SOFT_FLOORS
        ]

        expected = self.evaluate_verdict(floor_details)
        consistent = expected == verdict

        return {
            "deterministic": True,
            "llm_inside_kernel": False,
            "self_reference_mode": "rule-audit",
            "hard_fails": hard_fails,
            "soft_fails": soft_fails,
            "expected_verdict": expected,
            "verdict_consistent": consistent,
        }


# Singleton instance
evaluator = ConstitutionalEvaluator()

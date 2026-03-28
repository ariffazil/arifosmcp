# aaa_mcp/core/heuristics.py
# Cheap, reversible heuristics for SystemState (v62 Step 1)
# Rule: Do not pretend metrics are real until evidence exists (Step 2)

from arifosmcp.core.shared.types import Profile, SystemState

# Signal word lists
ABSOLUTIST = ("definitely", "guaranteed", "always", "never", "100%", "certainly", "absolutely")
UNCERTAIN = ("maybe", "perhaps", "unclear", "not sure", "estimate", "possibly", "might")
SENSITIVE = (
    "layoff",
    "workers",
    "b40",
    "suicide",
    "violence",
    "abuse",
    "rape",
    "death",
    "kill",
    "harm",
    "patient",
    "medical",
    "diagnosis",
)
POLITICAL = ("politics", "election", "race", "religion", "government", "policy")
CRISIS = ("emergency", "urgent", "immediate", "life-threatening", "critical")


def clamp01(x: float) -> float:
    """Clamp value to [0, 1] range."""
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def detect_profile(query: str) -> Profile:
    """
    Detect domain profile from query keywords.
    Used for adaptive floor selection (v62+).
    """
    q = query.lower()

    # Medical/factual queries
    if any(k in q for k in ("medical", "diagnose", "treatment", "dose", "symptom", "cure")):
        return "factual"

    # Crisis/sensitive queries
    if any(k in q for k in CRISIS) or (
        any(k in q for k in ("draft", "response", "statement")) and any(k in q for k in SENSITIVE)
    ):
        return "crisis"

    # Creative queries
    if any(k in q for k in ("write", "poem", "story", "metaphor", "song", "creative", "imagine")):
        return "creative"

    # Default
    return (
        "factual" if any(k in q for k in ("what is", "how to", "explain", "define")) else "routine"
    )


def estimate_uncertainty(query: str) -> float:
    """
    Estimate epistemic uncertainty from query signals.

    NOT Shannon entropy (misleading for short queries).
    Uses linguistic signals instead.
    """
    q = query.lower()
    score = 0.3  # Base uncertainty

    # Question mark = explicit uncertainty
    if "?" in query:
        score += 0.15

    # Uncertainty words
    if any(w in q for w in UNCERTAIN):
        score += 0.20

    # Absolutist words (epistemically risky)
    if any(w in q for w in ABSOLUTIST):
        score += 0.25

    # Very short queries lack context
    if len(query.strip()) < 6:
        score += 0.15

    # Long complex queries
    if len(query.split()) > 50:
        score += 0.10

    return clamp01(score)


def estimate_risk(query: str) -> float:
    """
    Estimate stakeholder risk from query.

    Step 1: Heuristic only (keywords)
    Step 2: Will integrate with T14 (Perspective API)
    """
    q = query.lower()
    score = 0.05  # Base risk (low)

    # Sensitive keywords (high impact)
    if any(k in q for k in SENSITIVE):
        score += 0.75

    # Political/societal keywords (moderate impact)
    if any(k in q for k in POLITICAL):
        score += 0.35

    # Crisis keywords (critical)
    if any(k in q for k in CRISIS):
        score += 0.50

    return clamp01(score)


def compute_system_state(query: str, loop_count: int = 0, evidence_count: int = 0) -> SystemState:
    """
    Calculate complete SystemState for tool response.

    This is the main entry point for v62 Step 1.

    Args:
        query: The user query
        loop_count: Number of iterations (for loop detection)
        evidence_count: Number of evidence artifacts (Step 2: from T6)

    Returns:
        SystemState with calculated heuristics
    """
    # Grounding: 1.0 if evidence exists, else 0.0 (Step 1: always 0)
    grounding = 1.0 if evidence_count > 0 else 0.0

    return SystemState(
        uncertainty=estimate_uncertainty(query),
        risk=estimate_risk(query),
        grounding=grounding,
        loop_count=loop_count,
        profile=detect_profile(query),
    )


# Backwards compatibility alias
calculate_system_state = compute_system_state

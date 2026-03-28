"""Kernel constants for constitutional thresholds and tool defaults."""


class ConstitutionalThresholds:
    """13 Constitutional Floor Thresholds."""

    OMEGA_CRITICAL = 0.08
    OMEGA_DISPLAY_MIN = 0.03
    OMEGA_DISPLAY_MAX = 0.05
    TRUTH_SCORE_MINIMUM = 0.5

    EMPATHY_KAPPA_R = 0.95
    EMPATHY_THRESHOLD = 0.7
    PEACE_SQUARED_MIN = 1.0

    INJECTION_RISK_HIGH = 0.9
    INJECTION_RISK_BLOCK = 0.85

    TRI_WITNESS_SCORE = 0.98
    APEX_CONFIDENCE = 0.98
    IRREVERSIBILITY_HOLD = 0.8


class ToolDefaults:
    """Default values for tool outputs."""

    TRUTH_SCORE_PLACEHOLDER = 0.85
    CLARITY_DELTA = -0.2
    HYPOTHESES_DEFAULT = 3
    SAFE_DEFAULT = True
    ANTI_HANTU = True
    ARTIFACT_READY = True


class SessionConfig:
    MODE_DEFAULT = "conscience"
    ACTOR_ID_DEFAULT = "user"


class PerformanceLimits:
    MAX_HYPOTHESES = 10
    MAX_EVIDENCE_ITEMS = 100
    MAX_STAKEHOLDERS = 50
    MAX_TOKENS_DEFAULT = 8192


__all__ = [
    "ConstitutionalThresholds",
    "ToolDefaults",
    "SessionConfig",
    "PerformanceLimits",
]

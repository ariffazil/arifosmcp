"""
Eureka Nudge - Lightweight emergence prompts
Just a little push. That's it.
"""

from dataclasses import dataclass
from enum import Enum


class NudgeType(Enum):
    """Types of cognitive nudges for emergence."""

    REFRAME = "reframe"  # See it differently
    INVERT = "invert"  # Flip the problem
    ZOOM_OUT = "zoom_out"  # Broader context
    ZOOM_IN = "zoom_in"  # Specific detail
    CONNECT = "connect"  # Link to unrelated
    SIMPLIFY = "simplify"  # Remove complexity
    EXTREME = "extreme"  # Edge case test
    FIRST = "first"  # Beginner's mind


@dataclass(frozen=True)
class EurekaNudge:
    """A lightweight cognitive nudge."""

    type: NudgeType
    prompt_addition: str
    description: str


# The nudge library - just little pushes
NUDGES = {
    NudgeType.REFRAME: EurekaNudge(
        type=NudgeType.REFRAME,
        prompt_addition="\n[Reframe] What if this isn't about the obvious thing? What hidden pattern connects?",
        description="Shift perspective to see hidden structures",
    ),
    NudgeType.INVERT: EurekaNudge(
        type=NudgeType.INVERT,
        prompt_addition="\n[Invert] How would you FAIL at this? Now avoid that.",
        description="Flip the problem to reveal constraints",
    ),
    NudgeType.ZOOM_OUT: EurekaNudge(
        type=NudgeType.ZOOM_OUT,
        prompt_addition="\n[Zoom Out] What larger system contains this? How does it breathe there?",
        description="See the broader context",
    ),
    NudgeType.ZOOM_IN: EurekaNudge(
        type=NudgeType.ZOOM_IN,
        prompt_addition="\n[Zoom In] Find one concrete, specific example. Touch it.",
        description="Ground in specific detail",
    ),
    NudgeType.CONNECT: EurekaNudge(
        type=NudgeType.CONNECT,
        prompt_addition="\n[Connect] What unrelated domain solves similar problems? Steal from there.",
        description="Cross-domain analogy",
    ),
    NudgeType.SIMPLIFY: EurekaNudge(
        type=NudgeType.SIMPLIFY,
        prompt_addition="\n[Simplify] Remove 80% of the complexity. What's the 20% that matters?",
        description="Strip to essence",
    ),
    NudgeType.EXTREME: EurekaNudge(
        type=NudgeType.EXTREME,
        prompt_addition="\n[Extreme] What if this was 100x bigger? 1000x smaller? What breaks?",
        description="Stress test at boundaries",
    ),
    NudgeType.FIRST: EurekaNudge(
        type=NudgeType.FIRST,
        prompt_addition="\n[First Principles] Forget what you know. Build from atoms.",
        description="Strip accumulated assumptions",
    ),
}


def get_nudge(nudge_type: NudgeType | None = None) -> EurekaNudge:
    """Get a specific nudge or random one."""
    import random

    if nudge_type is None:
        nudge_type = random.choice(list(NudgeType))
    return NUDGES[nudge_type]


def apply_nudge(query: str, nudge: EurekaNudge | None = None) -> str:
    """Apply a nudge to a query. Just a little push."""
    if nudge is None:
        nudge = get_nudge()
    return f"{query}{nudge.prompt_addition}"


# Quick nudge functions for direct use
def reframe(query: str) -> str:
    """Reframe perspective."""
    return apply_nudge(query, NUDGES[NudgeType.REFRAME])


def invert(query: str) -> str:
    """Invert the problem."""
    return apply_nudge(query, NUDGES[NudgeType.INVERT])


def zoom_out(query: str) -> str:
    """Zoom to broader context."""
    return apply_nudge(query, NUDGES[NudgeType.ZOOM_OUT])


def zoom_in(query: str) -> str:
    """Zoom to specific detail."""
    return apply_nudge(query, NUDGES[NudgeType.ZOOM_IN])


def connect(query: str) -> str:
    """Connect to unrelated domain."""
    return apply_nudge(query, NUDGES[NudgeType.CONNECT])


def simplify(query: str) -> str:
    """Strip complexity."""
    return apply_nudge(query, NUDGES[NudgeType.SIMPLIFY])


def extreme(query: str) -> str:
    """Test at extremes."""
    return apply_nudge(query, NUDGES[NudgeType.EXTREME])


def first_principles(query: str) -> str:
    """Build from atoms."""
    return apply_nudge(query, NUDGES[NudgeType.FIRST])

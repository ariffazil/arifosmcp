"""
core/perception/reality_ingest.py — First-Class Reality Feedback Loop

Elevates external observability (L3 Civilization) into internal
reasoning (L1 Instruction). This ensures the system is not
just closed-loop reasoning, but adaptive intelligence.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RealitySignal:
    """A data point from external environment."""

    source: str
    content: str
    reliability: float  # [0.0, 1.0]
    timestamp: datetime = field(default_factory=datetime.now)
    tags: list[str] = field(default_factory=list)


class PerceptionSubsystem:
    """
    The 'Senses' of the arifOS kernel.
    Filters and ingests external reality signals for cognition.
    """

    def __init__(self):
        self._signal_buffer: list[RealitySignal] = []
        self._grounding_knowledge_base: dict[str, str] = {}

    def ingest(self, source: str, content: str, reliability: float = 0.5):
        """Standard ingestion. Filters for signal-to-noise ratio (F4)."""
        if reliability < 0.2:
            return  # Noise filter

        signal = RealitySignal(source=source, content=content, reliability=reliability)
        self._signal_buffer.append(signal)

        # In a real system, this would trigger an L1 'Axiom Update' workflow
        # if the reliability is high enough.

    def query_reality(self, query: str) -> list[RealitySignal]:
        """Search the signal buffer for relevant grounding evidence."""
        # Simple string matching for now
        return [s for s in self._signal_buffer if query.lower() in s.content.lower()]

    def get_latest_signals(self, limit: int = 5) -> list[RealitySignal]:
        return sorted(self._signal_buffer, key=lambda x: x.timestamp, reverse=True)[:limit]


# Global singleton
perception = PerceptionSubsystem()

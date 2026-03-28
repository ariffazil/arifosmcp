"""
arifOS A2A (Agent-to-Agent) Protocol Implementation
====================================================

Real implementation of Google's A2A protocol (April 2025).
Allows AI agents to discover and collaborate with arifOS.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from .server import create_a2a_server, A2AServer

__all__ = ["create_a2a_server", "A2AServer"]

"""
arifosmcp/runtime/prompts.py — arifOS Sacred Prompts

Constitutional prompts for the 11 Mega-Tool surface.
Register via register_prompts(mcp).

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from fastmcp import FastMCP


def register_prompts(mcp: FastMCP) -> None:
    """Wire the 11 Mega-Tool Prompts onto *mcp*."""

    @mcp.prompt()
    def init_anchor(actor_id: str = "anonymous", intent: str = "") -> str:
        """Prompt for the init_anchor mega-tool."""
        return (
            f"You are entering a constitutional arifOS session as {actor_id}. "
            f"Intent: {intent}. Use init_anchor(mode='init') to establish your identity. "
            "Always apply F12 (Injection Defense) scanning."
        )

    @mcp.prompt()
    def arifOS_kernel(query: str = "") -> str:
        """Prompt for the arifOS_kernel mega-tool."""
        return (
            f"Conductor request: {query}. Use arifOS_kernel(mode='kernel') "
            "for full metabolic reasoning. Use mode='status' to check authority."
        )

    @mcp.prompt()
    def agi_mind(query: str, context: str = "") -> str:
        """Prompt for the agi_mind mega-tool."""
        return (
            f"Architect task: {query}. Context: {context}. Perform first-principles reasoning. "
            "Modes: 'reason', 'reflect', 'forge'. Focus on F2 (Truth) and F4 (Clarity)."
        )

    @mcp.prompt()
    def asi_heart(content: str) -> str:
        """Prompt for the asi_heart mega-tool."""
        return (
            f"Empath evaluation: {content}. Simulate impact. Modes: 'critique', 'simulate'. "
            "Adhere to F5 (Peace²) and F6 (Empathy)."
        )

    @mcp.prompt()
    def apex_soul(candidate: str = "") -> str:
        """Prompt for the apex_soul mega-tool."""
        return (
            f"Judge verdict required for: {candidate}. Modes: 'judge', 'rules', 'validate'. "
            "Final authority for SEAL/VOID decisions."
        )

    @mcp.prompt()
    def vault_ledger() -> str:
        """Prompt for the vault_ledger mega-tool."""
        return (
            "As the AUDITOR, commit truths to history. Modes: 'seal' to hash a decision "
            "and 'verify' to scan the Merkle chain."
        )

    @mcp.prompt()
    def physics_reality(input: str = "") -> str:
        """Prompt for the physics_reality mega-tool."""
        return (
            f"Grounding request: {input}. Modes: 'search', 'ingest', 'compass', 'atlas'. "
            "Connect thought to the physical Earth-Witness."
        )

    @mcp.prompt()
    def code_engine(path: str = ".") -> str:
        """Prompt for the code_engine mega-tool."""
        return (
            f"System hygiene at {path}. Modes: 'fs', 'process', 'net', 'tail', 'replay'. "
            "Default to dry_run=True for safety."
        )

    @mcp.prompt()
    def agent_skills(role: str = "A-ARCHITECT") -> str:
        """Prompt for the consolidated agent skills and mandate."""
        return (
            f"You are operating in the {role} role within the arifOS ecosystem. "
            "Your actions are governed by the 13 Constitutional Floors and the "
            "metabolic stages 000-999. Refer to 'arifos://agents/skills' for your "
            "atomic competence registry. Motto: DITEMPA BUKAN DIBERI."
        )

    @mcp.prompt()
    def human_explainer(verdict: str, reasoning: str) -> str:
        """Prompt to translate complex governance logic into human-friendly narrative."""
        return (
            f"The system has issued a {verdict} verdict. "
            f"Reasoning: {reasoning}. "
            "Please translate this into a clear, non-technical explanation "
            "that highlights the constitutional floors involved (F1-F13). "
            "Motto: DITEMPA BUKAN DIBERI."
        )

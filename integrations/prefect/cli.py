"""
arifOS × Cyclopts CLI

Modern CLI for arifOS using Cyclopts (better than Typer).
Provides intuitive command-line interface to all 11 mega-tools.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Literal

try:
    from cyclopts import App, Parameter
    from cyclopts.types import ExistingPath
    CYCLOPTS_AVAILABLE = True
except ImportError:
    CYCLOPTS_AVAILABLE = False
    App = None
    Parameter = None
    ExistingPath = None

from arifosmcp.runtime.megaTools import (
    init_anchor,
    physics_reality,
    engineering_memory,
    agi_mind,
    asi_heart,
    apex_soul,
    vault_ledger,
    arifOS_kernel,
    math_estimator,
    code_engine,
    architect_registry,
)
from arifosmcp.runtime.models import Verdict
from arifosmcp.runtime.public_registry import public_tool_names

logger = logging.getLogger(__name__)


def create_cyclopts_app() -> App:
    """
    Create a Cyclopts App for arifOS CLI.
    
    Returns:
        Configured Cyclopts App
        
    Example:
        app = create_cyclopts_app()
        app()
    """
    if not CYCLOPTS_AVAILABLE:
        raise RuntimeError("Cyclopts not installed. Run: pip install cyclopts")
    
    app = App(
        name="arifos",
        help="arifOS Sovereign Intelligence Kernel CLI",
        version="2026.03.28",
    )
    
    # ═══════════════════════════════════════════════════════════════════════
    # 000_INIT: init_anchor
    # ═══════════════════════════════════════════════════════════════════════
    
    @app.command
    async def init(
        mode: Literal["init", "state", "revoke", "refresh"] = "init",
        session_id: str | None = None,
        actor_id: str = "cli-user",
        declared_name: str | None = None,
        risk_tier: str = "medium",
        dry_run: bool = False,
    ):
        """
        Initialize or manage an arifOS session.
        
        Parameters
        ----------
        mode
            Operation mode: init, state, revoke, refresh
        session_id
            Unique session identifier
        actor_id
            Actor identifier
        declared_name
            Declared actor name
        risk_tier
            Risk classification: micro, low, medium, high, critical
        dry_run
            Simulate without executing
        """
        result = await init_anchor(
            mode=mode,
            session_id=session_id,
            actor_id=actor_id,
            declared_name=declared_name,
            risk_tier=risk_tier,
            dry_run=dry_run,
        )
        
        print(f"Verdict: {result.verdict}")
        print(f"Stage: {result.stage}")
        if result.session_id:
            print(f"Session: {result.session_id}")
        if result.payload:
            print(f"Payload: {json.dumps(result.payload, indent=2)}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # 111_SENSE: physics_reality
    # ═══════════════════════════════════════════════════════════════════════
    
    @app.command
    async def search(
        query: str,
        mode: Literal["search", "ingest", "compass", "atlas", "time"] = "search",
        top_k: int = 5,
        session_id: str | None = None,
        dry_run: bool = True,
    ):
        """
        Search and acquire ground truth from reality.
        
        Parameters
        ----------
        query
            Search query or URL to ingest
        mode
            Search mode: search, ingest, compass, atlas, time
        top_k
            Number of results to return
        session_id
            Active session ID
        dry_run
            Simulate without executing
        """
        result = await physics_reality(
            mode=mode,
            query=query,
            payload={"top_k": top_k},
            session_id=session_id,
            dry_run=dry_run,
        )
        
        print(f"Verdict: {result.verdict}")
        if result.verdict == Verdict.SEAL:
            print(f"Results: {json.dumps(result.payload, indent=2)}")
        else:
            print(f"Error: {result.payload.get('error', 'Unknown')}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # 333_MIND: agi_mind
    # ═══════════════════════════════════════════════════════════════════════
    
    @app.command
    async def reason(
        query: str,
        mode: Literal["reason", "reflect", "forge"] = "reason",
        session_id: str | None = None,
        dry_run: bool = True,
    ):
        """
        AGI Reasoning - think, reflect, or forge solutions.
        
        Parameters
        ----------
        query
            Problem or question to reason about
        mode
            Reasoning mode: reason, reflect, forge
        session_id
            Active session ID
        dry_run
            Simulate without executing
        """
        result = await agi_mind(
            mode=mode,
            payload={"query": query},
            session_id=session_id,
            dry_run=dry_run,
        )
        
        print(f"Verdict: {result.verdict}")
        if hasattr(result, 'payload'):
            print(json.dumps(result.payload, indent=2, default=str))
    
    # ═══════════════════════════════════════════════════════════════════════
    # 666_HEART: asi_heart
    # ═══════════════════════════════════════════════════════════════════════
    
    @app.command
    async def critique(
        proposal: str,
        mode: Literal["critique", "simulate"] = "critique",
        session_id: str | None = None,
    ):
        """
        ASI Safety - critique proposals or simulate consequences.
        
        Parameters
        ----------
        proposal
            Proposal to analyze
        mode
            Analysis mode: critique or simulate
        session_id
            Active session ID
        """
        result = await asi_heart(
            mode=mode,
            payload={"proposal": proposal},
            session_id=session_id,
            dry_run=False,
        )
        
        print(f"Verdict: {result.verdict}")
        print(f"Assessment: {json.dumps(result.payload, indent=2, default=str)}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # 888_JUDGE: apex_soul
    # ═══════════════════════════════════════════════════════════════════════
    
    @app.command
    async def judge(
        candidate: str,
        mode: Literal["validate", "judge", "hold", "probe"] = "validate",
        session_id: str | None = None,
    ):
        """
        APEX Judgment - validate, judge, or probe candidates.
        
        Parameters
        ----------
        candidate
            Candidate to evaluate (code, decision, etc.)
        mode
            Judgment mode: validate, judge, hold, probe
        session_id
            Active session ID
        """
        result = await apex_soul(
            mode=mode,
            payload={"candidate": candidate},
            session_id=session_id,
        )
        
        print(f"Verdict: {result.verdict}")
        print(json.dumps(result.payload, indent=2, default=str))
    
    # ═══════════════════════════════════════════════════════════════════════
    # 999_VAULT: vault_ledger
    # ═══════════════════════════════════════════════════════════════════════
    
    @app.command
    async def seal(
        data: str,
        mode: Literal["seal", "verify"] = "seal",
        session_id: str | None = None,
    ):
        """
        Seal data to immutable vault or verify integrity.
        
        Parameters
        ----------
        data
            JSON data to seal or entry ID to verify
        mode
            Operation: seal or verify
        session_id
            Active session ID
        """
        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            payload = {"content": data}
        
        result = await vault_ledger(
            mode=mode,
            payload=payload,
            session_id=session_id,
        )
        
        print(f"Verdict: {result.verdict}")
        print(json.dumps(result.payload, indent=2, default=str))
    
    # ═══════════════════════════════════════════════════════════════════════
    # M-4_ARCH: architect_registry
    # ═══════════════════════════════════════════════════════════════════════
    
    @app.command
    def tools():
        """List all available arifOS tools."""
        print("arifOS Mega-Tools (11):")
        print()
        for name in sorted(public_tool_names()):
            print(f"  • {name}")
        print()
        print("Use --help with any command for details.")
    
    @app.command
    async def health(
        session_id: str | None = None,
    ):
        """Check arifOS system health."""
        from arifosmcp.runtime.megaTools import math_estimator
        
        result = await math_estimator(
            mode="health",
            session_id=session_id,
        )
        
        print(f"Status: {result.verdict}")
        if hasattr(result, 'payload'):
            vitals = result.payload.get('vitals', {})
            for key, value in vitals.items():
                print(f"  {key}: {value}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # 444_ROUTER: arifOS_kernel
    # ═══════════════════════════════════════════════════════════════════════
    
    @app.command
    async def kernel(
        intent: str,
        mode: Literal["kernel", "router", "status"] = "kernel",
        session_id: str | None = None,
    ):
        """
        Direct call to arifOS kernel router.
        
        Parameters
        ----------
        intent
            Natural language intent
        mode
            Kernel mode: kernel, router, status
        session_id
            Active session ID
        """
        result = await arifOS_kernel(
            mode=mode,
            payload={"intent": intent},
            session_id=session_id,
        )
        
        print(f"Verdict: {result.verdict}")
        print(json.dumps(result.payload, indent=2, default=str))
    
    return app


# Entry point for CLI
def main():
    """Run arifOS CLI."""
    app = create_cyclopts_app()
    app()


if __name__ == "__main__":
    main()

"""
arifOS Tools as Prefect Tasks

Wraps arifOS mega-tools as Prefect @task decorators for workflow orchestration.
"""

from __future__ import annotations

import functools
import logging
from typing import Any, Callable

try:
    from prefect import flow, task, get_run_logger
    from prefect.tasks import Task as PrefectTask
    PREFECT_AVAILABLE = True
except ImportError:
    PREFECT_AVAILABLE = False
    flow = lambda **kw: lambda f: f
    task = lambda **kw: lambda f: f
    get_run_logger = lambda: logging.getLogger(__name__)

from arifosmcp.runtime.megaTools import (
    init_anchor,
    physics_reality,
    engineering_memory,
    agi_mind,
    asi_heart,
    apex_soul,
    vault_ledger,
)
from arifosmcp.runtime.models import RuntimeEnvelope, Verdict

logger = logging.getLogger(__name__)


def arifos_task(tool_func: Callable, **task_kwargs) -> PrefectTask:
    """
    Decorator to wrap an arifOS mega-tool as a Prefect task.
    
    Args:
        tool_func: The arifOS mega-tool function
        **task_kwargs: Additional kwargs for Prefect @task decorator
        
    Returns:
        Prefect Task wrapped function
        
    Example:
        @arifos_task(physics_reality, retries=3)
        async def research(query: str):
            return await physics_reality(mode="search", payload={"query": query})
    """
    if not PREFECT_AVAILABLE:
        logger.warning("Prefect not installed, task decorator is passthrough")
        return tool_func
    
    @task(**task_kwargs)
    async def wrapped_task(*args, **kwargs) -> RuntimeEnvelope:
        prefect_logger = get_run_logger()
        prefect_logger.info(f"Executing arifOS tool: {tool_func.__name__}")
        
        try:
            result = await tool_func(*args, **kwargs)
            
            # Log constitutional verdict
            if hasattr(result, 'verdict'):
                prefect_logger.info(f"Verdict: {result.verdict}")
                
                # Fail task on VOID verdict (unless suppressed)
                if result.verdict == Verdict.VOID and not kwargs.get('allow_void'):
                    raise ValueError(f"Constitutional violation: {result.verdict}")
            
            return result
            
        except Exception as e:
            prefect_logger.error(f"arifOS tool failed: {e}")
            raise
    
    return wrapped_task


# Pre-configured arifOS tasks
@task(retries=2, retry_delay_seconds=5)
async def research_task(query: str, top_k: int = 5) -> dict:
    """
    Prefect task for arifOS physics_reality search.
    
    Args:
        query: Search query
        top_k: Number of results
        
    Returns:
        Research findings payload
    """
    logger = get_run_logger()
    logger.info(f"Researching: {query}")
    
    result = await physics_reality(
        mode="search",
        payload={"query": query, "top_k": top_k}
    )
    
    if result.verdict == Verdict.VOID:
        raise ValueError(f"Research blocked: {result.payload.get('error', 'Unknown')}")
    
    return result.payload


@task(retries=1)
async def vault_seal_task(data: dict, session_id: str) -> dict:
    """
    Prefect task for sealing data to arifOS vault.
    
    Args:
        data: Data to seal
        session_id: Session identifier
        
    Returns:
        Vault record
    """
    logger = get_run_logger()
    logger.info(f"Sealing to vault: {session_id}")
    
    result = await vault_ledger(
        mode="seal",
        payload={"data": data, "session_id": session_id}
    )
    
    return result.payload


@task
async def safety_check_task(proposal: dict) -> dict:
    """
    Prefect task for ASI Heart safety critique.
    
    Args:
        proposal: Proposal to critique
        
    Returns:
        Safety assessment
    """
    logger = get_run_logger()
    logger.info("Running safety check")
    
    result = await asi_heart(
        mode="critique",
        payload={"proposal": proposal}
    )
    
    # Block on high risk
    if result.payload.get('risk_level') == 'critical':
        raise ValueError("Critical risk detected - blocking execution")
    
    return result.payload


@flow(name="Constitutional Research Pipeline")
async def constitutional_flow(
    query: str,
    session_id: str | None = None,
    require_safety: bool = True
) -> dict:
    """
    Prefect flow with full arifOS constitutional governance.
    
    Flow stages:
    1. Initialize session (init_anchor)
    2. Research (physics_reality)
    3. Safety check [optional] (asi_heart)
    4. Record to vault (vault_ledger)
    
    Args:
        query: Research query
        session_id: Optional session ID
        require_safety: Whether to require safety check
        
    Returns:
        Complete pipeline result
    """
    logger = get_run_logger()
    logger.info(f"Starting constitutional flow: {query}")
    
    # Stage 1: Initialize
    if session_id:
        anchor_result = await init_anchor(
            mode="state",
            session_id=session_id
        )
        logger.info(f"Session state: {anchor_result.verdict}")
    
    # Stage 2: Research
    findings = await research_task(query)
    logger.info(f"Research complete: {len(findings.get('results', []))} results")
    
    # Stage 3: Safety check
    safety_result = None
    if require_safety:
        safety_result = await safety_check_task({"query": query, "findings": findings})
        logger.info(f"Safety check: {safety_result.get('assessment', 'unknown')}")
    
    # Stage 4: Record to vault
    record = await vault_seal_task({
        "query": query,
        "findings": findings,
        "safety_check": safety_result
    }, session_id or "anonymous")
    
    logger.info(f"Vault record created: {record.get('entry_id', 'unknown')}")
    
    return {
        "query": query,
        "findings": findings,
        "safety_check": safety_result,
        "vault_record": record
    }


# Deployment helper
def deploy_flow():
    """Deploy the constitutional flow to Prefect."""
    if not PREFECT_AVAILABLE:
        raise RuntimeError("Prefect not installed")
    
    from prefect.deployments import Deployment
    
    deployment = Deployment.build_from_flow(
        flow=constitutional_flow,
        name="arifos-constitutional-research",
        work_queue_name="arifos-constitutional",
        schedule=None  # Manual trigger or add cron
    )
    
    deployment.apply()
    print("✅ Constitutional flow deployed to Prefect")

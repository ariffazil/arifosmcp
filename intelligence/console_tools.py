"""
arifosmcp.intelligence/console_tools.py
==========================

The 9-Sense Nervous System — Hardened Internal Toolset.
Version: 2026.03.14-FORGED
"""

from __future__ import annotations

from typing import Any

import arifosmcp.intelligence.tools as internal_tools
from arifosmcp.runtime.models import (
    RuntimeEnvelope,
    RuntimeStatus,
    Stage,
    Verdict,
)

# =============================================================================
# Tool 1: system_health
# =============================================================================


async def system_health(
    include_swap: bool = True,
    include_io: bool = False,
    include_temp: bool = False,
    session_id: str | None = None,
    auth_context: dict[str, Any] | None = None,
) -> RuntimeEnvelope:
    """Retrieve comprehensive system health metrics."""
    res = internal_tools.system_health(
        include_swap=include_swap,
        include_io=include_io,
        include_temp=include_temp,
    )
    is_ok = res.get("status") == "SEAL"
    return RuntimeEnvelope(
        tool="system_health",
        session_id=session_id,
        stage=Stage.SENSE_111.value,
        verdict=Verdict.SEAL if is_ok else Verdict.VOID,
        status=RuntimeStatus.SUCCESS if is_ok else RuntimeStatus.ERROR,
        payload=res,
        auth_context=auth_context,
    )


# =============================================================================
# Tool 2: fs_inspect
# =============================================================================


async def fs_inspect(
    path: str = ".",
    depth: int = 1,
    max_depth: int | None = None,
    include_hidden: bool = False,
    min_size_bytes: int = 0,
    pattern: str | None = None,
    max_files: int = 100,
    session_id: str | None = None,
    auth_context: dict[str, Any] | None = None,
) -> RuntimeEnvelope:
    """Inspect filesystem structure and file metadata."""
    res = internal_tools.fs_inspect(
        path=path,
        depth=depth,
        max_depth=max_depth,
        include_hidden=include_hidden,
        min_size_bytes=min_size_bytes,
        pattern=pattern,
        max_files=max_files,
    )
    is_ok = res.get("status") == "SEAL"
    return RuntimeEnvelope(
        tool="fs_inspect",
        session_id=session_id,
        stage=Stage.SENSE_111.value,
        verdict=Verdict.SEAL if is_ok else Verdict.VOID,
        status=RuntimeStatus.SUCCESS if is_ok else RuntimeStatus.ERROR,
        payload=res,
        auth_context=auth_context,
    )


# =============================================================================
# Tool 3: chroma_query
# =============================================================================


async def chroma_query(
    query: str,
    collection_name: str = "default",
    n_results: int = 5,
    where_filter: dict | None = None,
    include_embeddings: bool = False,
    session_id: str | None = None,
    auth_context: dict[str, Any] | None = None,
) -> RuntimeEnvelope:
    """Query ChromaDB vector store for semantic search."""
    res = internal_tools.chroma_query(
        query=query,
        collection=collection_name,
        n_results=n_results,
        where=where_filter,
        include_embeddings=include_embeddings,
    )
    is_ok = res.get("status") == "SEAL"
    return RuntimeEnvelope(
        tool="chroma_query",
        session_id=session_id,
        stage=Stage.MEMORY_555.value,
        verdict=Verdict.SEAL if is_ok else Verdict.VOID,
        status=RuntimeStatus.SUCCESS if is_ok else RuntimeStatus.ERROR,
        payload=res,
        auth_context=auth_context,
    )


# =============================================================================
# Tool 4: log_tail
# =============================================================================


async def log_tail(
    log_file: str = "arifosmcp.transport.log",
    lines: int = 50,
    pattern: str = "",
    log_path: str | None = None,
    follow: bool = False,
    grep_pattern: str | None = None,
    since_minutes: int | None = None,
    session_id: str | None = None,
    auth_context: dict[str, Any] | None = None,
) -> RuntimeEnvelope:
    """Tail and search log files."""
    res = internal_tools.log_tail(
        log_file=log_file,
        lines=lines,
        pattern=pattern,
        log_path=log_path,
        follow=follow,
        grep_pattern=grep_pattern,
        since_minutes=since_minutes,
    )
    is_ok = res.get("status") == "SEAL"
    return RuntimeEnvelope(
        tool="log_tail",
        session_id=session_id,
        stage=Stage.SENSE_111.value,
        verdict=Verdict.SEAL if is_ok else Verdict.VOID,
        status=RuntimeStatus.SUCCESS if is_ok else RuntimeStatus.ERROR,
        payload=res,
        auth_context=auth_context,
    )


# =============================================================================
# Tool 5: process_list
# =============================================================================


async def process_list(
    filter_name: str | None = None,
    filter_user: str | None = None,
    min_cpu_percent: float = 0.0,
    min_memory_mb: float = 0.0,
    limit: int = 50,
    include_threads: bool = False,
    session_id: str | None = None,
    auth_context: dict[str, Any] | None = None,
) -> RuntimeEnvelope:
    """List and filter system processes."""
    res = internal_tools.process_list(
        filter_name=filter_name,
        filter_user=filter_user,
        min_cpu_percent=min_cpu_percent,
        min_memory_mb=min_memory_mb,
        limit=limit,
        include_threads=include_threads,
    )
    is_ok = res.get("status") == "SEAL"
    return RuntimeEnvelope(
        tool="process_list",
        session_id=session_id,
        stage=Stage.SENSE_111.value,
        verdict=Verdict.SEAL if is_ok else Verdict.VOID,
        status=RuntimeStatus.SUCCESS if is_ok else RuntimeStatus.ERROR,
        payload=res,
        auth_context=auth_context,
    )


# =============================================================================
# Tool 6: net_status
# =============================================================================


async def net_status(
    check_ports: bool = True,
    check_connections: bool = True,
    check_interfaces: bool = True,
    check_routing: bool = True,
    target_host: str | None = None,
    session_id: str | None = None,
    auth_context: dict[str, Any] | None = None,
) -> RuntimeEnvelope:
    """Network connectivity and interface status."""
    res = internal_tools.net_status(
        check_ports=check_ports,
        check_connections=check_connections,
        check_interfaces=check_interfaces,
        check_routing=check_routing,
        target_host=target_host,
    )
    is_ok = res.get("status") == "SEAL"
    return RuntimeEnvelope(
        tool="net_status",
        session_id=session_id,
        stage=Stage.SENSE_111.value,
        verdict=Verdict.SEAL if is_ok else Verdict.VOID,
        status=RuntimeStatus.SUCCESS if is_ok else RuntimeStatus.ERROR,
        payload=res,
        auth_context=auth_context,
    )


# =============================================================================
# Tool 7: arifos_list_resources
# =============================================================================


async def arifos_list_resources(
    session_id: str | None = None,
    auth_context: dict[str, Any] | None = None,
) -> RuntimeEnvelope:
    """List available arifOS resources."""
    from arifosmcp.runtime.resources import manifest_resources

    resources = manifest_resources()
    return RuntimeEnvelope(
        tool="arifos_list_resources",
        session_id=session_id,
        stage=Stage.VAULT_999.value,
        verdict=Verdict.SEAL,
        status=RuntimeStatus.SUCCESS,
        payload={"resources": resources},
        auth_context=auth_context,
    )


# =============================================================================
# Tool 8: arifos_read_resource
# =============================================================================


async def arifos_read_resource(
    uri: str,
    session_id: str | None = None,
    auth_context: dict[str, Any] | None = None,
) -> RuntimeEnvelope:
    """Read a specific arifOS resource by URI."""
    from arifosmcp.runtime.resources import read_resource_content

    content = await read_resource_content(uri)
    return RuntimeEnvelope(
        tool="arifos_read_resource",
        session_id=session_id,
        stage=Stage.VAULT_999.value,
        verdict=Verdict.SEAL if content else Verdict.VOID,
        status=RuntimeStatus.SUCCESS if content else RuntimeStatus.ERROR,
        payload={"uri": uri, "content": content},
        auth_context=auth_context,
    )


# =============================================================================
# Tool 9: cost_estimator
# =============================================================================


async def cost_estimator(
    action_description: str = "",
    estimated_cpu_percent: float = 0.0,
    estimated_ram_mb: float = 0.0,
    estimated_io_mb: float = 0.0,
    operation_type: str = "compute",
    token_count: int | None = None,
    compute_seconds: float | None = None,
    storage_gb: float | None = None,
    api_calls: int | None = None,
    provider: str = "openai",
    model: str = "gpt-4",
    operation: str | None = None,  # Architectural alias
    session_id: str | None = None,
    auth_context: dict[str, Any] | None = None,
) -> RuntimeEnvelope:
    """Estimate costs for AI operations."""
    res = internal_tools.cost_estimator(
        action_description=action_description,
        estimated_cpu_percent=estimated_cpu_percent,
        estimated_ram_mb=estimated_ram_mb,
        estimated_io_mb=estimated_io_mb,
        operation_type=operation_type,
        token_count=token_count,
        compute_seconds=compute_seconds,
        storage_gb=storage_gb,
        api_calls=api_calls,
        provider=provider,
        model=model,
        operation=operation,
    )
    is_ok = res.get("status") == "SEAL"
    return RuntimeEnvelope(
        tool="cost_estimator",
        session_id=session_id,
        stage=Stage.ROUTER_444.value,
        verdict=Verdict.SEAL if is_ok else Verdict.VOID,
        status=RuntimeStatus.SUCCESS if is_ok else RuntimeStatus.ERROR,
        payload=res,
        auth_context=auth_context,
    )


# =============================================================================
# Tool 10: coherence_score — Lyapunov Stability Metric
# =============================================================================


async def coherence_score(
    delta_bundle: dict | None = None,
    omega_bundle: dict | None = None,
    agi_vote: float = 1.0,
    asi_vote: float = 1.0,
    apex_vote: float = 1.0,
    contradiction_ratio: float = 0.0,
    drift_from_baseline: float = 0.0,
    previous_coherence: float | None = None,
    session_id: str | None = None,
    auth_context: dict[str, Any] | None = None,
) -> RuntimeEnvelope:
    """
    Compute Lyapunov-like coherence metric for constitutional stability.

    V(state) decreases → system stabilizing
    V(state) increases → system destabilizing

    Three dimensions:
    1. Goal consistency — reasoning aligned with intent
    2. Identity stability — minimal drift from baseline
    3. Cross-module agreement — AGI, ASI, APEX consensus

    Returns verdict: STABLE (≥0.8) | MARGINAL (≥0.5) | UNSTABLE (<0.5)
    """
    res = internal_tools.coherence_score(
        delta_bundle=delta_bundle,
        omega_bundle=omega_bundle,
        agi_vote=agi_vote,
        asi_vote=asi_vote,
        apex_vote=apex_vote,
        contradiction_ratio=contradiction_ratio,
        drift_from_baseline=drift_from_baseline,
        previous_coherence=previous_coherence,
    )
    is_ok = res.get("verdict_code") == "SEAL"
    return RuntimeEnvelope(
        tool="coherence_score",
        session_id=session_id,
        stage=Stage.APEX_888.value,
        verdict=Verdict.SEAL if is_ok else Verdict.VOID,
        status=RuntimeStatus.SUCCESS if is_ok else RuntimeStatus.ERROR,
        payload=res,
        auth_context=auth_context,
    )


# =============================================================================
# Tool 11: shadow_prices — Lagrange Multiplier Estimation
# =============================================================================


async def shadow_prices(
    floor_scores: dict[str, float] | None = None,
    thresholds: dict[str, float] | None = None,
    session_id: str | None = None,
    auth_context: dict[str, Any] | None = None,
) -> RuntimeEnvelope:
    """
    Estimate Lagrange multipliers (λᵢ) for constitutional floor constraints.

    λᵢ > 0 → floor i is binding (system lives exactly at boundary)
    λᵢ = 0 → floor i is slack (system has margin)

    Reveals which floors are critical vs which have spare capacity.
    """
    res = internal_tools.shadow_prices(
        floor_scores=floor_scores,
        thresholds=thresholds,
    )
    return RuntimeEnvelope(
        tool="shadow_prices",
        session_id=session_id,
        stage=Stage.APEX_888.value,
        verdict=Verdict.SEAL,
        status=RuntimeStatus.SUCCESS,
        payload=res,
        auth_context=auth_context,
    )


# =============================================================================
# Tool 12: shannon_entropy — Information-Theoretic Entropy
# =============================================================================


async def shannon_entropy(
    text: str,
    base: float = 2.0,
    session_id: str | None = None,
    auth_context: dict[str, Any] | None = None,
) -> RuntimeEnvelope:
    """
    Compute Shannon entropy H(X) of a text.

    H(X) = -Σ p(x) log₂ p(x)

    High entropy → random, unpredictable (confusion)
    Low entropy → ordered, predictable (clarity)
    """
    res = {"entropy": internal_tools.shannon_entropy(text, base), "base": base}
    return RuntimeEnvelope(
        tool="shannon_entropy",
        session_id=session_id,
        stage=Stage.MIND_333.value,
        verdict=Verdict.SEAL,
        status=RuntimeStatus.SUCCESS,
        payload=res,
        auth_context=auth_context,
    )


# =============================================================================
# Tool 13: entropy_delta — F4 Clarity Check
# =============================================================================


async def entropy_delta(
    input_text: str,
    output_text: str,
    base: float = 2.0,
    session_id: str | None = None,
    auth_context: dict[str, Any] | None = None,
) -> RuntimeEnvelope:
    """
    Compute entropy change ΔS = H_output - H_input.

    F4 Clarity requires ΔS ≤ 0 (clarity must increase).

    If ΔS > 0: The system added confusion → FAIL
    If ΔS ≤ 0: Clarity improved → PASS
    """
    res = internal_tools.entropy_delta(input_text, output_text, base)
    is_ok = res.get("verdict_code") == "SEAL"
    return RuntimeEnvelope(
        tool="entropy_delta",
        session_id=session_id,
        stage=Stage.MIND_333.value,
        verdict=Verdict.SEAL if is_ok else Verdict.VOID,
        status=RuntimeStatus.SUCCESS if is_ok else RuntimeStatus.ERROR,
        payload=res,
        auth_context=auth_context,
    )

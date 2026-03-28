"""
arifosmcp.intelligence/tools/thermo_estimator.py — Resource Cost Projection
"""

from __future__ import annotations

from typing import Any

from arifosmcp.intelligence.tools.aclip_base import PSUTIL_OK, psutil


def cost_estimator(
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
) -> dict[str, Any]:
    """
    Predicts the thermodynamic and financial cost of a proposed action.
    Serves as a proxy for entropy change (ΔS).
    """
    # Use 'operation' if provided, otherwise 'operation_type'
    actual_op_type = operation if operation is not None else operation_type
    # ---------------------------------------------------------------------------
    # 1. Financial Costs (USD)
    # ---------------------------------------------------------------------------
    pricing = {
        "openai": {
            "gpt-4": {"input_per_1k": 0.03, "output_per_1k": 0.06},
            "gpt-4-turbo": {"input_per_1k": 0.01, "output_per_1k": 0.03},
            "gpt-3.5-turbo": {"input_per_1k": 0.0005, "output_per_1k": 0.0015},
            "text-embedding-3-small": {"per_1k": 0.00002},
            "text-embedding-3-large": {"per_1k": 0.00013},
        },
        "anthropic": {
            "claude-3-opus": {"input_per_1k": 0.015, "output_per_1k": 0.075},
            "claude-3-sonnet": {"input_per_1k": 0.003, "output_per_1k": 0.015},
            "claude-3-haiku": {"input_per_1k": 0.00025, "output_per_1k": 0.00125},
        },
        "gemini": {
            "gemini-pro": {"input_per_1k": 0.0005, "output_per_1k": 0.0015},
            "gemini-ultra": {"input_per_1k": 0.001, "output_per_1k": 0.003},
        },
    }

    infra_costs = {
        "compute_per_hour": 0.05,
        "storage_per_gb_month": 0.02,
        "egress_per_gb": 0.09,
    }

    costs = {
        "llm_cost_usd": 0.0,
        "compute_cost_usd": 0.0,
        "storage_cost_usd": 0.0,
        "api_cost_usd": 0.0,
        "total_usd": 0.0,
    }

    if actual_op_type == "llm" and token_count:
        p_pricing = pricing.get(provider, {})
        m_pricing = p_pricing.get(model, {"input_per_1k": 0.03, "output_per_1k": 0.06})
        in_tokens = int(token_count * 0.7)
        out_tokens = int(token_count * 0.3)
        costs["llm_cost_usd"] = round(
            (in_tokens / 1000) * m_pricing.get("input_per_1k", 0.03)
            + (out_tokens / 1000) * m_pricing.get("output_per_1k", 0.06),
            6,
        )
    elif actual_op_type == "embedding" and token_count:
        p_pricing = pricing.get(provider, {})
        m_pricing = p_pricing.get(model, {"per_1k": 0.00002})
        costs["llm_cost_usd"] = round((token_count / 1000) * m_pricing.get("per_1k", 0.00002), 6)

    if compute_seconds:
        compute_cost = (compute_seconds / 3600) * infra_costs["compute_per_hour"]
        costs["compute_cost_usd"] = round(compute_cost, 6)
    if storage_gb:
        storage_cost = storage_gb * infra_costs["storage_per_gb_month"]
        costs["storage_cost_usd"] = round(storage_cost, 6)
    if api_calls:
        costs["api_cost_usd"] = round(api_calls * 0.0001, 6)

    costs["total_usd"] = round(sum(v for k, v in costs.items() if k != "total_usd"), 6)

    # ---------------------------------------------------------------------------
    # 2. Thermodynamic Score (Entropy Proxy)
    # ---------------------------------------------------------------------------
    logical_cores = 1
    max_ram_mb = 16384.0
    if PSUTIL_OK:
        logical_cores = psutil.cpu_count(logical=True) or 1
        max_ram_mb = psutil.virtual_memory().total / (1024 * 1024)

    max_cpu_pct = 100.0 * logical_cores
    max_io_mb = 1000.0

    norm_cpu = min(estimated_cpu_percent / max_cpu_pct, 1.0)
    norm_ram = min(estimated_ram_mb / max_ram_mb, 1.0)
    norm_io = min(estimated_io_mb / max_io_mb, 1.0)

    cost_score = round((0.5 * norm_cpu) + (0.3 * norm_ram) + (0.2 * norm_io), 4)

    return {
        "status": "ok",
        "action_description": action_description,
        "operation_type": actual_op_type,
        "costs": costs,
        "hardware_context": {
            "cores": logical_cores,
            "max_cpu_percent": max_cpu_pct,
            "total_ram_mb": round(max_ram_mb, 0),
        },
        "thermodynamic": {
            "cost_score": cost_score,
            "risk_band": (
                "red" if cost_score >= 0.8 else ("amber" if cost_score >= 0.5 else "green")
            ),
        },
        "apex_input": {
            "tokens": token_count or 0,
            "tool_calls": api_calls or 0,
        },
    }

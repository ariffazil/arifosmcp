"""
arifosmcp/runtime/contracts_v2.py — Hardened Constitutional Contracts (v4)

BACKWARD COMPATIBILITY: This file re-exports all items from contracts.py.
The hardened contracts have been merged into contracts.py as of 2026-03-28.
All imports should migrate to `from arifosmcp.runtime.contracts import ...`.

This file is kept for backward compatibility with existing imports.
"""

from arifosmcp.runtime.contracts import (
    ToolStatus,
    OutputPolicy,
    VerdictScope,
    RiskTier,
    HumanDecisionMarker,
    SessionClass,
    TraceContext,
    EntropyBudget,
    ToolEnvelope,
    validate_fail_closed,
    calculate_entropy_budget,
    generate_trace_context,
    determine_human_marker,
    DOMAIN_PAYLOAD_GATES,
    check_domain_gate,
    AAA_PUBLIC_TOOLS,
    AAA_CANONICAL_TOOLS,
    REQUIRES_SESSION,
    READ_ONLY_TOOLS,
    AAA_TOOL_STAGE_MAP,
    TRINITY_BY_TOOL,
    AAA_TOOL_ALIASES,
    TOOL_MODES,
    AAA_TOOL_LAW_BINDINGS,
    LAW_13_CATALOG,
    require_session,
    public_tool_input_contracts,
    verify_contract,
    __all__,
)

__all__ = [
    "ToolStatus",
    "OutputPolicy",
    "VerdictScope",
    "RiskTier",
    "HumanDecisionMarker",
    "SessionClass",
    "TraceContext",
    "EntropyBudget",
    "ToolEnvelope",
    "validate_fail_closed",
    "calculate_entropy_budget",
    "generate_trace_context",
    "determine_human_marker",
    "DOMAIN_PAYLOAD_GATES",
    "check_domain_gate",
    "AAA_PUBLIC_TOOLS",
    "AAA_CANONICAL_TOOLS",
    "REQUIRES_SESSION",
    "READ_ONLY_TOOLS",
    "AAA_TOOL_STAGE_MAP",
    "TRINITY_BY_TOOL",
    "AAA_TOOL_ALIASES",
    "TOOL_MODES",
    "AAA_TOOL_LAW_BINDINGS",
    "LAW_13_CATALOG",
    "require_session",
    "public_tool_input_contracts",
    "verify_contract",
]

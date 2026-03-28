from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal


# -----------------------------------------------------------------------------
# 11 CANONICAL MEGA-TOOLS (PUBLIC SURFACE TARGET)
# -----------------------------------------------------------------------------
from .runtime.tool_specs import MEGA_TOOLS, MegaToolName


# -----------------------------------------------------------------------------
# MODE ENUMS (STRICT)
# -----------------------------------------------------------------------------
class InitAnchorMode(str, Enum):
    init = "init"
    revoke = "revoke"
    refresh = "refresh"
    state = "state"
    status = "status"


class KernelMode(str, Enum):
    kernel = "kernel"
    status = "status"


class ApexSoulMode(str, Enum):
    judge = "judge"
    rules = "rules"
    validate = "validate"
    hold = "hold"
    armor = "armor"
    notify = "notify"
    probe = "probe"


class VaultLedgerMode(str, Enum):
    seal = "seal"
    verify = "verify"


class AgiMindMode(str, Enum):
    reason = "reason"
    reflect = "reflect"
    forge = "forge"


class AsiHeartMode(str, Enum):
    critique = "critique"
    simulate = "simulate"


class EngineeringMemoryMode(str, Enum):
    engineer = "engineer"
    query = "query"
    recall = "recall"
    write = "write"
    generate = "generate"


class PhysicsRealityMode(str, Enum):
    search = "search"
    ingest = "ingest"
    compass = "compass"
    atlas = "atlas"


class MathEstimatorMode(str, Enum):
    cost = "cost"
    health = "health"
    vitals = "vitals"


class CodeEngineMode(str, Enum):
    fs = "fs"
    process = "process"
    net = "net"
    tail = "tail"
    replay = "replay"


class ArchitectRegistryMode(str, Enum):
    register = "register"
    list = "list"
    read = "read"


MEGA_TOOL_MODES: dict[MegaToolName, set[str]] = {
    "init_anchor": {m.value for m in InitAnchorMode},
    "arifOS_kernel": {m.value for m in KernelMode},
    "apex_soul": {m.value for m in ApexSoulMode},
    "vault_ledger": {m.value for m in VaultLedgerMode},
    "agi_mind": {m.value for m in AgiMindMode},
    "asi_heart": {m.value for m in AsiHeartMode},
    "engineering_memory": {m.value for m in EngineeringMemoryMode},
    "physics_reality": {m.value for m in PhysicsRealityMode},
    "math_estimator": {m.value for m in MathEstimatorMode},
    "code_engine": {m.value for m in CodeEngineMode},
    "architect_registry": {m.value for m in ArchitectRegistryMode},
}


# -----------------------------------------------------------------------------
# LEGACY TOOL SURFACE (MUST BE 100% COVERED)
# -----------------------------------------------------------------------------
LEGACY_TOOLS: set[str] = {
    "init_anchor",
    "register_tools",
    "arifOS_kernel",
    "forge",
    "agi_reason",
    "agi_reflect",
    "reality_compass",
    "reality_atlas",
    "search_reality",
    "ingest_evidence",
    "asi_critique",
    "asi_simulate",
    "agentzero_engineer",
    "agentzero_memory_query",
    "apex_judge",
    "agentzero_validate",
    "audit_rules",
    "agentzero_armor_scan",
    "agentzero_hold_check",
    "check_vital",
    "open_apex_dashboard",
    "vault_seal",
    "verify_vault_ledger",
    "system_health",
    "fs_inspect",
    "process_list",
    "net_status",
    "log_tail",
    "cost_estimator",
    "chroma_query",
    "trace_replay",
    "list_resources",
    "read_resource",
    "arifos_list_resources",
    "arifos_read_resource",
    "metabolic_loop",
    "metabolic_loop_router",
    "apex_score_app",
    "stage_pipeline_app",
}


# -----------------------------------------------------------------------------
# CAPABILITY MAP (legacy tool -> mega_tool + mode)
# -----------------------------------------------------------------------------
@dataclass(frozen=True)
class CapabilityTarget:
    mega_tool: MegaToolName
    mode: str
    note: str = ""


CAPABILITY_MAP: dict[str, CapabilityTarget] = {
    # ---- Governance / Bootstrap (000_INIT) ----
    "init_anchor": CapabilityTarget("init_anchor", "init", "Canonical init"),
    "arifOS_kernel": CapabilityTarget("arifOS_kernel", "kernel", "Canonical router"),
    "metabolic_loop": CapabilityTarget("arifOS_kernel", "kernel", "Legacy compatibility"),
    # ---- AGI (333/555) ----
    "agi_reason": CapabilityTarget("agi_mind", "reason", "Reasoning"),
    "agi_reflect": CapabilityTarget("agi_mind", "reflect", "Reflection"),
    "forge": CapabilityTarget("agi_mind", "forge", "Forge"),
    # ---- ASI (666) ----
    "asi_critique": CapabilityTarget("asi_heart", "critique", "Adversarial critique"),
    "asi_simulate": CapabilityTarget("asi_heart", "simulate", "Consequence simulation"),
    # ---- Reality / Physics (111/222) ----
    "search_reality": CapabilityTarget("physics_reality", "search", "External search"),
    "ingest_evidence": CapabilityTarget("physics_reality", "ingest", "URL/file -> evidence"),
    "reality_compass": CapabilityTarget("physics_reality", "compass", "Quick grounding"),
    "reality_atlas": CapabilityTarget("physics_reality", "atlas", "Evidence merge"),
    # ---- Math / telemetry (444) ----
    "check_vital": CapabilityTarget("math_estimator", "vitals", "Thermo vitals"),
    "system_health": CapabilityTarget("math_estimator", "health", "Host health metrics"),
    "cost_estimator": CapabilityTarget("math_estimator", "cost", "Cost estimator"),
    # ---- Code / machine ops (M-3) ----
    "fs_inspect": CapabilityTarget("code_engine", "fs", "Filesystem inspection"),
    "process_list": CapabilityTarget("code_engine", "process", "Process listing"),
    "net_status": CapabilityTarget("code_engine", "net", "Network status"),
    "log_tail": CapabilityTarget("code_engine", "tail", "Log tail"),
    "trace_replay": CapabilityTarget("code_engine", "replay", "Replay traces"),
    # ---- Engineering + memory (555/666) ----
    "agentzero_engineer": CapabilityTarget("engineering_memory", "engineer", "Material execution"),
    "agentzero_memory_query": CapabilityTarget("engineering_memory", "query", "Recall memory"),
    "chroma_query": CapabilityTarget("engineering_memory", "query", "Vector query"),
    # ---- APEX / governance (888) ----
    "apex_judge": CapabilityTarget("apex_soul", "judge", "Verdict"),
    "audit_rules": CapabilityTarget("apex_soul", "rules", "Inspect floors"),
    "agentzero_validate": CapabilityTarget("apex_soul", "validate", "Validator"),
    "agentzero_hold_check": CapabilityTarget("apex_soul", "hold", "Hold status"),
    "agentzero_armor_scan": CapabilityTarget("apex_soul", "armor", "Injection scan"),
    "open_apex_dashboard": CapabilityTarget("apex_soul", "rules", "Dashboard"),
    "apex_score_app": CapabilityTarget("apex_soul", "rules", "Score UI"),
    "stage_pipeline_app": CapabilityTarget("apex_soul", "rules", "Pipeline UI"),
    # ---- Vault (999) ----
    "vault_seal": CapabilityTarget("vault_ledger", "seal", "Seal ledger"),
    "verify_vault_ledger": CapabilityTarget("vault_ledger", "verify", "Verify ledger"),
}


def iter_unmapped_legacy_tools() -> list[str]:
    """Legacy tools missing from CAPABILITY_MAP."""
    return sorted([t for t in LEGACY_TOOLS if t not in CAPABILITY_MAP])


def iter_unknown_tools_in_map() -> list[str]:
    """CAPABILITY_MAP entries not present in LEGACY_TOOLS (typo guard)."""
    return sorted([t for t in CAPABILITY_MAP.keys() if t not in LEGACY_TOOLS])


def iter_invalid_megatool_targets() -> list[str]:
    allowed = set(MEGA_TOOLS)
    bad: list[str] = []
    for legacy, tgt in CAPABILITY_MAP.items():
        if tgt.mega_tool not in allowed:
            bad.append(f"{legacy} -> {tgt.mega_tool}:{tgt.mode}")
    return sorted(bad)


def iter_invalid_modes() -> list[str]:
    bad: list[str] = []
    for legacy, tgt in CAPABILITY_MAP.items():
        allowed_modes = MEGA_TOOL_MODES.get(tgt.mega_tool, set())
        if tgt.mode not in allowed_modes:
            bad.append(f"{legacy} -> {tgt.mega_tool}:{tgt.mode}")
    return sorted(bad)

CAPABILITY_MAP.update({
    "arifos_list_resources": CapabilityTarget("engineering_memory", "query", "fallback"),
    "arifos_read_resource": CapabilityTarget("engineering_memory", "query", "fallback"),
    "list_resources": CapabilityTarget("engineering_memory", "query", "fallback"),
    "metabolic_loop_router": CapabilityTarget("arifOS_kernel", "kernel", "fallback"),
    "read_resource": CapabilityTarget("engineering_memory", "query", "fallback"),
    "register_tools": CapabilityTarget("arifOS_kernel", "kernel", "fallback"),
})

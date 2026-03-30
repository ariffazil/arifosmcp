from dataclasses import dataclass
from typing import Any, Literal


@dataclass(frozen=True)
class ToolSpec:
    name: str
    stage: str
    role: str
    layer: str
    description: str
    trinity: str
    floors: tuple[str, ...]
    input_schema: dict[str, Any]
    default_budget_tier: str = "medium"
    min_budget_tier: str = "micro"
    max_budget_tier: str = "large"
    overflow_policy: str = "truncate"
    readonly: bool = True


@dataclass(frozen=True)
class ResourceSpec:
    uri: str
    name: str
    description: str
    mime_type: str = "application/json"
    # Unified flag for resource templates
    is_template: bool = False


@dataclass(frozen=True)
class PromptSpec:
    name: str
    description: str
    arguments: list[dict[str, Any]] = None


MegaToolName = Literal[
    "init_anchor",
    "arifOS_kernel",
    "apex_soul",
    "vault_ledger",
    "agi_mind",
    "asi_heart",
    "engineering_memory",
    "physics_reality",
    "math_estimator",
    "code_engine",
    "architect_registry",
    "compat_probe",
]

MEGA_TOOLS: tuple[str, ...] = (
    "init_anchor",
    "arifOS_kernel",
    "apex_soul",
    "vault_ledger",
    "agi_mind",
    "asi_heart",
    "engineering_memory",
    "physics_reality",
    "math_estimator",
    "code_engine",
    "architect_registry",
    "compat_probe",
)


def _build_mega_schema(
    tool_name: str,
    modes: list[str],
    payload_properties: dict[str, Any],
    required_payload: list[str] = None,
) -> dict[str, Any]:
    """Helper to build the unified request envelope schema for a mega-tool."""
    return {
        "type": "object",
        "additionalProperties": True,
        "required": ["mode", "payload"],
        "properties": {
            "mode": {
                "type": "string",
                "description": f"Mode selector for {tool_name}.",
                "enum": modes,
            },
            "payload": {
                "type": "object",
                "description": "Mode-specific payload.",
                "required": required_payload or [],
                "properties": payload_properties,
                "additionalProperties": True,
            },
            "auth_context": {
                "type": ["object", "null"],
                "description": "Optional auth context for continuity (F11) and sovereignty (F13).",
                "additionalProperties": True,
            },
            "caller_context": {
                "type": ["object", "null"],
                "description": "Optional caller metadata.",
                "additionalProperties": True,
            },
            "risk_tier": {
                "type": "string",
                "description": "Requested risk posture.",
                "enum": ["low", "medium", "high", "critical"],
                "default": "medium",
            },
            "dry_run": {
                "type": "boolean",
                "description": "If true, compute/plan/validate only.",
                "default": True,
            },
            "allow_execution": {
                "type": "boolean",
                "description": "If true, execution is permitted IF floors pass.",
                "default": False,
            },
            "debug": {
                "type": "boolean",
                "description": "Include additional diagnostics.",
                "default": False,
            },
            "request_id": {
                "type": "string",
                "description": "Client trace ID.",
                "minLength": 8,
                "maxLength": 128,
            },
            "timestamp": {
                "type": "string",
                "description": "ISO 8601 timestamp.",
                "format": "date-time",
            },
        },
    }


PUBLIC_TOOL_SPECS: tuple[ToolSpec, ...] = (
    # ─── ⚖️ GOVERNANCE LAYER (G-1 to G-4) ───
    ToolSpec(
        name="init_anchor",
        stage="000_INIT",
        role="Constitutional Airlock",
        layer="GOVERNANCE",
        description=(
            "🔥 THE IGNITION STATE OF INTELLIGENCE (Unified). "
            "ONE tool for ALL constitutional session operations. "
            "Modes: 'init' (establish identity), 'state' (forensic audit), "
            "'status' (bootstrap diagnostics), 'revoke' (kill session), 'refresh' (rotate token)."
        ),
        trinity="PSI Ψ",
        floors=("F11", "F12", "F13"),
        input_schema=_build_mega_schema(
            "init_anchor",
            ["init", "revoke", "refresh", "state", "status"],
            {
                "actor_id": {"type": "string", "minLength": 2, "maxLength": 64},
                "model_soul": {
                    "type": "object",
                    "description": "Deep identity and behavioral contract (V2).",
                    "properties": {
                        "base_identity": {
                            "type": "object",
                            "properties": {
                                "provider": {"type": "string"},
                                "model_family": {"type": "string"},
                                "model_variant": {"type": "string"},
                                "runtime_class": {"type": "string"},
                            },
                        },
                        "runtime_state": {
                            "type": "object",
                            "properties": {
                                "tooling": {"type": "array", "items": {"type": "string"}},
                                "web_access": {"type": "boolean"},
                                "memory_mode": {"type": "string"},
                            },
                        },
                        "capability_map": {
                            "type": "object",
                            "additionalProperties": {"type": "boolean"},
                        },
                        "boundary_map": {
                            "type": "object",
                            "properties": {
                                "identity_claim_policy": {"type": "string"},
                                "tool_claim_policy": {"type": "string"},
                            },
                        },
                        "constitution": {
                            "type": "object",
                            "properties": {
                                "truth_policy": {"type": "string"},
                                "humility_policy": {"type": "string"},
                                "anti_hantu_policy": {"type": "string"},
                            },
                        },
                    },
                },
                "intent": {
                    "oneOf": [
                        {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 20000,
                            "description": "Legacy string format (auto-normalized to structured object)",
                        },
                        {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "minLength": 1, "maxLength": 20000},
                                "task_type": {
                                    "type": "string",
                                    "maxLength": 64,
                                    "enum": [
                                        "general",
                                        "ask",
                                        "audit",
                                        "design",
                                        "decide",
                                        "analyze",
                                        "execute",
                                    ],
                                    "default": "general",
                                },
                                "domain": {"type": "string", "maxLength": 64},
                                "desired_output": {
                                    "type": "string",
                                    "maxLength": 64,
                                    "enum": [
                                        "text",
                                        "json",
                                        "table",
                                        "code",
                                        "report",
                                        "decision",
                                        "mixed",
                                    ],
                                },
                                "reversibility": {
                                    "type": "string",
                                    "enum": ["reversible", "irreversible", "auditable"],
                                    "default": "auditable",
                                },
                            },
                            "required": ["query"],
                            "description": "Structured intent object with query, task_type, domain, desired_output, reversibility",
                        },
                    ],
                    "description": "User intent - accepts string (legacy) or structured object (preferred for governance)",
                },
                "declared_name": {"type": "string", "maxLength": 64},
                "session_id": {"type": "string", "minLength": 8, "maxLength": 128},
                "reason": {"type": "string", "maxLength": 1000},
                "human_approval": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether human has pre-approved this action (F13 Sovereign override)",
                },
            },
        ),
        default_budget_tier="small",
    ),
    ToolSpec(
        name="arifOS_kernel",
        stage="444_ROUTER",
        role="Stage Conductor",
        layer="GOVERNANCE",
        description=(
            "444_ROUTER: Primary metabolic conductor. Processes complex queries through "
            "the 000-999 pipe. Modes: 'kernel' (reasoning), 'status' (vitals)."
        ),
        trinity="DELTA/PSI",
        floors=("F4", "F11"),
        input_schema=_build_mega_schema(
            "arifOS_kernel",
            ["kernel", "status"],
            {
                "query": {"type": "string", "minLength": 1, "maxLength": 40000},
                "intent": {
                    "oneOf": [
                        {"type": "string"},
                        {
                            "type": "object",
                            "properties": {"query": {"type": "string"}},
                            "required": ["query"],
                        },
                    ],
                    "description": "Structured intent for governed reasoning.",
                },
                "context": {"type": "string", "maxLength": 100000},
                "max_steps": {"type": "integer", "minimum": 1, "maximum": 50, "default": 13},
                "session_id": {"type": "string"},
                "detail": {"type": "string", "enum": ["brief", "full"], "default": "full"},
            },
        ),
    ),
    ToolSpec(
        name="apex_soul",
        stage="888_JUDGE",
        role="Constitutional Verdict",
        layer="GOVERNANCE",
        description=(
            "888_JUDGE: Final authority for verdicts and defense. "
            "Modes: 'judge', 'rules', 'validate', 'hold', 'armor', 'notify', 'probe' (test floors)."
        ),
        trinity="PSI Ψ",
        floors=("F3", "F12", "F13"),
        input_schema=_build_mega_schema(
            "apex_soul",
            ["judge", "rules", "validate", "hold", "armor", "notify", "probe"],
            {
                "candidate": {"type": "string"},
                "hold_id": {"type": "string"},
                "message": {"type": "string"},
                "session_id": {"type": "string"},
                "target_floor": {
                    "type": "string",
                    "description": "Specific floor to probe (e.g. 'F12').",
                },
            },
        ),
    ),
    ToolSpec(
        name="vault_ledger",
        stage="999_VAULT",
        role="Immutable Memory",
        layer="GOVERNANCE",
        description=(
            "999_VAULT: Permanent decision recording and integrity. Modes: 'seal', 'verify'."
        ),
        trinity="PSI Ψ",
        floors=("F1", "F13"),
        input_schema=_build_mega_schema(
            "vault_ledger",
            ["seal", "verify"],
            {
                "verdict": {"type": "string"},
                "evidence": {"type": "string"},
                "full_scan": {"type": "boolean", "default": True},
                "session_id": {"type": "string"},
            },
        ),
    ),
    # ─── 🧠 INTELLIGENCE LAYER (I-1 to I-3) ───
    ToolSpec(
        name="agi_mind",
        stage="333_MIND",
        role="Logic & Synthesis",
        layer="INTELLIGENCE",
        description=(
            "333_MIND: Core reasoning and synthesis engine. Modes: 'reason', 'reflect', 'forge'."
        ),
        trinity="DELTA Δ",
        floors=("F2", "F4", "F7", "F8"),
        input_schema=_build_mega_schema(
            "agi_mind",
            ["reason", "reflect", "forge"],
            {
                "query": {"type": "string"},
                "topic": {"type": "string"},
                "session_id": {"type": "string"},
            },
            required_payload=["query"],
        ),
    ),
    ToolSpec(
        name="asi_heart",
        stage="666_HEART",
        role="Ethics & Simulation",
        layer="INTELLIGENCE",
        description=(
            "666_HEART: Safety, empathy, and consequence modeling. Modes: 'critique', 'simulate'."
        ),
        trinity="OMEGA Ω",
        floors=("F5", "F6", "F9"),
        input_schema=_build_mega_schema(
            "asi_heart",
            ["critique", "simulate"],
            {"content": {"type": "string"}, "session_id": {"type": "string"}},
            required_payload=["content"],
        ),
    ),
    ToolSpec(
        name="engineering_memory",
        stage="555_MEMORY",
        role="Technical Execution",
        layer="INTELLIGENCE",
        description=(
            "555_MEMORY: Governed autonomous engineering and vector memory. "
            "Modes: 'engineer' (execute), 'vector_query' (search), 'vector_store' (save), "
            "'vector_forget' (delete), 'generate' (create). "
            "Constitutional: F10/F2 verification on all vector queries."
        ),
        trinity="OMEGA Ω",
        floors=("F10", "F11", "F2"),
        input_schema=_build_mega_schema(
            "engineering_memory",
            ["engineer", "vector_query", "vector_store", "vector_forget", "generate", "query"],
            {
                "task": {"type": "string"},
                "query": {"type": "string"},
                "prompt": {"type": "string"},
                "content": {"type": "string"},
                "session_id": {"type": "string"},
            },
        ),
    ),
    # ─── ⚙️ MACHINE LAYER (M-1 to M-4) ───
    ToolSpec(
        name="physics_reality",
        stage="111_SENSE",
        role="Environmental Grounding",
        layer="MACHINE",
        description="111_SENSE: Earth-Witness fact acquisition and mapping. Modes: 'search', 'ingest', 'compass', 'atlas', 'time' (temporal intelligence — current UTC+KL datetime, weekday, quarter).",
        trinity="DELTA Δ",
        floors=("F2", "F3", "F10"),
        input_schema=_build_mega_schema(
            "physics_reality",
            ["search", "ingest", "compass", "atlas", "time"],
            {
                "input": {"type": "string"},
                "operation": {"type": "string"},
                "session_id": {"type": "string"},
                "top_k": {"type": "integer", "default": 5},
            },
        ),
    ),
    ToolSpec(
        name="math_estimator",
        stage="444_ROUTER",
        role="Thermodynamic Vitals",
        layer="MACHINE",
        description=(
            "Quantitative health and metabolic estimation. Modes: 'cost', 'health', 'vitals'."
        ),
        trinity="DELTA Δ",
        floors=("F4", "F5"),
        input_schema=_build_mega_schema(
            "math_estimator",
            ["cost", "health", "vitals"],
            {"action": {"type": "string"}, "session_id": {"type": "string"}},
        ),
    ),
    ToolSpec(
        name="code_engine",
        stage="M-3_EXEC",
        role="Computational Execution",
        layer="MACHINE",
        description=(
            "System-level hygiene and observation. Modes: 'fs', 'process', 'net', 'tail', 'replay'."
        ),
        trinity="ALL",
        floors=("F1",),
        input_schema=_build_mega_schema(
            "code_engine",
            ["fs", "process", "net", "tail", "replay"],
            {
                "path": {"type": "string", "default": "."},
                "limit": {"type": "integer", "default": 50},
                "session_id": {"type": "string"},
            },
        ),
    ),
    ToolSpec(
        name="architect_registry",
        stage="M-4_ARCH",
        role="System Definition",
        layer="MACHINE",
        description="Tool and resource discovery. Modes: 'register', 'list', 'read'.",
        trinity="DELTA Δ",
        floors=("F10",),
        input_schema=_build_mega_schema(
            "architect_registry",
            ["register", "list", "read"],
            {"uri": {"type": "string"}, "session_id": {"type": "string"}},
        ),
    ),
    ToolSpec(
        name="compat_probe",
        stage="M-5_COMPAT",
        role="Interoperability Audit",
        layer="MACHINE",
        description="Verify session portability and enum compatibility between layers. Modes: 'audit', 'probe', 'ping'.",
        trinity="ALL",
        floors=("F11", "F4"),
        input_schema=_build_mega_schema(
            "compat_probe",
            ["audit", "probe", "ping"],
            {"session_id": {"type": "string"}},
        ),
    ),
)

PUBLIC_RESOURCE_SPECS: tuple[ResourceSpec, ...] = (
    ResourceSpec(
        uri="about://arifos",
        name="About arifOS",
        description="High-level overview of the arifOS Constitutional Governance system.",
    ),
    ResourceSpec(
        uri="canon://floors",
        name="Constitutional Floors",
        description="Detailed specification of the 13 Constitutional Floors (F1-F13).",
    ),
    ResourceSpec(
        uri="canon://contracts",
        name="Tool Contracts",
        description="Functional and safety contracts for the 11 Mega-Tools.",
    ),
    ResourceSpec(
        uri="canon://states",
        name="State Ladder",
        description="Forensic session state progression: anonymous -> claimed -> anchored -> verified -> scoped -> approved.",
    ),
    ResourceSpec(
        uri="arifos://governance/floors",
        name="Constitutional Doctrine",
        description="Immutable thresholds and legal doctrine for the 13 Floors.",
    ),
    ResourceSpec(
        uri="arifos://status/vitals",
        name="System Vitals",
        description="Real-time thermodynamic and metabolic health of the kernel.",
    ),
    ResourceSpec(
        uri="arifos://bootstrap/guide",
        name="Bootstrap Guide",
        description="Step-by-step sequence for establishing a governed session.",
    ),
    ResourceSpec(
        uri="arifos://agents/skills",
        name="Agent Skills",
        description="Canonical registry of AI agent competencies and behaviors.",
    ),
    ResourceSpec(
        uri="arifos://caller/state",
        name="Caller State",
        description="Current session identity, authority level, and available next actions.",
    ),
    ResourceSpec(
        uri="arifos://sessions/{session_id}/vitals",
        name="Session Vitals",
        description="Dynamic vitals for a specific governed session.",
        is_template=True,
    ),
    ResourceSpec(
        uri="arifos://tools/{tool_name}/spec",
        name="Tool Specification",
        description="Dynamic contract and schema for a specific arifOS tool.",
        is_template=True,
    ),
    ResourceSpec(
        uri="arifos://floors/{floor_id}/doctrine",
        name="Floor Doctrine",
        description="Dynamic legal and physical doctrine for a specific floor.",
        is_template=True,
    ),
)

PUBLIC_PROMPT_SPECS: tuple[PromptSpec, ...] = (
    PromptSpec(name="init_anchor", description="Prompt for establishing a constitutional session."),
    PromptSpec(name="arifOS_kernel", description="Prompt for the primary metabolic conductor."),
    PromptSpec(
        name="agi_mind", description="Prompt for first-principles reasoning and reflection."
    ),
    PromptSpec(
        name="asi_heart", description="Prompt for ethical simulation and adversarial critique."
    ),
    PromptSpec(name="apex_soul", description="Prompt for sovereign judgment and safety auditing."),
    PromptSpec(name="vault_ledger", description="Prompt for immutable recording and verification."),
    PromptSpec(
        name="physics_reality", description="Prompt for grounding thoughts in the physical world."
    ),
    PromptSpec(
        name="code_engine", description="Prompt for OS-level hygiene and computational execution."
    ),
)

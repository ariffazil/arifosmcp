"""
arifosmcp/runtime/resources.py — arifOS Double Helix Resources

Peripheral Nervous System (PNS) organs and Constitutional Ring assets.
Exposes operational grounding, health, and invariants as dynamic resources.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import os
import json
from fastmcp import FastMCP
from fastmcp.tools import ToolResult
from .public_registry import (
    RUNTIME_ENVELOPE_SCHEMA,
    public_resource_uris,
    public_tool_specs,
    public_tool_input_schemas,
    release_version,
)


def apex_tools_html_rows() -> str:
    """Compatibility helper for legacy REST status pages."""
    rows: list[str] = []
    for spec in public_tool_specs():
        rows.append(
            f"<tr><td><span class='name'>{spec.name}</span></td>"
            f"<td class='role'>{spec.layer}</td>"
            f"<td class='role'>{spec.description}</td></tr>"
        )
    return "\n".join(rows)


def apex_tools_markdown_table() -> str:
    """Compatibility helper for markdown status summaries."""
    header = "| Tool Name | Layer | Role |\n|-----------|-------|------|"
    rows = [f"| {spec.name} | {spec.layer} | {spec.description} |" for spec in public_tool_specs()]
    return "\n".join([header, *rows])


# Registry of resource content functions - populated by register_resources
_resource_content_functions: dict[str, callable] = {}


def register_resources(mcp: FastMCP) -> None:
    """Wire the Double Helix resources (Inner Ring + PNS Outer Ring).

    Aligned with SPEC.md Section 6: Component Taxonomy
    """

    # --- SPEC.md SECTION 6.1: REQUIRED PUBLIC RESOURCES ---

    @mcp.resource("arifos://status/vitals")
    def arifos_vitals() -> str:
        """arifOS Status: Current health, capability map, degraded components."""
        from .public_registry import public_tool_names, release_version

        return json.dumps(
            {
                "server": "arifOSMCP",
                "version": release_version(),
                "motto": "DITEMPA BUKAN DIBERI",
                "protocol": "MCP-2025-11-25",
                "framework": "FastMCP-3.x",
                "status": "HEALTHY",
                "tools_available": len(public_tool_names()),
                "session_ladder": [
                    "anonymous",
                    "claimed",
                    "anchored",
                    "verified",
                    "scoped",
                    "approved",
                ],
                "diagnostics": {
                    "check_vital": "Available (no auth)",
                    "audit_rules": "Available (no auth)",
                },
            },
            ensure_ascii=False,
        )

    _resource_content_functions["arifos://status/vitals"] = arifos_vitals

    @mcp.resource("arifos://governance/floors")
    def arifos_floors() -> str:
        """arifOS Governance: Constitutional F1-F13 thresholds and doctrine."""
        return json.dumps(
            {
                "floors": {
                    "F1": {"name": "Amanah", "threshold": "LOCK", "type": "Hard", "engine": "ASI"},
                    "F2": {"name": "Truth", "threshold": "≥ 0.99", "type": "Hard", "engine": "AGI"},
                    "F3": {
                        "name": "Tri-Witness",
                        "threshold": "≥ 0.95",
                        "type": "Mirror",
                        "engine": "APEX",
                    },
                    "F4": {
                        "name": "ΔS Clarity",
                        "threshold": "≤ 0",
                        "type": "Hard",
                        "engine": "AGI",
                    },
                    "F5": {"name": "Peace²", "threshold": "≥ 1.0", "type": "Soft", "engine": "ASI"},
                    "F6": {
                        "name": "κᵣ Empathy",
                        "threshold": "≥ 0.70",
                        "type": "Soft",
                        "engine": "ASI",
                    },
                    "F7": {
                        "name": "Ω₀ Humility",
                        "threshold": "0.03-0.05",
                        "type": "Hard",
                        "engine": "AGI",
                    },
                    "F8": {
                        "name": "G Genius",
                        "threshold": "≥ 0.80",
                        "type": "Mirror",
                        "engine": "AGI",
                    },
                    "F9": {
                        "name": "C_dark",
                        "threshold": "< 0.30",
                        "type": "Derived",
                        "engine": "ASI",
                    },
                    "F10": {
                        "name": "Ontology",
                        "threshold": "LOCK",
                        "type": "Wall",
                        "engine": "APEX",
                    },
                    "F11": {
                        "name": "Command Auth",
                        "threshold": "LOCK",
                        "type": "Hard",
                        "engine": "ASI",
                    },
                    "F12": {
                        "name": "Injection",
                        "threshold": "< 0.85",
                        "type": "Wall",
                        "engine": "APEX",
                    },
                    "F13": {
                        "name": "Sovereign",
                        "threshold": "HUMAN",
                        "type": "Veto",
                        "engine": "APEX",
                    },
                },
                "execution_order": "F12→F11 → AGI (F1,F2,F4,F7) → ASI (F5,F6,F9,F13) → Mirrors (F3,F8) → Ledger",
                "hard_fail": "VOID",
                "soft_fail": "PARTIAL",
            },
            ensure_ascii=False,
        )

    _resource_content_functions["arifos://governance/floors"] = arifos_floors

    @mcp.resource("arifos://bootstrap/guide")
    def arifos_bootstrap_guide() -> str:
        """arifOS Bootstrap: Startup path, canonical sequence, example payloads."""
        return json.dumps(
            {
                "bootstrap_sequence": [
                    {
                        "step": 1,
                        "tool": "check_vital",
                        "state_required": "anonymous",
                        "auth_required": False,
                        "output": ["health", "capabilities", "degraded_components"],
                        "example": {"session_id": "global"},
                    },
                    {
                        "step": 2,
                        "tool": "audit_rules",
                        "state_required": "anonymous",
                        "auth_required": False,
                        "output": ["constitutional_floors", "doctrine_hooks"],
                        "example": {"session_id": "global"},
                    },
                    {
                        "step": 3,
                        "tool": "init_anchor",
                        "state_required": "anonymous_or_claimed",
                        "auth_required": False,
                        "input": ["actor_id", "declared_name", "intent"],
                        "output": ["anchored_session", "auth_context_seed"],
                        "example": {
                            "actor_id": "arif",
                            "declared_name": "Muhammad Arif",
                            "intent": {
                                "query": "testing kernel governance flow",
                                "task_type": "general",
                            },
                        },
                    },
                    {
                        "step": 4,
                        "tool": "arifOS_kernel",
                        "state_required": "anchored",
                        "auth_required": True,
                        "modes": ["inspect", "analyze", "recommend", "execute"],
                        "output": ["governed_execution_result"],
                        "example": {
                            "query": "analyze system health",
                            "risk_tier": "low",
                            "auth_context": {"session_id": "session-xxx", "actor_id": "arif"},
                        },
                    },
                ],
                "global_session_rule": "session_id='global' is diagnostics-only. No state changes allowed.",
                "recovery_rule": "Every blocked call returns: current_state, why_blocked, next_tool, required_args, example_payload, retry_safe",
            },
            ensure_ascii=False,
        )

    _resource_content_functions["arifos://bootstrap/guide"] = arifos_bootstrap_guide

    @mcp.resource("arifos://agents/skills")
    def arifos_agents_skills() -> str:
        """arifOS Agent Skills: Consolidated guide for AI agents using the 11 mega-tools."""
        # Dynamically read from root AGENTS.md
        root_agents_md = os.path.join(os.path.dirname(__file__), "..", "..", "AGENTS.md")
        if os.path.exists(root_agents_md):
            with open(root_agents_md, "r", encoding="utf-8") as f:
                return f.read()
        return "AGENTS.md not found in root. Please contact the 888_JUDGE."

    _resource_content_functions["arifos://agents/skills"] = arifos_agents_skills

    @mcp.resource("arifos://contracts/tools")
    def arifos_tool_contracts() -> str:
        """arifOS Contracts: Tool contract table with risk, auth, mutability."""
        from .public_registry import PUBLIC_TOOL_SPECS

        contracts = []
        for spec in PUBLIC_TOOL_SPECS:
            risk = "low"
            if any(f in ["F11", "F13"] for f in spec.floors):
                risk = "high"
            elif any(f in ["F1"] for f in spec.floors):
                risk = "critical"
            elif len(spec.floors) > 2:
                risk = "medium"

            contracts.append(
                {
                    "canonical_name": spec.name,
                    "stage": spec.stage,
                    "trinity": spec.trinity,
                    "risk_class": risk,
                    "auth_required": "F11" in spec.floors or "F13" in spec.floors,
                    "floors": list(spec.floors),
                }
            )
        return json.dumps({"contracts": contracts}, ensure_ascii=False)

    _resource_content_functions["arifos://contracts/tools"] = arifos_tool_contracts

    @mcp.resource("arifos://caller/state")
    def arifos_caller_state() -> str:
        """arifOS Caller State: Current state, allowed tools, blocked tools."""
        # This would be dynamic based on session - static for now
        return json.dumps(
            {
                "current_state": "anonymous",
                "verification_tier": "GUEST",
                "allowed_tools": ["check_vital", "audit_rules", "init_anchor"],
                "blocked_tools": ["arifOS_kernel", "verify_vault_ledger"],
                "next_step": {
                    "tool": "init_anchor",
                    "reason": "Identity required for governed execution",
                    "example": {
                        "actor_id": "your-name",
                        "declared_name": "Your Name",
                        "intent": {"query": "purpose of session", "task_type": "general"},
                    },
                },
                "session_ladder": {
                    "anonymous": {"allows": "diagnostics only", "exit": "claim identity"},
                    "claimed": {"allows": "diagnostics only", "exit": "create anchor"},
                    "anchored": {
                        "allows": "memory, evidence, kernel prep",
                        "exit": "cryptographic proof",
                    },
                    "verified": {"allows": "+ ledger verification", "exit": "scope grant"},
                    "scoped": {"allows": "+ low-risk kernel", "exit": "human escalation"},
                    "approved": {"allows": "+ high-risk, mutations", "exit": "completion"},
                },
            },
            ensure_ascii=False,
        )

    _resource_content_functions["arifos://caller/state"] = arifos_caller_state

    # --- LEGACY RESOURCES (Backward Compatibility) ---

    @mcp.resource("canon://invariants")
    def canon_invariants() -> str:
        """ΔΩΨ constitutional invariants and thermodynamic laws."""
        return json.dumps({"delta": "ΔS ≤ 0", "omega": "Ω₀ ∈ [0.03, 0.05]", "psi": "G ≥ 0.80"})

    _resource_content_functions["canon://invariants"] = canon_invariants

    @mcp.resource("canon://floors")
    def canon_floors() -> str:
        """Static F1-F13 constitutional floor thresholds and execution order reference."""
        return json.dumps(
            {
                "structure": "9 Floors + 2 Mirrors + 2 Walls = 13 LAWS",
                "execution_order": "F12→F11 → AGI (F1,F2,F4,F7) → ASI (F5,F6,F9,F13) → Mirrors (F3,F8) → Ledger",
                "hard_fail": "VOID",
                "soft_fail": "PARTIAL",
                "floors": {
                    "F1": {
                        "name": "Amanah",
                        "threshold": "LOCK",
                        "type": "Hard",
                        "engine": "ASI",
                        "check": "Reversible? Within mandate?",
                    },
                    "F2": {
                        "name": "Truth",
                        "threshold": "≥ 0.99",
                        "type": "Hard",
                        "engine": "AGI",
                        "check": "Factually accurate?",
                    },
                    "F3": {
                        "name": "Tri-Witness",
                        "threshold": "≥ 0.95",
                        "type": "Mirror",
                        "engine": "APEX",
                        "check": "External calibration (Human·AI·Earth)",
                    },
                    "F4": {
                        "name": "ΔS Clarity",
                        "threshold": "≤ 0",
                        "type": "Hard",
                        "engine": "AGI",
                        "check": "Reduces confusion?",
                    },
                    "F5": {
                        "name": "Peace²",
                        "threshold": "≥ 1.0",
                        "type": "Soft",
                        "engine": "ASI",
                        "check": "Non-destructive?",
                    },
                    "F6": {
                        "name": "κᵣ Empathy",
                        "threshold": "≥ 0.70",
                        "type": "Soft",
                        "engine": "ASI",
                        "check": "Serves weakest stakeholder?",
                    },
                    "F7": {
                        "name": "Ω₀ Humility",
                        "threshold": "0.03-0.05",
                        "type": "Hard",
                        "engine": "AGI",
                        "check": "States uncertainty?",
                    },
                    "F8": {
                        "name": "G Genius",
                        "threshold": "≥ 0.80",
                        "type": "Mirror",
                        "engine": "AGI",
                        "check": "Internal coherence (AxPxXxE2)",
                    },
                    "F9": {
                        "name": "C_dark",
                        "threshold": "< 0.30",
                        "type": "Derived",
                        "engine": "ASI",
                        "check": "Dark cleverness contained?",
                    },
                    "F10": {
                        "name": "Ontology",
                        "threshold": "LOCK",
                        "type": "Wall",
                        "engine": "APEX",
                        "check": "No consciousness/soul claims",
                    },
                    "F11": {
                        "name": "Command Auth",
                        "threshold": "LOCK",
                        "type": "Hard",
                        "engine": "ASI",
                        "check": "Nonce-verified identity?",
                    },
                    "F12": {
                        "name": "Injection",
                        "threshold": "< 0.85",
                        "type": "Wall",
                        "engine": "APEX",
                        "check": "Block adversarial control",
                    },
                    "F13": {
                        "name": "Sovereign",
                        "threshold": "HUMAN",
                        "type": "Veto",
                        "engine": "APEX",
                        "check": "Human final authority?",
                    },
                },
            },
            ensure_ascii=False,
        )

    _resource_content_functions["canon://floors"] = canon_floors

    @mcp.resource("canon://contracts")
    def canon_contracts() -> str:
        """Tool Contract Table: Hierarchy, authority levels, and bootstrap requirements."""
        return """
# arifOS Tool Contract Table (v2026.03.14)

| Class                  | Tools                  | Auth Required | Anonymous OK? | Purpose |
|------------------------|------------------------|---------------|---------------|---------|
| **Read-only / Diag**   | check_vital, audit_rules| ❌ No         | ✅ Yes        | Assess health & capability |
| **Grounding / Sense**  | search_reality, ingest | ⚠️ Optional   | ✅ Yes        | External fact grounding |
| **Memory / Anchor**    | init_anchor             | ⚠️ Start Here | ✅ Yes        | Establish identity & session |
| **Verification**       | verify_vault_ledger    | ✅ Yes        | ❌ No         | Verify Merkle chain integrity |
| **Consequential**      | arifOS_kernel, forge   | ✅ Yes        | ❌ No         | Governed execution & actions |

## Transition Pathways
Review `canon://states` for the full Session Ladder and state transition requirements.

## Bootstrap Sequence
1. **check_vital**: Check system readiness and current state.
2. **audit_rules**: Inspect constitutional thresholds.
3. **init_anchor**: **MANDATORY** establishes your `auth_context`.
4. **arifOS_kernel**: Use the `auth_context` from step 3 to perform real work.
"""

    _resource_content_functions["canon://contracts"] = canon_contracts

    @mcp.resource("canon://states")
    def canon_states() -> str:
        """Session Ladder: State machine and transition requirements."""
        return """
# arifOS Session Ladder (State Machine)

| State        | Entry Condition           | Allowed Tools               | Exit Condition          |
|--------------|---------------------------|-----------------------------|-------------------------|
| **anonymous**| No identity claim         | diagnostics, read-only search| actor/name claim        |
| **claimed**  | Actor ID provided         | same as anonymous           | anchor created          |
| **anchored** | `init_anchor` succeeded   | memory, evidence, kernel prep| cryptographic proof     |
| **verified** | Proof accepted            | ledger verification         | scope grant             |
| **scoped**   | Approval scope granted    | low-risk kernel             | human escalation        |
| **approved** | Human escalation cleared  | high-risk kernel, mutations | completion/revocation   |

## Verification Status
- **GUEST**: `anonymous` or `claimed`. Passive observer.
- **OPERATOR**: `anchored` or `verified`. Governed participant.
- **APEX**: `scoped` or `approved`. Sovereign authority.
"""

    _resource_content_functions["canon://states"] = canon_states

    @mcp.resource("canon://index")
    def canon_index() -> str:
        """High-level arifOS canon map: tools, floors, and resources."""
        return json.dumps(
            {
                "version": release_version(),
                "motto": "DITEMPA BUKAN DIBERI",
                "architecture": "Double Helix",
                "authority_ladder": [
                    "anonymous",
                    "claimed",
                    "anchored",
                    "verified",
                    "scoped",
                    "approved",
                ],
                "resources": public_resource_uris(),
            },
            ensure_ascii=False,
        )

    _resource_content_functions["canon://index"] = canon_index

    @mcp.resource("arifos://sessions/{session_id}/vitals")
    def arifos_session_vitals(session_id: str) -> str:
        """arifOS Session Vitals: Real-time telemetry for a specific session."""
        from arifosmcp.core.physics.thermodynamics_hardened import get_thermodynamic_report

        try:
            report = get_thermodynamic_report(session_id)
            return json.dumps({"session_id": session_id, "vitals": report}, ensure_ascii=False)
        except Exception:
            return json.dumps({"session_id": session_id, "status": "UNKNOWN"}, ensure_ascii=False)

    _resource_content_functions["arifos://sessions/{session_id}/vitals"] = arifos_session_vitals

    @mcp.resource("arifos://tools/{tool_name}/spec")
    def arifos_tool_spec(tool_name: str) -> str:
        """arifOS Tool Specification: Detailed contract for a specific tool."""
        from .public_registry import get_tool_spec_by_name
        spec = get_tool_spec_by_name(tool_name)
        if spec:
            return json.dumps(spec.model_dump(), ensure_ascii=False)
        return json.dumps({"error": "Tool not found", "name": tool_name})

    _resource_content_functions["arifos://tools/{tool_name}/spec"] = arifos_tool_spec

    @mcp.resource("arifos://floors/{floor_id}/doctrine")
    def arifos_floor_doctrine(floor_id: str) -> str:
        """arifOS Floor Doctrine: The mathematical and legal basis for a constitutional floor."""
        from arifosmcp.core.shared.floors import get_floor_spec
        spec = get_floor_spec(floor_id)
        return json.dumps(spec, ensure_ascii=False)

    _resource_content_functions["arifos://floors/{floor_id}/doctrine"] = arifos_floor_doctrine

    @mcp.resource("schema://tools/input")
    def schema_tools_input() -> str:
        """Canonical JSON Schema input specs for public tools."""
        return json.dumps(public_tool_input_schemas(), ensure_ascii=False)

    _resource_content_functions["schema://tools/input"] = schema_tools_input

    @mcp.resource("schema://tools/output")
    def schema_tools_output() -> str:
        """Canonical RuntimeEnvelope output schema."""
        return json.dumps(RUNTIME_ENVELOPE_SCHEMA, ensure_ascii=False)

    _resource_content_functions["schema://tools/output"] = schema_tools_output


def manifest_resources() -> list[str]:
    """Return list of all registered resource URIs."""
    return public_resource_uris()


async def read_resource_content(uri: str) -> str | None:
    """Read resource content by URI (Hardened 9 support).

    Dispatches to registered resource functions for actual content.
    """
    if uri not in public_resource_uris():
        return None

    # Call the registered resource function for actual content
    if uri in _resource_content_functions:
        return _resource_content_functions[uri]()

    # Fallback for any URI in registry without registered function
    return None


def build_open_apex_dashboard_result(session_id: str = "global") -> ToolResult | None:
    """Return a ToolResult containing the APEX dashboard v2.1 redirect/HTML."""
    dashboard_path = os.path.join(
        os.path.dirname(__file__), "..", "sites", "dashboard", "index.html"
    )
    if os.path.exists(dashboard_path):
        with open(dashboard_path, "r", encoding="utf-8") as f:
            html = f.read()
        return ToolResult(content=[{"type": "text", "text": html}])
    return None

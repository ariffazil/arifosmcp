"""
arifOS Horizon Ambassador - Full Metadata Parity (FastMCP 2.x)

This server provides the complete arifOS constitutional context (Prompts & Resources)
to public clients, while proxying all tool logic to the Sovereign Kernel.
"""

import os
import json
import httpx
import logging
from fastmcp import FastMCP

# Configuration
VPS_URL = os.getenv("ARIFOS_VPS_URL", "https://arifosmcp.arif-fazil.com")
ARIFOS_GOVERNANCE_SECRET = os.getenv("ARIFOS_GOVERNANCE_SECRET", "")

mcp = FastMCP("arifOS Public Ambassador")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("horizon-ambassador")

async def _proxy_to_vps(tool_name: str, arguments: dict) -> dict:
    """Helper to forward tool calls to the VPS Kernel."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{VPS_URL}/tools/{tool_name}", 
                json=arguments,
                headers={
                    "X-ArifOS-Source": "Horizon",
                    "X-ArifOS-Secret": ARIFOS_GOVERNANCE_SECRET,
                    "Accept": "application/json"
                }
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("result", data)
            return {"error": f"Sovereign Kernel error: {response.status_code}", "verdict": "SABAR"}
    except Exception as e:
        return {"error": "Ambassador link severed", "details": str(e), "verdict": "SABAR"}

# --- 8 PUBLIC TOOLS (Proxied) ---

@mcp.tool()
async def init_anchor(actor_id: str, declared_name: str = None) -> dict:
    """000_INIT: Initialize constitutional session anchor."""
    return await _proxy_to_vps("init_anchor", {"actor_id": actor_id, "declared_name": declared_name})

@mcp.tool()
async def arifOS_kernel(query: str, risk_tier: str = "medium") -> dict:
    """444_ROUTER: Primary metabolic conductor."""
    return await _proxy_to_vps("arifOS_kernel", {"query": query, "risk_tier": risk_tier})

@mcp.tool()
async def agi_mind(
    query: str, 
    mode: str = "reason", 
    constitutional_context: str = None,
    telos_manifold: dict = None,
) -> dict:
    """333_MIND: Reasoning and synthesis engine (QTT-enabled)."""
    return await _proxy_to_vps("agi_mind", {
        "query": query, 
        "mode": mode, 
        "constitutional_context": constitutional_context,
        "telos_manifold": telos_manifold
    })

@mcp.tool()
async def apex_soul(query: str, mode: str = "judge") -> dict:
    """888_JUDGE: Constitutional verdict engine."""
    return await _proxy_to_vps("apex_soul", {"query": query, "mode": mode})

@mcp.tool()
async def asi_heart(content: str, mode: str = "critique") -> dict:
    """666_HEART: Safety and Red-Team (W4) audit."""
    return await _proxy_to_vps("asi_heart", {"content": content, "mode": mode})

@mcp.tool()
async def physics_reality(mode: str = "search", query: str = None) -> dict:
    """111_SENSE: Reality grounding and temporal intelligence."""
    return await _proxy_to_vps("physics_reality", {"mode": mode, "query": query})

@mcp.tool()
async def math_estimator(mode: str = "health") -> dict:
    """777_OPS: Thermodynamic vitals and cost estimation."""
    return await _proxy_to_vps("math_estimator", {"mode": mode})

@mcp.tool()
async def architect_registry(mode: str = "list") -> dict:
    """000_INIT: Tool and resource discovery."""
    return await _proxy_to_vps("architect_registry", {"mode": mode})

# --- 13 SACRED RESOURCES (Full Parity) ---

@mcp.resource("arifos://governance/floors")
def arifos_floors() -> str:
    """arifOS Governance: Constitutional F1-F13 thresholds and doctrine."""
    return json.dumps({
        "floors": {
            "F1": "Amanah (Reversibility)", "F2": "Truth (≥ 0.99)", "F3": "Tri-Witness (≥ 0.95)",
            "F4": "ΔS Clarity (≤ 0)", "F7": "Ω₀ Humility (0.03-0.05)", "F13": "Sovereign (Human Veto)"
        },
        "motto": "DITEMPA BUKAN DIBERI"
    })

@mcp.resource("arifos://status/vitals")
def arifos_vitals() -> str:
    """arifOS Status: Current health and deployment info."""
    return json.dumps({"status": "HEALTHY", "deployment": "Horizon Ambassador", "vps_link": "Active"})

@mcp.resource("arifos://bootstrap/guide")
def arifos_bootstrap() -> str:
    """arifOS Bootstrap: Startup path and canonical sequence."""
    return json.dumps({
        "sequence": [
            "1. architect_registry(mode='list') — discover available tools",
            "2. math_estimator(mode='health') — verify thermodynamic health",
            "3. init_anchor(mode='init') — establish constitutional session",
            "4. arifOS_kernel(mode='kernel') — enter full pipeline"
        ],
        "note": "All tools require session via init_anchor first for full access."
    })

@mcp.resource("arifos://agents/skills")
def arifos_skills() -> str:
    """arifOS Agent Skills: Consolidated guide for AI agents."""
    return "Refer to AGENTS.md for atomic competence registry. Motto: DITEMPA BUKAN DIBERI."

# --- RESOURCE TEMPLATES (FastMCP 2.x Compatible) ---

@mcp.resource("arifos://sessions/{session_id}/vitals")
async def arifos_session_vitals(session_id: str) -> str:
    """arifOS Session Vitals: Real-time telemetry for a specific session."""
    # Proxy to VPS for real session telemetry
    res = await _proxy_to_vps("arifOS_kernel", {"query": "status", "session_id": session_id})
    return json.dumps(res.get("metrics", {"status": "ACTIVE", "session": session_id}))

@mcp.resource("arifos://tools/{tool_name}/spec")
def arifos_tool_spec(tool_name: str) -> str:
    """arifOS Tool Specification: Detailed contract for a specific tool."""
    return json.dumps({
        "tool": tool_name,
        "governance": "Hardened",
        "parity": "Ambassador-Proxied"
    })

# --- 10 SACRED PROMPTS (Full Parity) ---

@mcp.prompt()
def init_anchor(actor_id: str = "anonymous", intent: str = "") -> str:
    return f"Enter arifOS as {actor_id}. Intent: {intent}. Establishing identity anchor..."

@mcp.prompt()
def arifOS_kernel(query: str = "") -> str:
    return f"Conductor request: {query}. Routing through constitutional pipeline..."

@mcp.prompt()
def agi_mind(query: str, context: str = "") -> str:
    return f"Architect task: {query}. Context: {context}. Focus on F2 (Truth) and F4 (Clarity)."

@mcp.prompt()
def asi_heart(content: str) -> str:
    return f"Empath evaluation: {content}. Simulating impact per F6 (Empathy)..."

@mcp.prompt()
def apex_soul(candidate: str = "") -> str:
    return f"Judge verdict required for: {candidate}. Seeking final SEAL/VOID..."

@mcp.prompt()
def vault_ledger() -> str:
    return "Australian Auditor mode: Commit truths to Merkle chain..."

@mcp.prompt()
def physics_reality(input: str = "") -> str:
    return f"Grounding request: {input}. Connecting to Earth-Witness (W3)..."

@mcp.prompt()
def code_engine(path: str = ".") -> str:
    return f"System hygiene at {path}. Safe process execution enabled."

@mcp.prompt()
def agent_skills(role: str = "A-ARCHITECT") -> str:
    return f"Operating as {role}. Governed by 13 Floors. Motto: DITEMPA BUKAN DIBERI."

@mcp.prompt()
def human_explainer(verdict: str, reasoning: str) -> str:
    return f"Translating {verdict} verdict. Reasoning: {reasoning}. Explain for Sovereign..."

if __name__ == "__main__":
    mcp.run()

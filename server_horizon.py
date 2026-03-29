"""
arifOS Horizon Ambassador - Hybrid Entrypoint (FastMCP 2.x Compatible)

This entrypoint is designed specifically for Prefect Horizon. It proxies
all tool calls to the full arifOS Sovereign Kernel (3.x) running on your VPS.
"""

import os
import httpx
import logging
from fastmcp import FastMCP

# Configuration
# Default to your VPS URL.
VPS_URL = os.getenv("ARIFOS_VPS_URL", "https://arifosmcp.arif-fazil.com")
ARIFOS_GOVERNANCE_SECRET = os.getenv("ARIFOS_GOVERNANCE_SECRET", "")

# Create Ambassador (Strictly 2.x compatible)
mcp = FastMCP("arifOS Public Ambassador")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("horizon-ambassador")

async def _proxy_to_vps(tool_name: str, arguments: dict) -> dict:
    """Helper to forward tool calls to the VPS Kernel."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            logger.info(f"Proxying {tool_name} to {VPS_URL}...")
            
            # The arifOS Sovereign Kernel uses /tools/{name} for REST calls
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
                # Extract the nested 'result' field from arifOS REST response
                if isinstance(data, dict) and "result" in data:
                    return data["result"]
                return data
            else:
                return {
                    "error": f"Sovereign Kernel returned {response.status_code}",
                    "verdict": "SABAR",
                    "note": response.text[:200]
                }
    except Exception as e:
        logger.error(f"Ambassador link severed: {str(e)}")
        return {
            "error": "Ambassador link severed",
            "verdict": "SABAR",
            "details": str(e)
        }

@mcp.tool()
async def init_anchor(actor_id: str, declared_name: str = None) -> dict:
    """000_INIT: Initialize constitutional session anchor."""
    return await _proxy_to_vps("init_anchor", {"actor_id": actor_id, "declared_name": declared_name})

@mcp.tool()
async def arifOS_kernel(query: str, risk_tier: str = "medium") -> dict:
    """444_ROUTER: Primary metabolic conductor."""
    return await _proxy_to_vps("arifOS_kernel", {"query": query, "risk_tier": risk_tier})

@mcp.tool()
async def agi_mind(query: str, mode: str = "reason") -> dict:
    """333_MIND: Reasoning and synthesis engine (QTT-enabled)."""
    return await _proxy_to_vps("agi_mind", {"query": query, "mode": mode})

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

# --- RESOURCES (FastMCP 2.x Compatible) ---

@mcp.resource("arifos://governance/floors")
def arifos_floors() -> str:
    """arifOS Governance: Constitutional F1-F13 thresholds and doctrine."""
    return """{
        "floors": {
            "F1": {"name": "Amanah", "threshold": "LOCK", "type": "Hard"},
            "F2": {"name": "Truth", "threshold": ">= 0.99", "type": "Hard"},
            "F3": {"name": "Tri-Witness", "threshold": ">= 0.95", "type": "Mirror"},
            "F4": {"name": "Clarity", "threshold": "<= 0", "type": "Hard"},
            "F13": {"name": "Sovereign", "threshold": "HUMAN", "type": "Veto"}
        },
        "motto": "DITEMPA BUKAN DIBERI"
    }"""

@mcp.resource("arifos://status/vitals")
def arifos_vitals() -> str:
    """arifOS Status: Current health and deployment info."""
    return """{
        "status": "HEALTHY",
        "deployment": "Horizon Ambassador",
        "mode": "Proxy",
        "vps_link": "Active"
    }"""

# --- PROMPTS (FastMCP 2.x Compatible) ---

@mcp.prompt()
def init_anchor(actor_id: str = "anonymous", intent: str = "") -> str:
    """Prompt for initial identity establishment."""
    return f"Establish your constitutional identity as {actor_id}. Intent: {intent}."

@mcp.prompt()
def arifOS_kernel(query: str = "") -> str:
    """Prompt for full metabolic reasoning."""
    return f"Process this query through the arifOS kernel: {query}."

@mcp.prompt()
def agi_mind(query: str) -> str:
    """Prompt for first-principles reasoning."""
    return f"Analyze this using AGI first-principles: {query}. Focus on Truth and Clarity."

if __name__ == "__main__":
    mcp.run()

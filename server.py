"""
arifOS Sovereign Intelligence Kernel - Dual Sovereignty Entry Point

This file serves as the unified entry point for BOTH:
1. VPS Sovereign Kernel (primary) - https://arifos.arif-fazil.com
2. Horizon Public Ambassador (secondary) - https://arifos.fastmcp.app

Environment is auto-detected via ARIFOS_DEPLOYMENT env var.

Repository: https://github.com/ariffazil/arifOS
Documentation: https://arifos.arif-fazil.com
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from arifosmcp.runtime.server import mcp
from config.environments import (
    get_environment,
    is_sovereign,
    is_public,
    get_server_config,
)

# Detect environment
env = get_environment()

# Log deployment mode
print(f"🏛️ arifOS starting in {env.mode.value.upper()} mode")
print(f"   Name: {env.name}")
print(f"   URL: {env.base_url}")
print(f"   Constitutional Floors: {', '.join(env.constitutional_floors)}")

if is_sovereign():
    print("🔥 SOVEREIGN KERNEL: All F1-F13 floors enforced")
elif is_public():
    print("☁️  PUBLIC AMBASSADOR: Limited tool surface for public access")

# Export the FastMCP instance
__all__ = ["mcp"]

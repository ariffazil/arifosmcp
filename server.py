"""
arifOS MCP Server - Clean Entry Point for Horizon + VPS

Repository: https://github.com/ariffazil/arifosmcp
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the configured FastMCP instance
from arifosmcp.runtime.server import mcp

# Export for FastMCP Cloud / Horizon
__all__ = ["mcp"]

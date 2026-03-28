"""
arifOS MCP Server - Clean Entry Point for Horizon + VPS
Repository: https://github.com/ariffazil/arifosmcp
"""

import os
import sys

# CRITICAL: Add current directory to path BEFORE any imports
# This ensures arifosmcp package can be found in both VPS and Horizon deployments
_current_file = os.path.abspath(__file__)
_current_dir = os.path.dirname(_current_file)

# Add current dir (package root) to path
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

# Also add parent for absolute imports
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Create arifosmcp namespace if missing (Horizon compatibility)
if 'arifosmcp' not in sys.modules:
    import types
    arifosmcp_module = types.ModuleType('arifosmcp')
    arifosmcp_module.__path__ = [_current_dir]
    sys.modules['arifosmcp'] = arifosmcp_module

# Now safe to import
from arifosmcp.runtime.server import mcp

# Export for FastMCP Cloud / Horizon
__all__ = ["mcp"]

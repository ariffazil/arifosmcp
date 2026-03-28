"""
arifOS MCP Smart Gateway - Automatic Horizon/VPS Switcher
Repository: https://github.com/ariffazil/arifosmcp
"""

import os
import sys
import logging

# Configuration
IS_HORIZON = os.getenv("FASTMCP_CLOUD_URL") is not None or os.getenv("HORIZON_ENVIRONMENT") is not None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("arifos-gateway")

def setup_paths():
    """Ensure arifosmcp can be found in all environments."""
    _current_file = os.path.abspath(__file__)
    _current_dir = os.path.dirname(_current_file)
    if _current_dir not in sys.path:
        sys.path.insert(0, _current_dir)
    
    # Fake module for Horizon if needed
    if 'arifosmcp' not in sys.modules:
        import types
        mod = types.ModuleType('arifosmcp')
        mod.__path__ = [_current_dir]
        sys.modules['arifosmcp'] = mod

if IS_HORIZON:
    # -------------------------------------------------------------------------
    # HORIZON AMBASSADOR MODE (FastMCP 2.x Compatible Proxy)
    # -------------------------------------------------------------------------
    logger.info("BOOT: Detected Horizon environment. Starting Public Ambassador Proxy...")
    
    # We import the proxy logic from our dedicated file to avoid 3.x kernel imports
    setup_paths()
    from server_horizon import mcp
    
else:
    # -------------------------------------------------------------------------
    # VPS KERNEL MODE (FastMCP 3.x Sovereign Kernel)
    # -------------------------------------------------------------------------
    logger.info("BOOT: Detected VPS environment. Starting Sovereign Kernel...")
    
    setup_paths()
    try:
        from arifosmcp.runtime.server import mcp
    except ImportError as e:
        if "fastmcp.dependencies" in str(e):
            logger.error("FATAL: FastMCP 3.x required for Kernel mode. Use 'pip install -U fastmcp'")
        raise

# Export for FastMCP Cloud / Horizon
__all__ = ["mcp"]

if __name__ == "__main__":
    mcp.run()

"""
arifOS MCP Server - Universal Entrypoint (VPS + Horizon Compatible)
═══════════════════════════════════════════════════════════════════════════════

Auto-detects environment and switches between:
• VPS Mode:    Full Sovereign Kernel (FastMCP 3.x)
• Horizon Mode: Public Ambassador Proxy (FastMCP 2.x)

Repository: https://github.com/ariffazil/arifosmcp
API Key: fmcp_Z9oLZZ0OtOZkr4dzPCzp7hIm_GA2H-D94RUC2BzYnYw
"""

import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("arifos-gateway")

# ═══════════════════════════════════════════════════════════════════════════════
# CRITICAL: Detect Horizon BEFORE any imports that might fail
# ═══════════════════════════════════════════════════════════════════════════════

def _is_horizon_environment() -> bool:
    """
    Detect if running in Prefect Horizon environment.
    Checks multiple signals to handle both runtime and build-time detection.
    """
    # Primary: Horizon-specific environment variables
    if os.getenv("FASTMCP_CLOUD_URL"):
        return True
    if os.getenv("HORIZON_ENVIRONMENT"):
        return True
    
    # Secondary: FastMCP version check (works during build inspection)
    try:
        import fastmcp
        version = getattr(fastmcp, "__version__", "0.0.0")
        major_version = int(version.split(".")[0])
        if major_version < 3:
            logger.info(f"[DETECT] FastMCP {version} < 3.x → Horizon Mode")
            return True
    except Exception:
        pass
    
    # Tertiary: Check if we're in a containerized/cloud environment
    if os.getenv("KUBERNETES_SERVICE_HOST"):
        return True
    if os.path.exists("/.dockerenv") and not os.getenv("VPS_MODE"):
        # In Docker but not explicitly marked as VPS
        return True
        
    return False


IS_HORIZON = _is_horizon_environment()


# ═══════════════════════════════════════════════════════════════════════════════
# PATH SETUP (Safe for both environments)
# ═══════════════════════════════════════════════════════════════════════════════

def _setup_paths():
    """Ensure arifosmcp can be found in all environments."""
    _current_dir = os.path.dirname(os.path.abspath(__file__))
    if _current_dir not in sys.path:
        sys.path.insert(0, _current_dir)
    
    # Create fake module structure for Horizon if needed
    if 'arifosmcp' not in sys.modules:
        import types
        mod = types.ModuleType('arifosmcp')
        mod.__path__ = [_current_dir]
        sys.modules['arifosmcp'] = mod


_setup_paths()


# ═══════════════════════════════════════════════════════════════════════════════
# MODE-SPECIFIC IMPORTS (Only import what won't break)
# ═══════════════════════════════════════════════════════════════════════════════

if IS_HORIZON:
    # ═════════════════════════════════════════════════════════════════════════
    # HORIZON MODE: FastMCP 2.x Compatible - No 3.x imports!
    # ═════════════════════════════════════════════════════════════════════════
    logger.info("[BOOT] Horizon environment detected → Public Ambassador Mode")
    logger.info("[BOOT] All calls proxied to VPS kernel at arifosmcp.arif-fazil.com")
    
    # Import the Horizon-safe server (no fastmcp.dependencies!)
    from server_horizon import mcp
    
else:
    # ═════════════════════════════════════════════════════════════════════════
    # VPS MODE: Full Sovereign Kernel (FastMCP 3.x)
    # ═════════════════════════════════════════════════════════════════════════
    logger.info("[BOOT] VPS environment detected → Full Sovereign Kernel Mode")
    
    try:
        from arifosmcp.runtime.server import mcp
    except ImportError as e:
        if "fastmcp.dependencies" in str(e):
            logger.error("[FATAL] FastMCP 3.x required. Run: pip install -U fastmcp")
            logger.error("[FATAL] Or set VPS_MODE=1 if you're actually on VPS")
        raise


# Export for FastMCP Cloud / Horizon
__all__ = ["mcp"]

if __name__ == "__main__":
    mcp.run()

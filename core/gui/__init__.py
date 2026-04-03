"""
arifOS MCP - GUI Module
══════════════════════════════════════════════════════════════════════════════

Provides GUI components for ChatGPT Apps SDK integration.
Used when mode="gui" is passed to MCP tools.

Usage:
    from core.gui import build_apex_dashboard, wrap_with_meta
    
    @mcp.tool()
    def apex_judge(action: str, mode: str = "text"):
        if mode != "gui":
            return {"verdict": "SEAL", ...}
        
        data = fetch_arifos_status()
        dashboard = build_apex_dashboard(data)
        return {"verdict": "SEAL", **wrap_with_meta(dashboard)}
"""

from .widgets import (
    GUIWidget,
    Stat, Badge, Progress, Table, TableColumn, Text, Container,
    header, muted, kpi, status_badge, progress_bar, data_table
)

from .dashboard_builder import (
    build_apex_dashboard,
    build_session_status,
    build_vault_ledger,
    wrap_with_meta
)

__all__ = [
    # Widgets
    "GUIWidget",
    "Stat", "Badge", "Progress", "Table", "TableColumn", "Text", "Container",
    "header", "muted", "kpi", "status_badge", "progress_bar", "data_table",
    # Builders
    "build_apex_dashboard",
    "build_session_status", 
    "build_vault_ledger",
    "wrap_with_meta",
]
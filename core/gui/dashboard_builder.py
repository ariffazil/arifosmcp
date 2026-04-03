"""
arifOS MCP - Dashboard Builder
══════════════════════════════════════════════════════════════════════════════

Builds complete dashboard UI from arifOS data.
Used when mode="gui" is passed to tools.
"""

from typing import Optional
from .widgets import (
    Container, Text, Stat, Badge, Progress, Table, TableColumn,
    header, muted, kpi, status_badge, progress_bar, data_table
)


def build_apex_dashboard(data: dict) -> dict:
    """
    Build complete APEX dashboard UI.
    
    Args:
        data: Dictionary with arifOS status data:
            - system_name: str
            - updated_at: str
            - status: dict (system, governance, vault_integrity, etc.)
            - governance_health: dict (clarity, stability, judgment, etc.)
            - recent_verdicts: list of dict
    
    Returns:
        dict with _meta for ChatGPT Apps SDK
    """
    status = data.get("status", {})
    health = data.get("governance_health", {})
    verdicts = data.get("recent_verdicts", [])
    
    # Build the dashboard
    with Container(kind="vstack", gap=4) as dashboard:
        # Header
        dashboard.add(header(f"🧠 {data.get('system_name', 'arifOS APEX')}"))
        dashboard.add(muted(f"Updated: {data.get('updated_at', 'N/A')}"))
        
        # Status badges
        with Container(kind="hstack", gap=2) as badges:
            badges.add(status_badge(f"System: {status.get('system', 'Unknown')}", 
                                    status.get('system', 'unknown')))
            badges.add(status_badge(f"Gov: {status.get('governance', 'Unknown')}",
                                    status.get('governance', 'unknown')))
        dashboard.add(badges)
        
        # KPI Grid
        with Container(kind="grid", gap=2, css_class="grid-cols-3") as kpis:
            kpis.add(kpi("Vault Integrity", f"{status.get('vault_integrity', 0)}%"))
            kpis.add(kpi("Approval Rate", f"{status.get('approval_rate_7d', 0)}%"))
            kpis.add(kpi("Active Sessions", str(status.get('active_sessions', 0))))
            kpis.add(kpi("Breaches (24h)", str(status.get('policy_breaches_24h', 0))))
            kpis.add(kpi("Human Override", f"{health.get('human_override_respected', 0)}%"))
            kpis.add(kpi("Fail-Closed", f"{health.get('fail_closed_compliance', 0)}%"))
        dashboard.add(kpis)
        
        # Governance Health
        dashboard.add(header("Governance Health"))
        dashboard.add(progress_bar(
            labels=["Clarity", "Stability", "Judgment"],
            values=[
                health.get('clarity', 0),
                health.get('stability', 0),
                health.get('judgment', 0)
            ]
        ))
        
        # Recent Verdicts
        if verdicts:
            dashboard.add(header("Recent Verdicts"))
            dashboard.add(data_table(
                columns=[
                    TableColumn("time", "Time"),
                    TableColumn("verdict", "Verdict"),
                    TableColumn("risk", "Risk"),
                ],
                rows=verdicts
            ))
    
    return dashboard.to_component()


def build_session_status(data: dict) -> dict:
    """Build session status dashboard."""
    sessions = data.get("sessions", [])
    
    with Container(kind="vstack", gap=4) as dashboard:
        dashboard.add(header(f"📡 arifOS Sessions"))
        dashboard.add(muted(f"Total: {len(sessions)} active"))
        
        if sessions:
            dashboard.add(data_table(
                columns=[
                    TableColumn("id", "ID"),
                    TableColumn("actor", "Actor"),
                    TableColumn("mode", "Mode"),
                    TableColumn("result", "Result"),
                ],
                rows=sessions
            ))
    
    return dashboard.to_component()


def build_vault_ledger(data: dict, limit: int = 10) -> dict:
    """Build vault audit log dashboard."""
    entries = data.get("entries", [])[:limit]
    
    with Container(kind="vstack", gap=4) as dashboard:
        dashboard.add(header(f"🔐 Vault Ledger (Last {limit})"))
        
        if entries:
            dashboard.add(data_table(
                columns=[
                    TableColumn("timestamp", "Time"),
                    TableColumn("verdict", "Verdict"),
                    TableColumn("action", "Action"),
                    TableColumn("reasoning", "Reason"),
                ],
                rows=entries
            ))
        else:
            dashboard.add(muted("No recent entries"))
    
    return dashboard.to_component()


def wrap_with_meta(content: dict, title: Optional[str] = None) -> dict:
    """
    Wrap content with _meta for ChatGPT Apps SDK.
    
    Args:
        content: The UI component (from build_* functions)
        title: Optional title
    
    Returns:
        Full response with _meta
    """
    return {
        "_meta": {
            "outputType": "response",
            "outputTemplate": content
        },
        "_title": title
    }
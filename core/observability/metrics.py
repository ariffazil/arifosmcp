"""
core/observability/metrics.py — Live System Health & Performance

Tracks real-time performance metrics (latency, energy, tool accuracy)
for active sessions. This provides the 'Live Health' view contrasted
with the 'Historical Truth' of VAULT999.
"""

import time
from dataclasses import dataclass, field


@dataclass
class SystemMetric:
    """A data point for live system observability."""

    timestamp: float = field(default_factory=time.time)
    latency_ms: float = 0.0
    energy_consumed: float = 0.0  # Estimated compute cost
    tool_success: bool = True
    error_type: str | None = None


class LiveMetrics:
    """
    Live Observability Subsystem.
    Monitors system-wide health and session-specific performance.
    """

    def __init__(self):
        self._session_metrics: dict[str, list[SystemMetric]] = {}
        self._global_errors: int = 0

    def record_step(
        self,
        session_id: str,
        latency: float,
        energy: float,
        success: bool,
        error: str | None = None,
    ):
        """Record a single cognitive or material step."""
        if session_id not in self._session_metrics:
            self._session_metrics[session_id] = []

        metric = SystemMetric(
            latency_ms=latency, energy_consumed=energy, tool_success=success, error_type=error
        )
        self._session_metrics[session_id].append(metric)

        if not success:
            self._global_errors += 1

    def get_session_health(self, session_id: str) -> dict:
        """Calculate average health for a session."""
        metrics = self._session_metrics.get(session_id, [])
        if not metrics:
            return {"status": "inactive"}

        avg_latency = sum(m.latency_ms for m in metrics) / len(metrics)
        total_energy = sum(m.energy_consumed for m in metrics)
        success_rate = len([m for m in metrics if m.tool_success]) / len(metrics)

        return {
            "status": "healthy" if success_rate > 0.9 else "unstable",
            "avg_latency": f"{avg_latency:.2f}ms",
            "total_energy": f"{total_energy:.4f} units",
            "success_rate": f"{success_rate * 100:.1f}%",
            "data_points": len(metrics),
        }

    def get_global_status(self) -> dict:
        return {
            "active_monitored_sessions": len(self._session_metrics),
            "total_recorded_errors": self._global_errors,
            "system_uptime": "TBD",  # Logic for kernel start time needed
        }


# Global singleton
live_metrics = LiveMetrics()

# =========================================================================
# SYSTEM AUDITOR (Migrated from 333_APPS/forge_init.py)
# =========================================================================

import ast
from pathlib import Path


class SystemAuditor:
    """Verifies membrane architecture and thermodynamic separation."""

    @classmethod
    def check_5_organ_membrane(cls, arifos_root: Path) -> tuple[bool, list[str]]:
        """Verify server registers exactly the Sovereign Stack + Utilities."""
        server_path = arifos_root / "aaa_mcp" / "server.py"
        violations = []
        if not server_path.exists():
            return False, ["CRITICAL: aaa_mcp/server.py not found"]
        content = server_path.read_text()

        required_organs = [
            ("init_session", "Ψ"),
            ("agi_cognition", "Δ"),
            ("asi_empathy", "Ω"),
            ("apex_verdict", "Ψ"),
            ("vault_seal", "F1"),
        ]
        for organ, symbol in required_organs:
            if f'@mcp.tool(name="{organ}"' not in content:
                violations.append(f"MISSING ORGAN: {organ} ({symbol})")

        legacy_patterns = [
            '"reason"',
            '"validate"',
            '"align"',
            '"forge"',
            '"audit"',
            "9 A-CLIP skills",
        ]
        for pattern in legacy_patterns:
            if pattern in content and "Internal" not in content:
                violations.append(f"LEGACY REFERENCE: {pattern} (must be internal only)")

        return len(violations) == 0, violations

    @classmethod
    def audit_apps_bypass(cls, apps_dir: Path) -> list[str]:
        """Scan apps for direct LLM API calls (bypass)."""
        violations = []
        forbidden_imports = ["openai", "anthropic", "openai-python", "anthropic-python"]
        for py_file in apps_dir.rglob("*.py"):
            if py_file.name in ["metabolizer.py", "manifesto.py", "__init__.py"]:
                continue
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            for forbidden in forbidden_imports:
                                if forbidden in alias.name.lower():
                                    violations.append(
                                        f"{py_file.name}:{node.lineno} imports '{alias.name}'"
                                    )
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        for forbidden in forbidden_imports:
                            if forbidden in node.module.lower():
                                violations.append(
                                    f"{py_file.name}:{node.lineno} imports from '{node.module}'"
                                )
            except Exception:
                pass
        return violations

    @classmethod
    def check_thermodynamic_separation(cls, arifos_root: Path) -> tuple[bool, list[str]]:
        """Verify strict separation between core/ (Logic) and aaa_mcp/ (Transport)."""
        violations = []
        core_dir = arifos_root / "core"
        transport_libs = ["fastmcp", "starlette", "fastapi", "uvicorn", "mcp.server"]
        for py_file in core_dir.rglob("*.py"):
            try:
                source = py_file.read_text(encoding="utf-8")
                for lib in transport_libs:
                    if f"import {lib}" in source or f"from {lib}" in source:
                        violations.append(
                            f"VIOLATION: {py_file.name} imports '{lib}' (core/ must be PURE LOGIC)"
                        )
            except Exception:
                pass
        return len(violations) == 0, violations

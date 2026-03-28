"""
arifosmcp.intelligence/tools/safety_guard.py — Gating Decisions & Safety Relay
"""

from __future__ import annotations

import re
from typing import Any

from arifosmcp.intelligence.tools.aclip_base import ok, partial
from arifosmcp.intelligence.tools.system_monitor import get_system_health


def forge_guard(
    check_system_health: bool = True,
    cost_score_threshold: float = 0.8,
    cost_score_to_check: float = 0.0,
    action: str = "",
    target: str = "",
    session_id: str = "",
    risk_level: str = "low",  # low | medium | high | critical
    justification: str = "",
    dry_run: bool = True,
    require_approval: bool = False,
) -> dict[str, Any]:
    """
    Forge guard — local circuit breaker and gating sensor.
    Evaluates actions against safety patterns and system pressure.

    Args:
        check_system_health: Include host pressure checks
        cost_score_threshold: Threshold for warning/stop
        cost_score_to_check: Estimated cost score (0-1)
        action: Proposed action (e.g., 'delete', 'execute')
        target: Target resource or command
        session_id: Correlation ID
        risk_level: Assessed risk (low/medium/high/critical)
        justification: Intent description
        dry_run: Result only, no execution signal
        require_approval: Mandate manual review
    """
    gate = "OK"
    reason_code = "CLEAR"
    can_proceed = True
    reasons = []

    # 1. Cost Check
    if cost_score_to_check >= cost_score_threshold:
        gate = "SABAR"
        reason_code = "COST_THRESHOLD_EXCEEDED"
        can_proceed = False
        reasons.append(f"Cost score {cost_score_to_check} >= threshold {cost_score_threshold}")

    # 2. System Health Check
    host_signals = {}
    if check_system_health:
        health = get_system_health()
        if health.get("status") == "VOID":
            reasons.append(f"Safety check partial: System monitor error: {health.get('error')}")
        else:
            # get_system_health returns combined resource data at top level (wrapped by ok/partial)
            # meta keys are status, warning, etc.
            host_signals = {
                "cpu_percent": health.get("cpu", {}).get("percent", 0),
                "ram_percent": health.get("memory", {}).get("percent", 0),
            }

            # Use warnings from result if present
            warnings = health.get("warnings", [])
            if not warnings and "warning" in health:
                warnings = [health["warning"]]

            if any("HIGH" in w or "CRITICAL" in w for w in warnings):
                # Dry-run must stay deterministic for policy simulation and CI.
                # We surface host pressure as context, but only block live actions.
                if dry_run:
                    reasons.extend([f"DRY_RUN_HOST_SIGNAL: {w}" for w in warnings])
                else:
                    gate = "SABAR"
                    reason_code = "HOST_PRESSURE"
                    can_proceed = False
                    reasons.extend(warnings)

    # 3. Forbidden Patterns (F12 Defense)
    forbidden_patterns = [
        r"rm\s+-rf\s+/",
        r"dd\s+if=.*\s+of=/dev/",
        r"mkfs\.",
        r">\s*/etc/passwd",
        r":\(\)\{ :\|: & \}\;:",  # Fork bomb
    ]

    scan_text = f"{action} {target} {justification}".lower()
    danger_detected = False
    for pattern in forbidden_patterns:
        if re.search(pattern, scan_text, re.IGNORECASE):
            danger_detected = True
            gate = "VOID_LOCAL"
            reason_code = "FORBIDDEN_PATTERN"
            can_proceed = False
            reasons.append(f"DANGER: Forbidden pattern matched: {pattern}")
            break

    # 4. High/Critical Risk Actions require review (888_HOLD lane)
    if not danger_detected and risk_level in ("high", "critical"):
        gate = "SABAR"
        reason_code = "RISK_REVIEW_REQUIRED"
        can_proceed = False
        reasons.append(f"RISK: {risk_level.upper()} action requires sovereign review.")

    # 4. Critical Target Protection (F6 Empathy)
    if not danger_detected:
        critical_targets = [r"\.env", r"id_rsa", r"\.ssh", r"production", r"database"]
        for target_pat in critical_targets:
            if re.search(target_pat, target.lower()):
                if risk_level in ("high", "critical") or require_approval:
                    gate = "SABAR"
                    reason_code = "CRITICAL_TARGET_SABAR"
                    can_proceed = False
                    reasons.append(f"PROTECTED: Target '{target_pat}' requires review.")

    # Alignment with MCP Bridge Verdicts
    verdict_alias = {
        "OK": "SEAL",
        "SABAR": "SABAR",
        "VOID_LOCAL": "VOID",
    }.get(gate, "SABAR")

    payload = {
        "gate": gate,
        "verdict": verdict_alias,
        "reason_code": reason_code,
        "can_proceed": can_proceed,
        "danger_detected": danger_detected,
        "reasons": reasons,
        "host_signals": host_signals,
        "risk_level": risk_level,
        "dry_run": dry_run,
    }

    if gate == "VOID_LOCAL":
        # We return ok() here because the guard successfully executed its logic
        # and correctly identified a violation. The verdict field in payload
        # carries the actual 'VOID' signal for the consumer.
        return ok(payload, error=f"Safety violation: {reason_code}")
    if not can_proceed:
        return partial(payload, warning="; ".join(reasons))

    return ok(payload)

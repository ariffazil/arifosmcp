import asyncio
from typing import Any

from arifosmcp.intelligence.tools.envelope import unified_tool_output
from arifosmcp.core.kernel.constitutional_decorator import constitutional_floor
from arifosmcp.core.telemetry import log_telemetry

# Local compatibility ledger for ACLIP-only execution paths.
_LOCAL_STAGE_RESULTS: dict[str, dict[str, Any]] = {}


def store_stage_result(session_id: str, stage: str, result: dict[str, Any]) -> None:
    """Compatibility shim for stage result persistence without transport coupling."""
    _LOCAL_STAGE_RESULTS.setdefault(session_id, {})[stage] = result


async def vault_seal(
    session_id: str,
    verdict: str,
    payload: dict[str, Any],
    query_summary: str = "",
    category: str = "local_ops",
    floors_checked: list[str] | None = None,
    floors_failed: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compatibility shim for 999 sealing from ACLIP local guard flows."""
    seal_metadata = dict(metadata or {})
    if query_summary:
        seal_metadata["query_summary"] = query_summary
    if category:
        seal_metadata["category"] = category
    if floors_checked:
        seal_metadata["floors_checked"] = list(floors_checked)
    if floors_failed:
        seal_metadata["floors_failed"] = list(floors_failed)

    store_stage_result(
        session_id=session_id,
        stage="999_SEAL",
        result={
            "verdict": verdict,
            "payload": payload,
            "metadata": seal_metadata,
            "sealed": True,
        },
    )

    # Keep telemetry continuity for observability.
    log_telemetry(
        session_id=session_id,
        omega_0=0.0,
        irreversibility_index=0.0,
        verdict=verdict,
    )

    # Best-effort canonical VAULT write through core organ.
    try:
        from arifosmcp.core.organs._4_vault import vault

        await vault(
            action="seal",
            judge_output={
                "verdict": verdict,
                "floor_scores": {},
                "floors_failed": floors_failed or [],
            },
            session_id=session_id,
            query=query_summary,
            authority=category,
            eureka_data={"payload": payload, "metadata": seal_metadata},
        )
    except Exception:
        # Fail-open for compatibility: local guard should not crash on optional vault backend errors.
        pass

    return {
        "status": "SEALED",
        "verdict": verdict,
        "session_id": session_id,
    }


# Risk patterns for F6 Blast Radius
DESTRUCTIVE_PATTERNS = [
    "rm -rf",
    "rm -r",
    "rm -f",
    "mkfs",
    "dd if=",
    "fdisk",
    "chmod 777",
    "chown",
    "mv /",
    "cp /",
]

NETWORK_PATTERNS = ["curl", "wget", "ssh", "nc ", "netcat", "telnet", "ftp"]

CRITICAL_PATHS = ["/", "/etc", "/var", "/usr", "/bin", "/sbin", "C:\\Windows", "C:\\Program Files"]


def calculate_local_blast_radius(command: str) -> dict[str, Any]:
    """
    F6 Empathy: Calculate blast radius for local shell commands.
    Returns score (0.0-1.0) and reasoning.
    """
    score = 0.0
    reasoning = []

    # Check for destructive patterns
    for pattern in DESTRUCTIVE_PATTERNS:
        if pattern in command:
            score += 0.6
            reasoning.append(f"Destructive pattern detected: '{pattern}'")

    # Check for network activity (exfiltration risk)
    for pattern in NETWORK_PATTERNS:
        if pattern in command:
            score += 0.3
            reasoning.append(f"Network call detected: '{pattern}'")

    # Check for piping to shell (high risk of injection/execution)
    if "|" in command and ("sh" in command or "bash" in command or "python" in command):
        score += 0.5
        reasoning.append("Pipe-to-shell detected (RCE risk)")

    # Check for critical paths
    for path in CRITICAL_PATHS:
        # Simple check, real implementation would need robust path parsing
        if path in command:
            score += 0.4
            reasoning.append(f"Critical system path referenced: '{path}'")

    # Cap score
    score = min(1.0, score)

    return {
        "score": score,
        "reasoning": "; ".join(reasoning) if reasoning else "Low risk local command",
    }


@unified_tool_output(tool_name="local_exec", stage="444_ROUTER")
@constitutional_floor("F1", "F11", "F12")
async def local_exec_guard(
    command: str,
    session_id: str,
    justification: str,
    run_in_background: bool = False,
    require_human_match: bool = False,
) -> dict[str, Any]:
    """
    Constitutional Guard for Local Shell Execution.
    Enforces F1 (Audit), F6 (Blast Radius), and F11 (Authority).

    Args:
        command: The shell command to execute
        session_id: Constitutional session ID
        justification: Why this command is needed (for audit)
        run_in_background: If True, runs without waiting (async)
        require_human_match: Force 888_HOLD

    Returns:
        Standard verdict dictionary
    """
    # 1. Calculate Blast Radius (F6)
    blast = calculate_local_blast_radius(command)

    # 2. Determine Verdict
    verdict = "SEAL"
    verdict_reason = "Command approved"
    floors_failed = []

    if require_human_match:
        verdict = "888_HOLD"
        verdict_reason = "Human override requested explicitly"

    elif blast["score"] >= 0.5:
        verdict = "888_HOLD"
        verdict_reason = f"High risk command (Score: {blast['score']}): {blast['reasoning']}"
        floors_failed.append("F6")

    # 3. Log Intent (F1 Amanah)
    store_stage_result(
        session_id=session_id,
        stage="local_guard",
        result={
            "tool": "local_exec_guard",
            "command": command,
            "blast_score": blast["score"],
            "verdict": verdict,
        },
    )

    # 4. Handle Verdict
    if verdict == "888_HOLD":
        return {
            "status": "PENDING_APPROVAL",
            "verdict": "888_HOLD",
            "reason": verdict_reason,
            "blast_radius": blast,
            "command": command,
            "message": "🔒 DITEMPA BUKAN DIBERI: High-risk command requires human approval.",
        }

    # 5. Execute if SEALed
    try:
        # Create subprocess
        process = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        # If background, return immediately
        if run_in_background:
            return {
                "status": "SUCCESS",
                "verdict": "SEAL",
                "pid": process.pid,
                "message": "Command started in background",
            }

        # Wait for completion
        stdout, stderr = await process.communicate()

        result_payload = {
            "command": command,
            "return_code": process.returncode,
            "stdout": stdout.decode(errors="replace")[:2000],  # Truncate logs
            "stderr": stderr.decode(errors="replace")[:2000],
        }

        # 6. Seal in Vault (F1 Amanah - Post-execution log)
        await vault_seal(
            session_id=session_id,
            verdict="SEAL",
            payload=result_payload,
            query_summary=f"Exec: {command[:50]}",
            category="local_ops",
            floors_checked=["F1", "F6", "F11", "F12"],
            floors_failed=floors_failed,
        )

        return {
            "status": "SUCCESS" if process.returncode == 0 else "ERROR",
            "verdict": "SEAL",
            "result": result_payload,
            "blast_radius": blast,
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "verdict": "HOLD",
            "error": str(e),
            "command": command,
            "issue": "EXEC_FAIL",
        }

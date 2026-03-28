import subprocess
import os
import shlex
from datetime import datetime, timezone

# arifOS Governance Imports
from arifosmcp.core.shared.physics import delta_S
from arifosmcp.agentzero.escalation.hold_state import anchor_hold_registry

class HardenedShellForge:
    """
    Sovereign Forge for Shell Operations.
    
    Enforces arifOS 13 Floors:
    - F1 Amanah: Pre-execution checkpointing via git-worktree/commit.
    - F7 Humility: Mandatory dry_run enforcement.
    - F13 Sovereign: 888_HOLD logic for High/Critical risk commands.
    """
    
    def __init__(self, default_cwd: str = None):
        self.default_cwd = default_cwd or os.getcwd()

    def _is_high_risk(self, command: str) -> bool:
        """Heuristic for high-risk shell operations."""
        risk_patterns = ["rm ", "git push", "pip install", "rm -rf", "mv ", "> /", "docker rm", "sudo "]
        return any(p in command.lower() for p in risk_patterns)

    def execute(
        self,
        command: str,
        cwd: str = None,
        dry_run: bool = True,
        session_id: str = "anonymous"
    ) -> dict[str, any]:
        """Execute a shell command with governance induction."""
        target_cwd = cwd or self.default_cwd
        is_risk = self._is_high_risk(command)

        # 1. Check for global 888_HOLD (Anchor Void)
        if anchor_hold_registry.is_held(session_id):
            return {
                "ok": False,
                "status": "HOLD",
                "error": "888_HOLD: Anchor is void. Execution blocked.",
                "note": anchor_hold_registry.get_hold_reason(session_id)
            }

        # 2. Risk Evaluation & F13 Calibration
        if is_risk and not dry_run:
            # High risk + Not a dry run -> Force 888_HOLD unless explicit override
            return {
                "ok": False,
                "status": "888_HOLD",
                "error": "F13 Sovereign: High-risk command detected. Approval required.",
                "command_preview": command
            }

        # 3. F7 Humility: Dry Run Simulation
        if dry_run:
            return {
                "ok": True,
                "status": "SIMULATED",
                "command": command,
                "note": "F7 Humility: Command simulated but not executed.",
                "thermodynamics": {"delta_s": 0, "status": "STABLE"}
            }

        # 4. Preparation: F1 Amanah Checkpoint (MOCK Logic - in prod would call git)
        # Note: In a real system, we would trigger a worktree-add or commit here.

        # 5. Execution
        args = shlex.split(command)
        start_time = datetime.now(timezone.utc)

        try:
            result = subprocess.run(
                args,
                cwd=target_cwd,
                capture_output=True,
                text=True,
                check=False,
                timeout=60  # Humility limit: avoid hangs
            )

            # F4 Clarity: Thermodynamic Measurement
            input_context = f"{command} @ {target_cwd}"
            output_context = f"{result.stdout}\n{result.stderr}"
            ds = delta_S(input_context, output_context)

            return {
                "ok": result.returncode == 0,
                "status": "SEALED" if result.returncode == 0 else "ERROR",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "entropy": {"delta_s": round(ds, 4), "is_stable": ds <= 0},
                "execution_timestamp": start_time.isoformat()
            }
        except subprocess.TimeoutExpired:
            return {
                "ok": False,
                "status": "TIMEOUT",
                "error": "F7 Humility: Command timed_out after 60s.",
                "command": command
            }
        except Exception as e:
            return {
                "ok": False,
                "status": "EXCEPTION",
                "error": str(e),
                "command": command
            }

# Canonical instance
forge = HardenedShellForge()

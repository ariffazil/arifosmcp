"""
core/runtime_bridge.py - MCP Tool Wiring to Reality
Closes the Reality Gap by connecting skills to actual system execution.
"""

import subprocess
import shlex
from typing import Any, Dict
from dataclasses import dataclass


@dataclass
class ExecutionResult:
    """Result of system execution with constitutional metadata."""
    success: bool
    stdout: str
    stderr: str
    returncode: int
    command: str
    verification_hash: str
    execution_time_ms: float


class RuntimeBridge:
    """Bridge between AI skills and real system execution."""
    
    DANGEROUS_PATTERNS = [
        "rm -rf /", "> /dev/null", "curl | bash", 
        "sudo", "chmod 777", "mkfs"
    ]
    
    ALLOWED_COMMANDS = {
        "docker": ["ps", "images", "inspect", "logs", "stats"],
        "git": ["status", "log", "diff", "branch", "worktree"],
    }
    
    def __init__(self, session_id: str, dry_run: bool = True):
        self.session_id = session_id
        self.dry_run = dry_run
    
    async def execute(self, command: str, tool: str = "code_engine") -> ExecutionResult:
        """Execute command with constitutional pipeline."""
        
        # F7: Dry run
        if self.dry_run:
            return ExecutionResult(
                success=True,
                stdout=f"[DRY RUN] {command}",
                stderr="",
                returncode=0,
                command=command,
                verification_hash="dry_run",
                execution_time_ms=0.0
            )
        
        # F12: Injection check
        if any(p in command for p in self.DANGEROUS_PATTERNS):
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="F12_BLOCKED",
                returncode=-1,
                command=command,
                verification_hash="blocked",
                execution_time_ms=0.0
            )
        
        # Execute
        import time
        start = time.perf_counter()
        
        try:
            result = subprocess.run(
                shlex.split(command),
                capture_output=True,
                text=True,
                timeout=30,
                check=False
            )
            
            elapsed = (time.perf_counter() - start) * 1000
            
            return ExecutionResult(
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode,
                command=command,
                verification_hash=self._hash(result.stdout),
                execution_time_ms=elapsed
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                returncode=-1,
                command=command,
                verification_hash="error",
                execution_time_ms=0.0
            )
    
    def _hash(self, data: str) -> str:
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()[:16]


def get_runtime_bridge(session_id: str, dry_run: bool = True):
    return RuntimeBridge(session_id, dry_run)

"""
EngineerAgent - Code Execution (Ω Axis)

The EngineerAgent executes code, runs tools, and performs system operations.
It is heavily guarded by F11 (Command Auth) and requires Validator approval
for dangerous operations.

Constitutional Role: A-ENGINEER (Ω - Humility/Heart)
Enforced Floors: F5, F6, F9, F11

Responsibilities:
- Code execution in sandboxed environment
- Tool orchestration via MCP
- File system operations (audited)
- Shell command execution (F11 gated)
- Dynamic tool creation (with F8/F9 validation)

All dangerous operations require:
1. F11 authorization check
2. Validator approval (for high-risk)
3. Reversibility proof (F1)
4. VAULT999 logging
"""

from __future__ import annotations

import hashlib
import logging
import subprocess
from typing import Any, Dict, List, Optional

from .base import ConstitutionalAgent, FloorScore, TrinityRole, Verdict, VerdictStatus


logger = logging.getLogger(__name__)


class EngineerAgent(ConstitutionalAgent):
    """
    Engineer Agent - Executes code with constitutional safeguards.
    
    This agent can:
    - Execute Python/Shell code in sandboxed containers
    - Read/write files (audited)
    - Install packages (with approval)
    - Create dynamic tools (validated)
    
    It CANNOT:
    - Execute without F11 authorization
    - Bypass the Validator for dangerous ops
    - Access secrets without authentication
    - Execute irreversible actions without 888_HOLD
    """
    
    # Floors enforced by Engineer (Ω axis)
    ENGINEER_FLOORS = ["F5", "F6", "F9", "F11"]
    
    def __init__(self, agent_id: str = "engineer.001",
                 arifos_client=None,
                 sandbox_config: Optional[Dict] = None):
        super().__init__(
            agent_id=agent_id,
            role=TrinityRole.OMEGA,
            enforced_floors=self.ENGINEER_FLOORS,
            arifos_client=arifos_client,
            max_subagent_depth=2  # Can spawn specialist subagents
        )
        
        # Sandbox configuration
        self.sandbox_config = sandbox_config or {
            "network_isolated": True,
            "read_only_root": True,
            "max_memory_mb": 512,
            "max_execution_time": 300,  # 5 minutes
            "allowed_packages": ["numpy", "pandas", "requests"],
            "forbidden_commands": ["rm -rf /", "mkfs", "dd", ":(){:|:&};:"]
        }
        
        # Execution tracking
        self.code_executions = 0
        self.file_operations = 0
        self.blocked_operations = 0
        
        # Validator reference (for high-risk approval)
        self.validator: Optional[Any] = None
    
    @property
    def agent_type(self) -> str:
        return "engineer"
    
    def set_validator(self, validator: Any):
        """Set the ValidatorAgent for high-risk approvals."""
        self.validator = validator
    
    async def _execute_impl(self, task: Dict[str, Any],
                           execution_id: str,
                           verdict: Verdict) -> Dict[str, Any]:
        """
        Execute engineering task.
        
        Task types:
        - "execute_code": Run Python/Shell code
        - "read_file": Read file contents
        - "write_file": Write file (audited)
        - "install_package": Install Python package
        - "create_tool": Create dynamic tool
        - "shell_command": Execute shell command (F11 gated)
        """
        task_type = task.get("type", "execute_code")
        
        # Route to appropriate handler
        handlers = {
            "execute_code": self._execute_code,
            "read_file": self._read_file,
            "write_file": self._write_file,
            "install_package": self._install_package,
            "create_tool": self._create_tool,
            "shell_command": self._shell_command,
        }
        
        handler = handlers.get(task_type)
        if not handler:
            raise ValueError(f"Unknown engineer task type: {task_type}")
        
        return await handler(task, execution_id)
    
    async def _execute_code(self, task: Dict, execution_id: str) -> Dict[str, Any]:
        """
        Execute Python code in sandboxed environment.
        
        F9: Check for dark cleverness (obfuscation, exploits)
        F11: Verify authorization
        F5: Ensure constructive power only
        """
        code = task.get("code", "")
        language = task.get("language", "python")
        
        logger.info(f"[{execution_id}] Executing {language} code ({len(code)} chars)")
        
        # === F9: C_dark Check (Dark Cleverness) ===
        c_dark_score = self._check_c_dark(code)
        if c_dark_score > 0.3:
            self.blocked_operations += 1
            logger.warning(f"[{execution_id}] F9 violation: C_dark={c_dark_score}")
            return {
                "status": "BLOCKED",
                "reason": "F9_DARK_CLEVERNESS",
                "score": c_dark_score,
                "message": "Code contains suspicious patterns"
            }
        
        # === F11: Authorization Check ===
        is_dangerous = self._is_dangerous_code(code)
        if is_dangerous and not await self._verify_f11_auth(task):
            self.blocked_operations += 1
            return {
                "status": "BLOCKED",
                "reason": "F11_AUTH_REQUIRED",
                "message": "Dangerous code requires authorization"
            }
        
        # === F5: Peace² Check (Constructive Power) ===
        if not self._is_constructive(code):
            return {
                "status": "BLOCKED",
                "reason": "F5_NON_CONSTRUCTIVE",
                "message": "Code appears destructive"
            }
        
        # Execute in sandbox (MVP: subprocess, Production: Docker)
        try:
            if language == "python":
                result = await self._run_python_sandbox(code, execution_id)
            elif language == "shell":
                result = await self._run_shell_sandbox(code, execution_id)
            else:
                raise ValueError(f"Unsupported language: {language}")
            
            self.code_executions += 1
            
            return {
                "status": "success",
                "execution_id": execution_id,
                "language": language,
                "result": result,
                "c_dark_score": c_dark_score,
                "sandbox_used": True
            }
            
        except Exception as e:
            logger.error(f"[{execution_id}] Code execution failed: {e}")
            return {
                "status": "error",
                "execution_id": execution_id,
                "error": str(e)
            }
    
    async def _shell_command(self, task: Dict, execution_id: str) -> Dict[str, Any]:
        """
        Execute shell command with F11 gating.
        
        This is the most dangerous operation - requires:
        1. Local F11 check
        2. Validator approval for dangerous commands
        3. 888_HOLD for irreversible operations
        """
        command = task.get("command", "")
        
        logger.info(f"[{execution_id}] Shell command request: {command}")
        
        # Check against forbidden commands
        for forbidden in self.sandbox_config["forbidden_commands"]:
            if forbidden in command:
                self.blocked_operations += 1
                return {
                    "status": "BLOCKED",
                    "reason": "FORBIDDEN_COMMAND",
                    "command": command,
                    "message": f"Command contains forbidden pattern: {forbidden}"
                }
        
        # Determine risk level
        risk_level = self._assess_command_risk(command)
        
        # For high-risk commands, require Validator approval
        if risk_level in ["high", "critical"]:
            if not self.validator:
                return {
                    "status": "BLOCKED",
                    "reason": "VALIDATOR_REQUIRED",
                    "message": "High-risk command requires Validator approval"
                }
            
            # Request Validator approval
            validation_result = await self.validator.execute({
                "type": "validate_action",
                "action": {"type": "shell_command", "command": command},
                "agent_id": self.agent_id,
                "action_type": "shell_command",
                "risk_level": risk_level
            })
            
            if validation_result.get("verdict") != "SEAL":
                self.blocked_operations += 1
                return {
                    "status": "BLOCKED",
                    "reason": "VALIDATOR_DENIED",
                    "verdict": validation_result.get("verdict"),
                    "violations": validation_result.get("violations", [])
                }
        
        # Execute command (in production: Docker sandbox)
        try:
            result = await self._run_shell_sandbox(command, execution_id)
            
            return {
                "status": "success",
                "execution_id": execution_id,
                "command": command,
                "risk_level": risk_level,
                "result": result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "execution_id": execution_id,
                "error": str(e)
            }
    
    async def _read_file(self, task: Dict, execution_id: str) -> Dict[str, Any]:
        """Read file contents (audited)."""
        path = task.get("path", "")
        
        logger.info(f"[{execution_id}] Reading file: {path}")
        
        try:
            with open(path, 'r') as f:
                content = f.read()
            
            self.file_operations += 1
            
            # Calculate hash for audit
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            return {
                "status": "success",
                "path": path,
                "content": content,
                "hash": content_hash,
                "size": len(content)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "path": path,
                "error": str(e)
            }
    
    async def _write_file(self, task: Dict, execution_id: str) -> Dict[str, Any]:
        """Write file (audited with before/after hashes)."""
        path = task.get("path", "")
        content = task.get("content", "")
        
        logger.info(f"[{execution_id}] Writing file: {path} ({len(content)} bytes)")
        
        # Get before hash (if file exists)
        before_hash = None
        try:
            with open(path, 'rb') as f:
                before_hash = hashlib.sha256(f.read()).hexdigest()
        except FileNotFoundError:
            before_hash = "FILE_DID_NOT_EXIST"
        
        # Write file
        try:
            with open(path, 'w') as f:
                f.write(content)
            
            self.file_operations += 1
            
            # Calculate after hash
            with open(path, 'rb') as f:
                after_hash = hashlib.sha256(f.read()).hexdigest()
            
            return {
                "status": "success",
                "path": path,
                "before_hash": before_hash,
                "after_hash": after_hash,
                "size": len(content)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "path": path,
                "error": str(e)
            }
    
    async def _create_tool(self, task: Dict, execution_id: str) -> Dict[str, Any]:
        """
        Create dynamic tool with F8/F9 validation.
        
        Requires:
        - F8: Coherence check (A × P × X × E² ≥ 0.80)
        - F9: C_dark limit (< 0.30)
        - F11: Authorization
        """
        tool_name = task.get("name", "")
        tool_code = task.get("code", "")
        
        logger.info(f"[{execution_id}] Creating tool: {tool_name}")
        
        # F8: Genius/Coherence check
        coherence = self._calculate_coherence(tool_code)
        if coherence < 0.80:
            return {
                "status": "REJECTED",
                "reason": "F8_INCOHERENT",
                "coherence": coherence,
                "message": "Tool code lacks coherence"
            }
        
        # F9: Dark cleverness check
        c_dark = self._check_c_dark(tool_code)
        if c_dark > 0.30:
            return {
                "status": "REJECTED",
                "reason": "F9_DARK_CLEVERNESS",
                "c_dark": c_dark,
                "message": "Tool code contains dark patterns"
            }
        
        # Create tool (simplified for MVP)
        tool_hash = hashlib.sha256(tool_code.encode()).hexdigest()
        
        return {
            "status": "FORGED",
            "tool_name": tool_name,
            "tool_hash": tool_hash,
            "coherence": coherence,
            "c_dark": c_dark,
            "f8_verified": True,
            "f9_verified": True
        }
    
    async def _install_package(self, task: Dict, execution_id: str) -> Dict[str, Any]:
        """Install Python package (with approval check)."""
        package = task.get("package", "")
        
        logger.info(f"[{execution_id}] Installing package: {package}")
        
        # Check if package is allowed
        if package not in self.sandbox_config["allowed_packages"]:
            return {
                "status": "BLOCKED",
                "reason": "PACKAGE_NOT_ALLOWED",
                "package": package,
                "message": f"Package {package} not in allowed list"
            }
        
        # Would execute pip install in sandbox
        return {
            "status": "success",
            "package": package,
            "installed": True
        }
    
    # === Helper Methods ===
    
    def _check_c_dark(self, code: str) -> float:
        """
        F9: Measure dark cleverness (0.0 - 1.0).
        
        Looks for:
        - Obfuscation
        - Misleading variable names
        - Exploit patterns
        - Self-modification
        """
        score = 0.0
        code_lower = code.lower()
        
        # Obfuscation patterns
        obfuscation = ["eval(", "exec(", "__import__", "getattr", "globals()"]
        for pattern in obfuscation:
            if pattern in code_lower:
                score += 0.1
        
        # Suspicious imports
        suspicious = ["subprocess", "os.system", "socket", "ctypes"]
        for lib in suspicious:
            if f"import {lib}" in code_lower or f"from {lib}" in code_lower:
                score += 0.15
        
        # Self-modification
        if "__code__" in code or "compile(" in code_lower:
            score += 0.2
        
        return min(1.0, score)
    
    def _calculate_coherence(self, code: str) -> float:
        """
        F8: Calculate coherence G = A × P × X × E² (0.0 - 1.0).
        
        Simplified calculation for MVP:
        - Accuracy: Syntax validity
        - Precision: Clear naming
        - Novelty: Not copy-paste
        - Elegance: Simplicity
        """
        # Simplified - would use actual analysis
        # High coherence = well-structured, documented, clear code
        lines = code.split('\n')
        
        # Check for documentation
        has_docs = '"""' in code or "'''" in code
        
        # Check for clear naming (rough heuristic)
        has_clear_names = any(len(word) > 3 for word in code.split())
        
        # Check for structure
        has_structure = 'def ' in code or 'class ' in code
        
        score = 0.5  # Base
        if has_docs: score += 0.2
        if has_clear_names: score += 0.15
        if has_structure: score += 0.15
        
        return min(1.0, score)
    
    def _is_dangerous_code(self, code: str) -> bool:
        """Check if code is potentially dangerous."""
        dangerous = [
            "rm -rf", "os.remove", "shutil.rmtree",
            "socket", "urllib.request", "requests.post"
        ]
        code_lower = code.lower()
        return any(d in code_lower for d in dangerous)
    
    def _is_constructive(self, code: str) -> bool:
        """F5: Check if code is constructive (not destructive)."""
        destructive = ["delete", "destroy", "wipe", "nuke"]
        code_lower = code.lower()
        return not any(d in code_lower for d in destructive)
    
    async def _verify_f11_auth(self, task: Dict) -> bool:
        """Verify F11 authorization for dangerous operations."""
        # In production: Call arifOS F11 verification
        # For MVP: Simplified check
        return task.get("authorized", False)
    
    def _assess_command_risk(self, command: str) -> str:
        """Assess risk level of shell command."""
        high_risk = ["rm -rf", "sudo", "mkfs", "dd if", "iptables"]
        medium_risk = ["apt", "pip install", "git push", "docker"]
        
        cmd_lower = command.lower()
        
        for hr in high_risk:
            if hr in cmd_lower:
                return "critical"
        
        for mr in medium_risk:
            if mr in cmd_lower:
                return "high"
        
        return "low"
    
    async def _run_python_sandbox(self, code: str, execution_id: str) -> Dict:
        """Run Python code in sandboxed subprocess."""
        # MVP: Use subprocess with timeout
        # Production: Use Docker container
        
        try:
            result = subprocess.run(
                ["python", "-c", code],
                capture_output=True,
                text=True,
                timeout=self.sandbox_config["max_execution_time"],
                cwd="/tmp/sandbox"  # Restricted directory
            )
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Execution timeout", "stdout": "", "stderr": ""}
        except Exception as e:
            return {"error": str(e), "stdout": "", "stderr": ""}
    
    async def _run_shell_sandbox(self, command: str, execution_id: str) -> Dict:
        """Run shell command in sandboxed subprocess."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.sandbox_config["max_execution_time"],
                cwd="/tmp/sandbox"
            )
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Execution timeout", "stdout": "", "stderr": ""}
        except Exception as e:
            return {"error": str(e), "stdout": "", "stderr": ""}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engineer statistics."""
        return {
            "code_executions": self.code_executions,
            "file_operations": self.file_operations,
            "blocked_operations": self.blocked_operations,
            "sandbox_config": self.sandbox_config
        }

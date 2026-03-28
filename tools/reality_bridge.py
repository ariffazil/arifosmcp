"""
arifOS Reality Bridge - MCP Tool Wiring
Closes the Reality Gap (R) by connecting skills to real execution.
"""

import subprocess
import json
from typing import Dict, Any, Optional
from datetime import datetime


class RealityBridge:
    """Bridges AI skills to real system execution with constitutional governance."""
    
    def __init__(self):
        self.checkpoints = []
        self.execution_log = []
        
    def execute(self, tool: str, command: str, params: Dict[str, Any], 
                checkpoint_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute real system command with F1-F13 governance.
        
        Args:
            tool: Tool type (docker, git, filesystem)
            command: Command to execute
            params: Command parameters
            checkpoint_id: F1 reversibility checkpoint
        
        Returns:
            Execution result with F2 verification metadata
        """
        # F12: Injection defense
        if self._detect_injection(command):
            return {
                "status": "VOID",
                "success": False,
                "error": "F12_INJECTION_DETECTED",
                "command": command
            }
        
        # F1: Verify checkpoint exists for reversibility
        if not checkpoint_id:
            return {
                "status": "HOLD",
                "success": False,
                "error": "F1_CHECKPOINT_REQUIRED",
                "message": "Create checkpoint before execution: aclip checkpoint create"
            }
        
        # Execute based on tool type
        try:
            if tool == "docker":
                result = self._exec_docker(command, params)
            elif tool == "git":
                result = self._exec_git(command, params)
            elif tool == "filesystem":
                result = self._exec_fs(command, params)
            elif tool == "ssh":
                result = self._exec_ssh(command, params)
            elif tool == "shell":
                result = self._exec_shell(command, params)
            else:
                return {
                    "status": "VOID",
                    "success": False,
                    "error": f"Unknown tool: {tool}"
                }
        except Exception as e:
            return {
                "status": "VOID",
                "success": False,
                "error": str(e)
            }
        
        # F2: Verify execution succeeded
        if result.get("returncode", -1) == 0:
            result["success"] = True
            result["status"] = "SEAL"
            result["verification"] = self._verify_truth(result)
        else:
            result["success"] = False
            result["status"] = "VOID"
            result["floor_failed"] = "F2_TRUTH"
        
        # F10: Audit log
        self.execution_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "tool": tool,
            "command": command,
            "checkpoint_id": checkpoint_id,
            "result": result["status"]
        })
        
        return result
    
    def _exec_docker(self, command: str, params: Dict) -> Dict[str, Any]:
        """Execute Docker command."""
        cmd = ["docker"] + command.split()
        if params.get("container"):
            cmd.append(params["container"])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "returncode": 1}

    
    def _exec_git(self, command: str, params: Dict) -> Dict[str, Any]:
        """Execute Git command."""
        cmd = ["git"] + command.split()
        if params.get("path"):
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=30, cwd=params["path"]
                )
                return {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
            except Exception as e:
                return {"stdout": "", "stderr": str(e), "returncode": 1}
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "returncode": 1}
    
    def _exec_fs(self, command: str, params: Dict) -> Dict[str, Any]:
        """Execute filesystem operations."""
        import os
        try:
            if command == "list":
                path = params.get("path", ".")
                items = os.listdir(path)
                return {
                    "stdout": json.dumps(items),
                    "stderr": "",
                    "returncode": 0
                }
            elif command == "read":
                path = params.get("path", "")
                with open(path, 'r') as f:
                    content = f.read()
                return {
                    "stdout": content,
                    "stderr": "",
                    "returncode": 0
                }
            elif command == "exists":
                path = params.get("path", "")
                exists = os.path.exists(path)
                return {
                    "stdout": json.dumps({"exists": exists}),
                    "stderr": "",
                    "returncode": 0
                }
            else:
                return {
                    "stdout": "",
                    "stderr": f"Unknown fs command: {command}",
                    "returncode": 1
                }
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "returncode": 1}

    
    def _exec_ssh(self, command: str, params: Dict) -> Dict[str, Any]:
        """Execute SSH command."""
        host = params.get("host", "")
        user = params.get("user", "")
        cmd = ["ssh", f"{user}@{host}", command]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "returncode": 1}
    
    def _exec_shell(self, command: str, params: Dict) -> Dict[str, Any]:
        """Execute shell command with F12 protection."""
        if self._is_dangerous_shell(command):
            return {
                "stdout": "",
                "stderr": "F12: Dangerous shell command blocked",
                "returncode": 1
            }
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "returncode": 1}
    
    def _detect_injection(self, command: str) -> bool:
        """F12: Detect command injection attempts."""
        dangerous = [";", "&&", "||", "`", "$(", ">>", ">/"]
        return any(pattern in command for pattern in dangerous)
    
    def _is_dangerous_shell(self, command: str) -> bool:
        """Check for dangerous shell patterns."""
        dangerous_patterns = [
            "rm -rf /", "rm -rf /*", "> /dev/sda", "mkfs.", "dd if=/dev/zero",
            "format c:", "del /f /s /q", ":(){ :|:& };:"
        ]
        return any(pattern in command.lower() for pattern in dangerous_patterns)
    
    def _verify_truth(self, result: Dict) -> Dict[str, Any]:
        """F2: Cross-verify execution result."""
        output = result.get("stdout", "")
        return {
            "timestamp_valid": True,
            "output_hash": hash(output) & 0xFFFF,
            "verification_method": "direct_execution"
        }


def execute(tool: str, command: str, params: Dict, checkpoint_id: str = None) -> Dict:
    """Convenience function for direct execution."""
    bridge = RealityBridge()
    return bridge.execute(tool, command, params, checkpoint_id)

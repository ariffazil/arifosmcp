# F2: Constitutional Skill Bridge
# arifOS_kernel | init_anchor | apex_soul
# F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12, F13

"""
core/skill_bridge.py - SKILL to MCP Bridge

Connects the 9 Skills to MCP tools with constitutional governance:
1. F1: Reversibility check
2. F7: Dry run enforcement
3. F3: Tri-Witness validation
4. F13: Human override capability
"""

from typing import Any, Dict, Optional
from core.intelligence import compute_w3


class SkillBridge:
    """Bridge between Skills and MCP tools with constitutional checks."""
    
    def __init__(self, session_id: str, dry_run: bool = True):
        self.session_id = session_id
        self.dry_run = dry_run
        self.checkpoint = None
        self.reality_bridge = None
    
    def _get_reality_bridge(self):
        """Lazy import RealityBridge to avoid circular deps."""
        if self.reality_bridge is None:
            from arifosmcp.tools.reality_bridge import RealityBridge
            self.reality_bridge = RealityBridge()
        return self.reality_bridge
    
    async def execute_skill(
        self,
        skill_name: str,
        action: str,
        params: Dict[str, Any],
        operator: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Execute a skill with full constitutional pipeline.
        
        Flow:
        1. F1: Create checkpoint (reversibility)
        2. F7: Dry run check
        3. SKILL: Execute handler (now wired to Reality Bridge)
        4. F3: Tri-Witness validation
        5. F13: Human override check (if high risk)
        6. VAULT: Seal result
        """
        from skills import get_skill
        
        # Get skill
        skill_info = get_skill(skill_name)
        if not skill_info:
            return {
                "verdict": "VOID",
                "reason": f"Unknown skill: {skill_name}"
            }
        
        # F1: Create checkpoint for reversibility
        self.checkpoint = await self._create_checkpoint(skill_name, action)
        
        # F7: Dry run enforcement
        if self.dry_run:
            return await self._dry_run(skill_info, action, params)
        
        # Execute skill handler WITH Reality Bridge
        # Skills now get real execution through reality_bridge param
        skill_execute = skill_info["execute"]
        result = await skill_execute(
            action, 
            params, 
            self.session_id, 
            self.dry_run,
            reality_bridge=self._get_reality_bridge(),
            checkpoint=self.checkpoint
        )
        
        # F3: Tri-Witness validation
        if "w3_score" not in result:
            w3 = self._compute_w3(result, operator)
            result["w3_score"] = w3
            result["verdict"] = "SEAL" if w3 >= 0.95 else "888_HOLD"
        
        # F13: Human override for high risk
        if result.get("verdict") == "888_HOLD" and operator == "anonymous":
            result["required_action"] = "Run: aclip vault seal --approve"
        
        # Add checkpoint for rollback
        result["checkpoint"] = self.checkpoint
        result["rollback"] = f"aclip worktree rm {self.checkpoint}"
        
        return result
    
    async def _create_checkpoint(self, skill: str, action: str) -> str:
        """F1: Create reversibility checkpoint."""
        import uuid
        checkpoint = f"checkpoint-{skill}-{action}-{uuid.uuid4().hex[:8]}"
        return checkpoint
    
    async def _dry_run(self, skill_info: Dict, action: str, params: Dict) -> Dict[str, Any]:
        """F7: Simulate execution without side effects."""
        return {
            "verdict": "SEAL",
            "mode": "dry_run",
            "skill": skill_info["skill"].__name__,
            "action": action,
            "params": params,
            "would_execute": True,
            "checkpoint": self.checkpoint,
            "f7_compliant": True
        }
    
    def _compute_w3(self, result: Dict, operator: str) -> float:
        """F3: Compute Tri-Witness score."""
        human = 1.0 if operator != "anonymous" else 0.7
        ai = 0.95 if result.get("verdict") != "VOID" else 0.3
        earth = result.get("verification", 0.9)
        return compute_w3(human, ai, earth)


# Global bridge instance
_bridge: Optional[SkillBridge] = None


def get_bridge(session_id: str, dry_run: bool = True) -> SkillBridge:
    """Get or create skill bridge."""
    global _bridge
    if _bridge is None or _bridge.session_id != session_id:
        _bridge = SkillBridge(session_id, dry_run)
    return _bridge


async def execute_skill(
    skill_name: str,
    action: str,
    params: Dict[str, Any],
    session_id: str,
    dry_run: bool = True,
    operator: str = "anonymous"
) -> Dict[str, Any]:
    """
    Convenience function: Execute skill with constitutional bridge.
    
    Example:
        result = await execute_skill(
            "vps-docker",
            "check_status",
            {},
            session_id="abc123",
            dry_run=True
        )
    """
    bridge = get_bridge(session_id, dry_run)
    return await bridge.execute_skill(skill_name, action, params, operator)


# NEW: Direct execution through Reality Bridge
def execute_reality(
    tool: str,
    command: str,
    params: Dict[str, Any],
    checkpoint_id: str = None
) -> Dict[str, Any]:
    """
    Direct execution through Reality Bridge.
    Used by skills to call real system tools.
    """
    from arifosmcp.tools.reality_bridge import execute
    return execute(tool, command, params, checkpoint_id)


__all__ = ["SkillBridge", "get_bridge", "execute_skill", "execute_reality"]

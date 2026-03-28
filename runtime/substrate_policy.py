"""
arifosmcp/runtime/substrate_policy.py — The Intelligence Mapping for AAA Wire

This policy defines the Substrate Capability Class, Risk Tier, and Constitutional 
Floors for every mode in the M-11 Mega-Tool surface.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List

class SubstrateClass(str, Enum):
    INSPECT = "inspect"
    READ = "read"
    RECALL = "recall"
    WRITE = "write"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    COMMIT = "commit"
    COMMUNICATE = "communicate"

class RiskTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass(frozen=True)
class ModePolicy:
    substrate: SubstrateClass
    risk: RiskTier
    organ_stage: str
    floors: List[str] # Explicit Floor Mapping
    description: str

# The Canonical AAA Tool Policy Matrix
AAA_SUBSTRATE_POLICY = {
    "init_anchor": {
        "init": ModePolicy(SubstrateClass.WRITE, RiskTier.LOW, "000_INIT", ["F1", "F11", "F12"], "Bind session identity"),
        "state": ModePolicy(SubstrateClass.INSPECT, RiskTier.LOW, "000_INIT", ["F11"], "Check session status"),
        "refresh": ModePolicy(SubstrateClass.UPDATE, RiskTier.MEDIUM, "000_INIT", ["F11"], "Rotate tokens"),
        "revoke": ModePolicy(SubstrateClass.DELETE, RiskTier.HIGH, "000_INIT", ["F11", "F13"], "Kill session authority")
    },
    "physics_reality": {
        "search": ModePolicy(SubstrateClass.READ, RiskTier.MEDIUM, "111_SENSE", ["F2", "F3"], "Web grounding"),
        "ingest": ModePolicy(SubstrateClass.WRITE, RiskTier.MEDIUM, "111_SENSE", ["F2", "F10"], "Evidence creation"),
        "compass": ModePolicy(SubstrateClass.READ, RiskTier.LOW, "111_SENSE", ["F2"], "Directional grounding"),
        "atlas": ModePolicy(SubstrateClass.UPDATE, RiskTier.MEDIUM, "111_SENSE", ["F2", "F3"], "Multi-source mapping")
    },
    "agi_mind": {
        "reason": ModePolicy(SubstrateClass.READ, RiskTier.MEDIUM, "333_MIND", ["F2", "F4", "F7", "F8"], "First-principles logic"),
        "reflect": ModePolicy(SubstrateClass.INSPECT, RiskTier.MEDIUM, "333_MIND", ["F4", "F7"], "Self-audit loop"),
        "forge": ModePolicy(SubstrateClass.WRITE, RiskTier.MEDIUM, "333_MIND", ["F1", "F8"], "Artifact synthesis")
    },
    "asi_heart": {
        "critique": ModePolicy(SubstrateClass.READ, RiskTier.MEDIUM, "666_HEART", ["F5", "F6", "F9"], "Adversarial safety audit"),
        "simulate": ModePolicy(SubstrateClass.READ, RiskTier.MEDIUM, "666_HEART", ["F5", "F6"], "Stakeholder impact modeling")
    },
    "engineering_memory": {
        "vector_query": ModePolicy(SubstrateClass.RECALL, RiskTier.MEDIUM, "555_MEMORY", ["F10"], "Semantic retrieval"),
        "vector_store": ModePolicy(SubstrateClass.WRITE, RiskTier.MEDIUM, "555_MEMORY", ["F10"], "Memory commit"),
        "engineer": ModePolicy(SubstrateClass.EXECUTE, RiskTier.HIGH, "555_MEMORY", ["F1", "F11", "F13"], "High-stakes tool generation")
    },
    "code_engine": {
        "fs": ModePolicy(SubstrateClass.INSPECT, RiskTier.MEDIUM, "M-3_EXEC", ["F11", "F12"], "Filesystem inspection"),
        "process": ModePolicy(SubstrateClass.INSPECT, RiskTier.MEDIUM, "M-3_EXEC", ["F11", "F12"], "Process monitoring"),
        "run": ModePolicy(SubstrateClass.EXECUTE, RiskTier.HIGH, "M-3_EXEC", ["F11", "F12", "F13"], "Sandboxed script execution")
    },
    "architect_registry": {
        "list": ModePolicy(SubstrateClass.INSPECT, RiskTier.LOW, "M-4_ARCH", ["F11"], "Resource discovery"),
        "read": ModePolicy(SubstrateClass.READ, RiskTier.LOW, "M-4_ARCH", ["F11"], "Resource inspection"),
        "register": ModePolicy(SubstrateClass.WRITE, RiskTier.HIGH, "M-4_ARCH", ["F1", "F11", "F13"], "Component registration")
    },
    "apex_soul": {
        "judge": ModePolicy(SubstrateClass.INSPECT, RiskTier.MEDIUM, "888_JUDGE", ["F13"], "Final verdict"),
        "rules": ModePolicy(SubstrateClass.READ, RiskTier.LOW, "888_JUDGE", ["F13"], "Floor inspection"),
        "validate": ModePolicy(SubstrateClass.READ, RiskTier.MEDIUM, "888_JUDGE", ["F13"], "Action validation"),
        "armor": ModePolicy(SubstrateClass.INSPECT, RiskTier.MEDIUM, "888_JUDGE", ["F12"], "Shield scan")
    },
    "vault_ledger": {
        "seal": ModePolicy(SubstrateClass.COMMIT, RiskTier.HIGH, "999_VAULT", ["F1", "F3", "F13"], "Immutable audit seal"),
        "verify": ModePolicy(SubstrateClass.READ, RiskTier.MEDIUM, "999_VAULT", ["F3"], "Integrity check")
    }
}

def get_policy(tool: str, mode: str) -> ModePolicy | None:
    return AAA_SUBSTRATE_POLICY.get(tool, {}).get(mode)

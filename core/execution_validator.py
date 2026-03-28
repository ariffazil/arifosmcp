"""
core/execution_validator.py - Enhanced Feedback Loop Handler

Closes the Truth Gap (T) by validating execution results with:
1. Hash-based output verification
2. State diff comparison
3. F2 Truth enforcement
"""

import hashlib
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from difflib import unified_diff


@dataclass
class VerificationResult:
    """Result of output verification."""
    hash_match: bool
    content_hash: str
    expected_hash: Optional[str]
    integrity_score: float


@dataclass
class StateDiff:
    """Difference between expected and actual state."""
    added: List[str]
    removed: List[str]
    modified: List[str]
    similarity: float


@dataclass
class ValidationResult:
    """Result of execution validation."""
    w3_score: float
    human_witness: float
    ai_witness: float
    earth_witness: float
    verdict: str
    verification: VerificationResult
    state_diff: Optional[StateDiff] = None
    feedback: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())



class ExecutionValidator:
    """Validates execution results and closes the feedback loop."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.validation_history: List[ValidationResult] = []
        self.state_snapshots: Dict[str, str] = {}
    
    def validate_execution(
        self,
        expected: Dict[str, Any],
        actual: Dict[str, Any],
        human_approved: bool = True,
        compute_diff: bool = False
    ) -> ValidationResult:
        """Validate execution result against expectation."""
        # Human witness
        h = 1.0 if human_approved else 0.0
        
        # AI witness - did execution succeed?
        a = 1.0 if actual.get("success", False) else 0.3
        
        # Earth witness - verify actual system state
        e, verification = self._verify_earth_state(expected, actual)
        
        # Compute state diff if requested
        state_diff = None
        if compute_diff:
            state_diff = self._compute_state_diff(expected, actual)
        
        # Calculate W3
        w3 = (h * a * e) ** (1/3)
        
        # Determine verdict
        if w3 >= 0.95:
            verdict = "SEAL"
        elif w3 >= 0.85:
            verdict = "PARTIAL"
        elif w3 >= 0.70:
            verdict = "SABAR"
        else:
            verdict = "VOID"
        
        result = ValidationResult(
            w3_score=w3,
            human_witness=h,
            ai_witness=a,
            earth_witness=e,
            verdict=verdict,
            verification=verification,
            state_diff=state_diff,
            feedback={
                "expected": expected,
                "actual": actual,
                "validation_method": "hash_verification",
                "timestamp": datetime.now().isoformat()
            }
        )
        
        self.validation_history.append(result)
        return result

    
    def _verify_earth_state(
        self, expected: Dict, actual: Dict
    ) -> Tuple[float, VerificationResult]:
        """Verify actual system state changed as expected."""
        expected_output = expected.get("stdout", "")
        actual_output = actual.get("stdout", "")
        
        expected_hash = expected.get("verification_hash") or self._compute_hash(expected_output)
        actual_hash = self._compute_hash(actual_output)
        
        returncode = actual.get("returncode", -1)
        
        if returncode == 0:
            if expected_hash and actual_hash == expected_hash:
                return 1.0, VerificationResult(
                    hash_match=True, content_hash=actual_hash,
                    expected_hash=expected_hash, integrity_score=1.0
                )
            else:
                similarity = self._content_similarity(expected_output, actual_output)
                return 0.9 + (0.1 * similarity), VerificationResult(
                    hash_match=False, content_hash=actual_hash,
                    expected_hash=expected_hash, integrity_score=similarity
                )
        else:
            return 0.3, VerificationResult(
                hash_match=False, content_hash=actual_hash,
                expected_hash=expected_hash, integrity_score=0.0
            )
    
    def _compute_hash(self, content: str) -> str:
        """Compute SHA256 hash of content."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _content_similarity(self, expected: str, actual: str) -> float:
        """Calculate similarity between expected and actual output."""
        if not expected and not actual:
            return 1.0
        if not expected or not actual:
            return 0.0
        
        expected_lines = set(expected.split("\n"))
        actual_lines = set(actual.split("\n"))
        
        intersection = len(expected_lines & actual_lines)
        union = len(expected_lines | actual_lines)
        
        return intersection / union if union > 0 else 0.0

    
    def _compute_state_diff(
        self, expected: Dict, actual: Dict
    ) -> Optional[StateDiff]:
        """Compute detailed diff between expected and actual state."""
        expected_lines = expected.get("stdout", "").split("\n")
        actual_lines = actual.get("stdout", "").split("\n")
        
        diff = list(unified_diff(
            expected_lines, actual_lines,
            fromfile="expected", tofile="actual", lineterm=""
        ))
        
        added = []
        removed = []
        modified = []
        
        for line in diff:
            if line.startswith("+") and not line.startswith("+++"):
                added.append(line[1:])
            elif line.startswith("-") and not line.startswith("---"):
                removed.append(line[1:])
            elif line.startswith("@@"):
                modified.append(line)
        
        similarity = self._content_similarity(expected.get("stdout", ""), actual.get("stdout", ""))
        
        return StateDiff(
            added=added, removed=removed, modified=modified, similarity=similarity
        )
    
    def get_learning_summary(self) -> Dict:
        """Generate learning summary from validation history."""
        if not self.validation_history:
            return {"message": "No executions yet"}
        
        total = len(self.validation_history)
        sealed = sum(1 for v in self.validation_history if v.verdict == "SEAL")
        avg_w3 = sum(v.w3_score for v in self.validation_history) / total
        avg_integrity = sum(v.verification.integrity_score for v in self.validation_history) / total
        
        return {
            "total_executions": total,
            "seal_rate": sealed / total,
            "average_w3": avg_w3,
            "average_integrity": avg_integrity,
            "trend": "improving" if avg_w3 > 0.9 else "stable"
        }
    
    def snapshot_state(self, path: str, content: str):
        """Save state snapshot for later comparison."""
        self.state_snapshots[path] = self._compute_hash(content)
    
    def verify_state_unchanged(self, path: str, content: str) -> bool:
        """Verify that state has not changed since snapshot."""
        if path not in self.state_snapshots:
            return False
        current_hash = self._compute_hash(content)
        return self.state_snapshots[path] == current_hash


def validate(
    expected: Dict, actual: Dict, session_id: str,
    human_approved: bool = True, compute_diff: bool = False
) -> ValidationResult:
    """Convenience function for validation."""
    validator = ExecutionValidator(session_id)
    return validator.validate_execution(expected, actual, human_approved, compute_diff)

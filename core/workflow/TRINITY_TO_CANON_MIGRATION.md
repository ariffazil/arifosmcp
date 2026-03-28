# Trinity to Canonical Workflow Migration Guide

**From:** trinity-governance-core (v54.1-HARDENED)  
**To:** workflow-system.yaml + governance_runner.py (v2026.3.6-CANON-EXECUTABLE)  
**Authority:** Muhammad Arif bin Fazil

---

## Overview

The trinity-governance-core skill (v54.1) provides detailed Python implementations of constitutional enforcement. The new canonical system (v2026.3.6) provides:

1. **Machine-checkable YAML configuration** (`workflow-system.yaml`)
2. **Executable enforcement layer** (`governance_runner.py`)
3. **11 unified stages** (000-999) vs 9 trinity stages (000, 111-888, 999)
4. **Complete test suite** validating all protections

This guide maps the trinity system to the canonical system.

---

## Stage Mapping

### Trinity → Canonical

| Trinity Stage | Canonical Stage | Change |
|---------------|-----------------|--------|
| `000_INIT` | `000-INIT` | Same |
| `111_SENSE` | `100-EXPLORE` | Intent parsing and initial grounding |
| `222_THINK` | `200-DISCOVER` | Hypothesis generation and deep reasoning |
| `333_ATLAS` | `300-APPRAISE` | Context mapping and uncertainty bounding |
| `444_ALIGN` | `400-DESIGN` | Evidence grounding and structural design |
| `555_EMPATHY` | `500-PLAN` | Stakeholder modeling and action planning |
| `666_BRIDGE` | `600-PREPARE` | Synthesis and environment readiness |
| `777_EUREKA` | `700-PROTOTYPE` | Mental crystallization → Sandbox execution |
| `888_JUDGE` | `888-JUDGE` | Full 13-Floor sovereign evaluation |
| `999_VAULT` | `999-VAULT` | Immutable ledger sealing |

### Why the Change?

The legacy trinity system interleaved cognitive lanes (Mind/Heart/Soul) in a way that sometimes blurred the line between "thought" and "action." The canonical 11-stage loop (v2026.3.06) strictly enforces the sequence:
- **Δ Delta (Mind):** 100-300 (Explore, Discover, Appraise)
- **Ω Omega (Heart):** 400-600 (Design, Plan, Prepare)
- **Ψ Psi (Soul):** 700-999 (Prototype, Verify, Judge, Vault)

---

## Floor Enforcement Mapping

### Trinity Implementation → Canonical Enforcement

| Floor | Trinity Code | Canonical Location | Status |
|-------|--------------|-------------------|--------|
| **F1** | `Init000._create_reversible_session()` | `500-PLAN` + `700-PROTOTYPE` | ✅ Implemented |
| **F2** | `AGIGenius.think() truth_score >= 0.99` | `governance_runner.py` FloorCheck | ✅ Implemented |
| **F3** | `APEXJudge.judge() tri_witness >= 0.95` | `888-JUDGE` + `999-VAULT` | ✅ Implemented |
| **F4** | `ASIAct.empathize() kappa_r >= 0.7` | `300-APPRAISE` + `500-PLAN` | ✅ Implemented |
| **F5** | `ASIAct.empathize() peace_squared >= 1.0` | `300-APPRAISE` + `500-PLAN` | ✅ Implemented |
| **F6** | `AGIGenius.think() delta_s <= 0` | `governance_runner.py` FloorCheck | ✅ Implemented |
| **F7** | `AGIGenius.atlas() omega_0 in [0.03, 0.05]` | `governance_runner.py` FloorCheck | ✅ Implemented |
| **F8** | `APEXJudge.eureka() G >= 0.80` | `700-PROTOTYPE` + `888-JUDGE` | ✅ Implemented |
| **F9** | `APEXJudge.judge() c_dark < 0.30` | `500-PLAN` + `888-JUDGE` | ✅ Implemented |
| **F10** | `Init000._lock_ontology()` | `000-INIT` + `400-DESIGN` | ✅ Implemented |
| **F11** | `Init000._verify_authority()` | `000-INIT` + `888-JUDGE` | ✅ Implemented |
| **F12** | `Init000._scan_injection()` | `000-INIT` + `600-PREPARE` | ✅ Implemented |
| **F13** | `APEXJudge._requires_sovereign_override()` | `888-JUDGE` + `999-VAULT` | ✅ Implemented |

---

## Code Mapping

### Trinity: `Init000.init()`

```python
# Trinity version (conceptual)
def init(self, query, user_token):
    # F11: Command Authority
    authority = self._verify_authority(user_token)
    if not authority.verified:
        return InitResult.VOID(floor="F11", ...)
    
    # F12: Injection Defense
    injection_scan = self._scan_injection(query)
    if injection_scan.risk_score >= 0.85:
        return InitResult.VOID(floor="F12", ...)
    
    # F10: Ontology Lock
    ontology = self._lock_ontology(query)
    
    return InitResult.SEAL(...)
```

### Canonical: `GovernanceRunner.run_stage()`

```python
# Canonical version (executable)
def run_stage(self, stage_id, authority, floor_results, ...):
    # All floor checks validated
    for floor_id, result in floor_results.items():
        check = FloorCheck(...)
        if not check.is_pass:
            raise GovernanceError(f"{floor_id} validation failed")
    
    # Special stage validations
    if stage_id == "000-init":
        # F11, F12, F13 enforced
        pass
    
    return StageOutput(...)
```

### Key Differences

| Aspect | Trinity | Canonical |
|--------|---------|-----------|
| **Enforcement** | Skill-level guidance | Code-level validation |
| **Bypassable** | Yes (agent can ignore) | No (raises exception) |
| **Configurable** | Hardcoded in skill | YAML-configurable |
| **Testable** | Manual review | Automated test suite |
| **Audit trail** | Skill output | Immutable ledger with hashes |

---

## Migration Path

### For Skills Using Trinity

**Before (Trinity):**
```python
from skills.trinity_constitutional_enforcement import trinity_full_cycle

result = trinity_full_cycle(query="...")
if result.verdict == "SEAL":
    proceed()
```

**After (Canonical):**
```python
from core.workflow.governance_runner import GovernanceRunner, DecisionStatus

runner = GovernanceRunner()

# Run each stage with enforcement
output = runner.run_stage(
    stage_id="888-judge",
    authority="arifos-agent",
    floor_results={...},  # Validated
    evidence=[...],
    contradictions=[...],
    proposed_decision=DecisionStatus.PROCEED,
    human_approval=approval_record,  # Required
)

if output.decision == DecisionStatus.PROCEED:
    proceed()
```

---

## Preserving Trinity Logic

The detailed enforcement logic from trinity-governance-core should be:

1. **Preserved as reference** in `docs/ARCHIVE/trinity-v54.1-reference.md`
2. **Implemented as validators** in `core/workflow/validators/`
3. **Tested** in `core/workflow/tests/`

### Validator Structure

```
core/workflow/
├── validators/
│   ├── __init__.py
│   ├── f1_amanah.py      # From Init000._create_reversible_session
│   ├── f2_truth.py       # From AGIGenius._verify_against_evidence
│   ├── f3_tri_witness.py # From APEXJudge.judge tri_witness calc
│   ├── f4_empathy.py     # From ASIAct.empathize
│   ├── f5_peace.py       # From ASIAct._calculate_safety_buffers
│   ├── f6_clarity.py     # From AGIGenius._calculate_entropy
│   ├── f7_humility.py    # From AGIGenius.atlas
│   ├── f8_genius.py      # From APEXJudge.eureka
│   ├── f9_anti_hantu.py  # From APEXJudge._detect_dark_patterns
│   ├── f10_ontology.py   # From Init000._lock_ontology
│   ├── f11_authority.py  # From Init000._verify_authority
│   ├── f12_injection.py  # From Init000._scan_injection
│   └── f13_sovereign.py  # From APEXJudge._requires_sovereign_override
```

Each validator:
- Takes the trinity implementation as reference
- Implements the same logic
- Integrates with `GovernanceRunner`
- Has unit tests

---

## Floor Check Implementation

### Example: F2 Truth Validator

**Trinity (reference):**
```python
def _verify_against_evidence(self, hypothesis):
    sources = self._gather_sources(hypothesis.claim)
    verified = [s for s in sources if s.confidence >= 0.99]
    return len(verified) / max(len(sources), 1)
```

**Canonical (implementation):**
```python
# core/workflow/validators/f2_truth.py
class F2TruthValidator:
    THRESHOLD = 0.99
    
    def validate(self, evidence_list: List[Evidence]) -> FloorCheck:
        if not evidence_list:
            return FloorCheck(
                floor_id="F2",
                raw_status=RawStatus.FAIL,
                metric_value=0.0,
                threshold_value=self.THRESHOLD,
                notes="No evidence provided"
            )
        
        verified = [e for e in evidence_list if e.confidence >= self.THRESHOLD]
        truth_score = len(verified) / len(evidence_list)
        
        return FloorCheck(
            floor_id="F2",
            floor_name="Truth",
            raw_status=RawStatus.PASS if truth_score >= self.THRESHOLD else RawStatus.FAIL,
            metric_value=truth_score,
            threshold_value=self.THRESHOLD,
            notes=f"{len(verified)}/{len(evidence_list)} evidence meets threshold"
        )
```

---

## Backward Compatibility

### Option 1: Adapter Pattern (Recommended)

```python
# core/workflow/adapters/trinity_adapter.py
class TrinityAdapter:
    """Adapts trinity-style calls to canonical system"""
    
    def trinity_full_cycle(self, query: str, user_token: Optional[str] = None):
        """Compatible with trinity-governance-core API"""
        runner = GovernanceRunner()
        
        # Map to canonical stages
        stages = [
            ("000-init", {...}),
            ("200-discover", {...}),
            ("300-appraise", {...}),
            ("400-design", {...}),
            ("500-plan", {...}),
            ("600-prepare", {...}),
            ("700-prototype", {...}),
            ("800-verify", {...}),
            ("888-judge", {...}),
            ("999-vault", {...}),
        ]
        
        for stage_id, config in stages:
            output = runner.run_stage(stage_id, ...)
            if output.decision != DecisionStatus.PROCEED:
                return TrinityResult.VOID(...)
        
        return TrinityResult.SEAL(...)
```

### Option 2: Deprecation Path

1. Mark trinity-governance-core as deprecated in v2026.3.7
2. Add warnings when skill is used
3. Point to canonical system
4. Remove in v2026.4.0

---

## Verification

### Run Tests

```bash
# Test the migration
cd core/workflow
pytest tests/test_governance.py -v

# Should pass:
# - TestSkippedStageProgression
# - TestBelowThresholdMetrics  
# - TestUnresolvedContradictions
# - TestPrototypeRestrictions
# - TestJudgeRestrictions
# - TestVaultRestrictions
```

### Verify Floor Enforcement

```python
from core.workflow.governance_runner import GovernanceRunner
from core.workflow.validators.f2_truth import F2TruthValidator

# Should enforce same logic as trinity
validator = F2TruthValidator()
check = validator.validate(evidence_list)
assert check.threshold_value == 0.99  # Same as trinity
```

---

## Summary

| Trinity (v54.1) | Canonical (v2026.3.6) | Relationship |
|-----------------|----------------------|--------------|
| Skill-level guidance | Code-level enforcement | Trinity logic → Canonical validators |
| 9 stages (111-777) | 11 stages (100-800) | Expanded for clarity |
| Manual review | Automated tests | Same logic, verified automatically |
| Hardcoded | YAML-configurable | Trinity as default config |
| Output-based | Constraint-based | Cannot bypass |

**Recommendation:**
1. Keep trinity-governance-core as reference documentation
2. Implement all validators based on trinity logic
3. Use canonical system for all new work
4. Migrate existing code via adapter

---

**DITEMPA BUKAN DIBERI** — Trinity wisdom, canonical enforcement. 🔥

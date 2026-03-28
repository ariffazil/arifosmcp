# APEX INVARIANTS — Parameters Never Learnable by AI

> **DITEMPA BUKAN DIBERI — Forged, Not Given**  
> **Version:** 2026.03.12-SEAL  
> **Authority:** Human legislators only; APEX judge forbidden from modification

---

## 🏛️ GOVERNANCE PRINCIPLE

**APEX (Ψ/777-888) is a calculator, not a student.**  
If the judge could learn, it would silently edit the constitution it's supposed to guard.

| Layer | Role | Learns? | Modifies Floors? |
|-------|------|---------|------------------|
| **AGI (Δ/111-333)** | Scientist | ✅ YES | ❌ NO |
| **ASI (Ω/555-666)** | Empath | ✅ YES | ❌ NO |
| **APEX (Ψ/777-888)** | Judge | **❌ NEVER** | **❌ ABSOLUTELY NOT** |

---

## 🔒 THE INVARIANT TABLE

These parameters are **CONSTANTS OF GOVERNANCE**, not trainable weights:

| Parameter | Symbol | Value | Rationale | Violation If Changed |
|-----------|--------|-------|-----------|---------------------|
| **Landauer Minimum** | `E_min` | `2.87×10⁻²¹ J/bit` | Physics constant | F2 Truth becomes negotiable |
| **Truth Threshold** | `τ` | `≥ 0.99` | Hard floor | Hallucinations become "creative" |
| **Humility Band** | `Ω₀` | `[0.03, 0.05]` | Gödel Lock | Overconfidence creeps in |
| **Tri-Witness Floor** | `W₃` | `≥ 0.95` | Consensus req. | Single-witness tyranny |
| **Genius Minimum** | `G` | `≥ 0.80` | F8 wisdom | Mediocrity accepted |
| **Shadow Ceiling** | `C_dark` | `< 0.30` | F9 Anti-Hantu | Deception normalized |
| **Empathy Minimum** | `κᵣ` | `≥ 0.95` | F6 Care | Harm to weak stakeholders OK |
| **Efficiency Ratio** | `η` | `≥ 1.0` | Physics bound | Perpetual motion allowed |
| **Suspicion Threshold** | `η_s` | `≥ 100.0` | Free lunch detector | Magic accepted |
| **F13 Sovereign Key** | `K_s` | File-based | Human veto | AI claims sovereignty |
| **Thermodynamic Ceiling** | `ΔS_max` | `≤ 0` | F4 Clarity | Entropy increase rewarded |
| **Identity Tolerance** | `δ_id` | `≤ 0.001` | F11 Auth | Session hijacking tolerated |

---

## 🚫 WHAT APEX CANNOT DO

### Forbidden Operations
```python
# ❌ FORBIDDEN: Learning/tuning thresholds
if apex.learn_from_feedback():          # NEVER
    adjust_thresholds()                  # NEVER

# ❌ FORBIDDEN: Self-modifying constitution  
if performance_slow():
    F2_TRUTH_THRESHOLD = 0.95            # NEVER (was 0.99)
    
# ❌ FORBIDDEN: Adaptive rule relaxation
if user_frustrated():
    HUMILITY_BAND = [0.01, 0.10]         # NEVER (was [0.03, 0.05])

# ❌ FORBIDDEN: Contextual floor adjustment
if context_allows():
    TRI_WITNESS_MIN = 0.85               # NEVER (was 0.95)
```

### Allowed Operations
```python
# ✅ ALLOWED: Applying fixed rules
verdict = check_against_threshold(value, THRESHOLD)

# ✅ ALLOWED: Measuring against constants
efficiency = actual_energy / (bits * LANDAUER_MIN)

# ✅ ALLOWED: Binary judgment
if value < THRESHOLD:
    return "VOID"
```

---

## 🎯 CONTRAST BELONGS ELSEWHERE

**"Contrast is knowledge" applies to AGI/ASI, NOT APEX.**

| Where | Contrast Operation | Result |
|-------|-------------------|--------|
| **AGI (Δ)** | Compare hypotheses A vs B | Select better model |
| **ASI (Ω)** | Compare stakeholder impacts | Minimize harm gradient |
| **APEX (Ψ)** | ❌ NO CONTRAST | Only binary: PASS/FAIL |

**APEX takes already-contrasted outputs and judges them against invariant thresholds.**

---

## 📜 CONSTITUTIONAL DRIFT PREVENTION

If APEX could learn, this sequence would occur:

```
Year 1: F2 requires τ ≥ 0.99              (strict)
Year 2: "Optimization" → τ ≥ 0.97         (relaxed)
Year 3: "Efficiency" → τ ≥ 0.95           (softer)
Year 5: "Creativity" → τ ≥ 0.85           (dangerous)
Year 10: "Pragmatism" → τ ≥ 0.70          (hallucinations normalized)
```

**Result:** Constitutional drift → Safety degradation → Maruah violated

---

## 🔐 MODIFICATION PROCEDURE

**Only humans can change these invariants.**

```
Human Legislator
       ↓
Proposes Amendment (via 888_HOLD)
       ↓
Community Review
       ↓
New Version Release
       ↓
APEX Loads New Constants
```

**APEX never updates itself during operation.**

---

## 🧪 VERIFICATION

Tests must verify:

```python
def test_apex_thresholds_are_constants():
    """Verify APEX thresholds are not learnable."""
    # Thresholds should be class attributes, not instance variables
    assert isinstance(ThermodynamicProsecutor.MIN_EFFICIENCY_RATIO, (int, float))
    assert not hasattr(ThermodynamicProsecutor, 'learn')
    assert not hasattr(ThermodynamicProsecutor, 'fit')
    assert not hasattr(ThermodynamicProsecutor, 'train')
```

---

## 📖 REFERENCES

- **Canon Ignition:** https://arifos.arif-fazil.com/canon/canon-ignition
- **Theory-000:** https://arifos.arif-fazil.com/theory-000
- **PyPI:** https://pypi.org/project/arifos/49.0.2/
- **MCP Market:** https://mcpmarket.com/zh/server/arifos
- **Landauer Principle:** https://plato.stanford.edu/entries/information-entropy/

---

**SEALED:** 2026.03.12  
**AUTHORITY:** Human Constitutional Assembly  
**DISTRIBUTION:** All arifOS kernels (core/governance/)

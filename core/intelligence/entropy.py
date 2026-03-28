"""
arifOS 333 SYNTHESIS: Entropy Calculator
Measures thermodynamic ΔS for every agent action.
"""

def measure_entropy(before_state, after_state):
    # ΔS = S_final - S_initial
    # In arifOS, ΔS must be ≤ 0
    return after_state.entropy - before_state.entropy

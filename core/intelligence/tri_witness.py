"""
arifOS 333 WITNESS: Tri-Witness Calculator
Computes W3 = (H * A * E)^(1/3)
"""

def compute_w3(human_score, ai_score, earth_score):
    return (human_score * ai_score * earth_score) ** (1/3)

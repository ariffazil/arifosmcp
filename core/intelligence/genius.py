"""
arifOS 333 WITNESS: Genius Scorer
Computes G-Score based on metabolic efficiency.
"""

def calculate_genius(entropy_delta, clarity_score):
    # Genius is high clarity + negative entropy
    return clarity_score * (1 - entropy_delta)

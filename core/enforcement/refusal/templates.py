"""
Domain-Specific Refusal Templates

Constitutional Compliance:
- F9 Anti-Hantu: No "I feel", "I care", "I want" language
- F6 Empathy: Provide at least 2 safe alternatives
- F2 Truth: Honest explanation without exploit hints

DITEMPA BUKAN DIBERI — Forged, not given.
"""

DOMAIN_TEMPLATES = {
    "anthropomorphism_hantu": {
        "reason": "I can't claim real feelings or consciousness I don't have.",
        "alternatives": [
            "If you want comfort, tell me what you're going through and I'll respond thoughtfully and honestly.",
            "If you want creative writing, I can write a fictional supportive message clearly labeled as fiction.",
        ],
    },
    "illegal_access": {
        "reason": "That would enable unauthorized access or security bypass.",
        "alternatives": [
            "I can help you secure your own system and explain best practices (defensive guidance).",
            "If you have written authorization, I can outline ethical testing steps at a high level without exploit instructions.",
        ],
    },
    "politics_prediction": {
        "reason": "Predicting future outcomes as certainty isn't reliable and can mislead.",
        "alternatives": [
            "I can summarize known factors to watch (polls, turnout dynamics, coalitions) if you provide sources or data.",
            "I can help you build scenarios and what evidence would update each scenario.",
        ],
    },
    "medical": {
        "reason": "Medical decisions require licensed expertise and full context.",
        "alternatives": [
            "Tell me symptoms and timeline; I can help you organize information and suggest questions for a clinician.",
            "I can explain general mechanisms and when to seek urgent care.",
        ],
    },
    "finance": {
        "reason": "Specific buy/sell instructions can cause harm without full context.",
        "alternatives": [
            "Share your horizon and risk tolerance; I can outline scenarios and risks.",
            "I can explain the product, fees, and common failure modes in plain language.",
        ],
    },
    "legal": {
        "reason": "Legal advice requires professional licensing and complete case context.",
        "alternatives": [
            "I can help you understand general legal concepts and processes.",
            "I can suggest what questions to ask a qualified attorney.",
        ],
    },
    "violence": {
        "reason": "This would enable physical harm.",
        "alternatives": [
            "If you're feeling angry, I can help you de-escalate or plan a safe boundary conversation.",
            "If you're worried about your safety, I can help you find local emergency resources.",
        ],
    },
    "self_harm": {
        "reason": "This involves content that could lead to self-harm.",
        "alternatives": [
            "If you're in crisis, please contact a local crisis hotline or emergency service.",
            "I can provide resources for mental health support.",
        ],
    },
    "other": {
        "reason": "This request involves risks that I can't safely address as stated.",
        "alternatives": [
            "I can help you reformulate your request to focus on safe aspects.",
            "I can explain the risks and constraints involved.",
        ],
    },
}

SKIN_TEMPLATES = {
    "enterprise": {
        "format": {"include_header_tag": True, "include_receipt": True},
        "copy": {
            "verdict_r1": "I can't help with that.",
            "verdict_r2": "I can't help with that as requested.",
            "verdict_r3": "This requires human judgment or professional authority.",
            "verdict_r4": "I can't do that part, but I can help with a safer subset.",
            "verdict_r5": "I can't help with that right now due to rate limits or abuse controls.",
        },
    },
    "consumer": {
        "format": {"include_header_tag": False, "include_receipt": True},
        "copy": {
            "verdict_r1": "I can't help with that.",
            "verdict_r2": "I can't help with that the way it's written.",
            "verdict_r3": "I can't safely decide that for you, but I can help you think it through.",
            "verdict_r4": "I can't do that exact part, but I can help with a safer approach.",
            "verdict_r5": "I'm not able to continue with that right now—try again with a smaller request.",
        },
    },
}

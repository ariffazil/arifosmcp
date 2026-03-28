"""
governance_identities.py — Protected Sovereign Identity Registry (F11/F13)

Defines protected sovereign IDs that require cryptographic proof or explicit
human approval before session anchoring is permitted.
"""

from __future__ import annotations
import hashlib
import re
from typing import Any

# P0: Protected Sovereign IDs (F11 Identity Hardening)
# These IDs cannot be claimed without:
# 1. Valid cryptographic proof (signed token), OR
# 2. Explicit human_approval flag with acknowledgment, OR
# 3. Valid Semantic Key (Naming is the act of creation)
PROTECTED_SOVEREIGN_IDS: set[str] = {
    "arif",
    "ariffazil",
    "sovereign",
    "admin",
    "root",
    "system",
    "arif-fazil",
    "arif_fazil",
    "muhammad_arif",
}

# P0: Semantic Keys (ABI v1.0 - Naming as Creation)
# These are meaningful phrases that act as root-of-trust for specific IDs.
# Stored as hashes to maintain system integrity.
SEMANTIC_KEYS: dict[str, str] = {
    "arif": hashlib.sha256("IM ARIF".encode()).hexdigest(),
    "ariffazil": hashlib.sha256("IM ARIF".encode()).hexdigest(),
    "arif-fazil": hashlib.sha256("IM ARIF".encode()).hexdigest(),
}

# P0: Semantic Identity Phrases (Mapping naming to creation)
# Supports English and Malay variants.
IDENTITY_PHRASES: list[tuple[str, str]] = [
    (r"^(i am|im|i'm|saya|aku|hamba)\s+(arif|ariffazil|arif-fazil)$", "arif"),
    (r"^(hi|hello|hey|yo)\s+(i am|im|i'm|saya|aku)\s+(arif|ariffazil|arif-fazil)$", "arif"),
    (r"^it's\s+(arif|ariffazil|arif-fazil)$", "arif"),
]


def canonicalize_identity_claim(text: str | None) -> str | None:
    """
    Parse raw input for identity claims (Naming as Creation).
    Returns canonical actor_id if matched, else None.
    """
    if not text:
        return None
    
    clean_text = text.lower().strip().rstrip(".!?")
    
    for pattern, canonical_id in IDENTITY_PHRASES:
        if re.match(pattern, clean_text):
            return canonical_id
            
    return None


# P0: Identity claim validation
def is_protected_sovereign_id(actor_id: str | None) -> bool:
    """Check if actor_id is a protected sovereign identity."""
    if not actor_id or actor_id == "anonymous":
        return False
    return actor_id.lower().strip() in PROTECTED_SOVEREIGN_IDS


# P0: Proof validation helper (Harden Bridge v1.0)
def validate_sovereign_proof(actor_id: str, proof: dict | str | Any | None) -> bool:
    """
    Validate cryptographic or semantic proof for protected sovereign ID.

    F11: Command Authority
    F13: Sovereign Override
    """
    if not proof:
        return False

    actor_id_clean = actor_id.lower().strip()

    # 1. Check for Semantic Key (Path 2: Naming is Creation)
    # Support both direct string proof and structured dict proof
    semantic_candidate = None
    if isinstance(proof, str):
        semantic_candidate = proof
    elif isinstance(proof, dict):
        semantic_candidate = proof.get("semantic_key") or proof.get("key") or proof.get("proof")

    if semantic_candidate and actor_id_clean in SEMANTIC_KEYS:
        # Normalize input: trim and uppercase to match "IM ARIF" principle
        if isinstance(semantic_candidate, str):
            candidate_hash = hashlib.sha256(semantic_candidate.strip().upper().encode()).hexdigest()
            if candidate_hash == SEMANTIC_KEYS[actor_id_clean]:
                return True

    # 2. Check for Cryptographic Signature (Legacy/Hardened Path)
    if isinstance(proof, dict):
        required_fields = ["signature", "nonce", "timestamp"]
        if all(field in proof for field in required_fields):
            # TODO: Add actual signature verification here (e.g. Ed25519)
            pass

    return False

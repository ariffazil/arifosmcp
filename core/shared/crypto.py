"""
arifOS v60: Cryptographic Primitives
=====================================

Ed25519 signatures, Merkle trees, SHA-256 hashing.

Enforces: F1 (Amanah - Reversibility), F11 (Command Auth)

Version: v60.0-FORGE
Author: Muhammad Arif bin Fazil
License: AGPL-3.0-only
DITEMPA BUKAN DIBERI 💎🔥🧠
"""

import hashlib
import time
import uuid

# ============================================================================
# SESSION ID GENERATION (F1 Amanah - Traceable)
# ============================================================================


def generate_session_id() -> str:
    """
    Generate cryptographic session UUID.

    Formula: UUID4 with entropy from system time + random seed

    Returns:
        session_id: Unique identifier for audit trail
    """
    # Seed with current timestamp for entropy
    timestamp = int(time.time() * 1000000)
    base_uuid = uuid.uuid4()

    # Combine UUID with timestamp hash for extra entropy
    combined = f"{base_uuid}_{timestamp}"
    session_hash = hashlib.sha256(combined.encode()).hexdigest()[:16]

    return f"session_{session_hash}_{base_uuid.hex[:8]}"


# ============================================================================
# SHA-256 HASHING (F1 Amanah - Immutability)
# ============================================================================


def sha256_hash(data: str) -> str:
    """
    Compute SHA-256 hash for immutable audit.

    Args:
        data: String to hash

    Returns:
        hex_digest: 64-character hex string
    """
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def sha256_hash_dict(data: dict) -> str:
    """
    Compute SHA-256 hash of dictionary (sorted for consistency).

    Args:
        data: Dictionary to hash

    Returns:
        hex_digest: Hash of JSON representation
    """
    import json

    # Sort keys for deterministic hashing
    json_str = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return sha256_hash(json_str)


# ============================================================================
# ED25519 SIGNATURES (F11 Command Auth)
# ============================================================================


def ed25519_sign(message: str, private_key: str) -> str:
    """
    Sign message with Ed25519 private key.

    F11 Command Auth: Cryptographic proof of identity.

    Args:
        message: Data to sign
        private_key: Ed25519 private key (hex)

    Returns:
        signature: Ed25519 signature (hex)

    Note: This is a placeholder implementation.
          In production, use cryptography.hazmat.primitives.asymmetric.ed25519
    """
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ed25519

        # Convert hex private key to bytes
        private_key_bytes = bytes.fromhex(private_key)

        # Load private key
        private_key_obj = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)

        # Sign message
        signature = private_key_obj.sign(message.encode("utf-8"))

        return signature.hex()

    except (ImportError, ValueError):
        # Fallback: SHA-256 HMAC simulation (NOT SECURE FOR PRODUCTION)
        # ValueError fires when private_key is a passphrase rather than hex bytes
        import hmac

        return hmac.new(private_key.encode(), message.encode(), hashlib.sha256).hexdigest()


def ed25519_verify(message: str, signature: str, public_key: str) -> bool:
    """
    Verify Ed25519 signature.

    F11 Command Auth: Validate cryptographic proof.

    Args:
        message: Original data
        signature: Ed25519 signature (hex)
        public_key: Ed25519 public key (hex)

    Returns:
        valid: True if signature is valid
    """
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric import ed25519

        # Convert hex to bytes
        public_key_bytes = bytes.fromhex(public_key)
        signature_bytes = bytes.fromhex(signature)

        # Load public key
        public_key_obj = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)

        # Verify signature
        try:
            public_key_obj.verify(signature_bytes, message.encode("utf-8"))
            return True
        except InvalidSignature:
            return False

    except ImportError:
        # Fallback: Always return True in dev mode
        # TODO: Remove this in production!
        return True


def generate_ed25519_keypair() -> tuple[str, str]:
    """
    Generate Ed25519 key pair.

    Returns:
        (private_key_hex, public_key_hex)
    """
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ed25519

        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        # Serialize to bytes
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
        )

        return (private_bytes.hex(), public_bytes.hex())

    except ImportError:
        # Fallback: Generate random hex strings (NOT SECURE FOR PRODUCTION)
        private_hex = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
        public_hex = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
        return (private_hex, public_hex)


# ============================================================================
# MERKLE TREE (F1 Amanah - Tamper-Evident Chain)
# ============================================================================


def merkle_hash_pair(left: str, right: str) -> str:
    """
    Hash a pair of Merkle tree nodes.

    Args:
        left: Left node hash
        right: Right node hash

    Returns:
        parent_hash: Combined hash
    """
    combined = left + right
    return sha256_hash(combined)


def merkle_root(entries: list[str]) -> str:
    """
    Compute Merkle root from list of hashes.

    F1 Amanah: Tamper-evident data structure.

    Algorithm:
    1. Hash each entry
    2. Pair adjacent hashes and hash them
    3. Repeat until single root remains

    Args:
        entries: List of data strings

    Returns:
        merkle_root: Single root hash
    """
    if not entries:
        return sha256_hash("")

    # Hash all entries first
    hashes = [sha256_hash(entry) for entry in entries]

    # Build tree bottom-up
    while len(hashes) > 1:
        new_level = []

        # Process pairs
        for i in range(0, len(hashes), 2):
            left = hashes[i]
            right = hashes[i + 1] if i + 1 < len(hashes) else hashes[i]
            parent = merkle_hash_pair(left, right)
            new_level.append(parent)

        hashes = new_level

    return hashes[0]


def verify_merkle_proof(
    leaf: str,
    proof: list[tuple[str, str]],  # (hash, position) where position is 'left'|'right'
    root: str,
) -> bool:
    """
    Verify Merkle proof for a leaf.

    Args:
        leaf: Leaf data to verify
        proof: List of (sibling_hash, position) pairs
        root: Expected Merkle root

    Returns:
        valid: True if proof is valid
    """
    current_hash = sha256_hash(leaf)

    for sibling_hash, position in proof:
        if position == "left":
            current_hash = merkle_hash_pair(sibling_hash, current_hash)
        else:
            current_hash = merkle_hash_pair(current_hash, sibling_hash)

    return current_hash == root


# ============================================================================
# NONCE MANAGEMENT (F11 Command Auth - Replay Protection)
# ============================================================================


class NonceManager:
    """
    Nonce manager for replay attack prevention.

    F11 Command Auth: Each command must have unique nonce.
    """

    def __init__(self, window_seconds: int = 300):
        """
        Initialize nonce manager.

        Args:
            window_seconds: Time window for nonce validity (default 5 minutes)
        """
        self.window_seconds = window_seconds
        self._used_nonces: dict[str, float] = {}

    def generate_nonce(self) -> str:
        """
        Generate a new nonce.

        Returns:
            nonce: Unique nonce string
        """
        timestamp = int(time.time())
        random_part = uuid.uuid4().hex[:16]
        return f"{timestamp}_{random_part}"

    def validate_nonce(self, nonce: str) -> bool:
        """
        Validate nonce (check if unused and within time window).

        Args:
            nonce: Nonce to validate

        Returns:
            valid: True if nonce is valid and unused
        """
        # Parse timestamp from nonce
        try:
            timestamp_str = nonce.split("_")[0]
            nonce_time = int(timestamp_str)
        except (ValueError, IndexError):
            return False

        current_time = int(time.time())

        # Check time window
        if current_time - nonce_time > self.window_seconds:
            return False

        # Check if already used
        if nonce in self._used_nonces:
            return False

        # Mark as used
        self._used_nonces[nonce] = current_time

        # Cleanup old nonces
        self._cleanup_old_nonces(current_time)

        return True

    def _cleanup_old_nonces(self, current_time: int) -> None:
        """Remove nonces outside time window."""
        cutoff = current_time - self.window_seconds
        self._used_nonces = {
            nonce: timestamp
            for nonce, timestamp in self._used_nonces.items()
            if timestamp >= cutoff
        }


# ============================================================================
# EXPORT PUBLIC API
# ============================================================================

__all__ = [
    # Session
    "generate_session_id",
    # Hashing
    "sha256_hash",
    "sha256_hash_dict",
    # Ed25519
    "ed25519_sign",
    "ed25519_verify",
    "generate_ed25519_keypair",
    # Merkle
    "merkle_root",
    "merkle_hash_pair",
    "verify_merkle_proof",
    # Nonce
    "NonceManager",
]

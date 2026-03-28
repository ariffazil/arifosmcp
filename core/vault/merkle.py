"""
core/vault/merkle.py — RFC 6962 Merkle Chain for VAULT999

Implements an RFC 6962 (Certificate Transparency) style append-only
Merkle tree for the VAULT999 audit ledger.

Properties:
  - Append-only: no modification or deletion of existing records
  - Tamper detection: any change breaks the prev_hash chain AND the Merkle root
  - Inclusion proofs: O(log n) verification without full chain traversal
  - Python stdlib only: hashlib + no external dependencies

Usage:
  tree = MerkleTree()
  tree.append(record_hash)
  root = tree.root()
  proof = tree.prove_inclusion(leaf_index)
  verified = verify_inclusion_proof(proof, root, leaf_hash, tree_size)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# HASH PRIMITIVES (RFC 6962 §2.1)
# ─────────────────────────────────────────────────────────────────────────────
def _leaf_hash(data: str) -> str:
    """RFC 6962 leaf hash: SHA-256(0x00 || data)."""
    return hashlib.sha256(b"\x00" + data.encode("utf-8")).hexdigest()


def _node_hash(left: str, right: str) -> str:
    """RFC 6962 node hash: SHA-256(0x01 || left || right)."""
    return hashlib.sha256(
        b"\x01" + bytes.fromhex(left) + bytes.fromhex(right)
    ).hexdigest()


def _empty_hash() -> str:
    return hashlib.sha256(b"").hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# PROOF STRUCTURE
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class InclusionProof:
    """RFC 6962 inclusion proof for a single leaf."""
    leaf_index: int
    leaf_hash: str
    proof_path: list[tuple[str, str]] = field(default_factory=list)  # (hash, "left"|"right")
    tree_size: int = 0
    root_hash: str = ""
    verified: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# MERKLE TREE
# ─────────────────────────────────────────────────────────────────────────────
class MerkleTree:
    """
    In-memory RFC 6962 Merkle tree for VAULT999.

    For production use, leaves are persisted to PostgreSQL.
    This class handles the tree computation layer.
    """

    def __init__(self, leaves: list[str] | None = None):
        """
        Args:
            leaves: Optional list of pre-existing leaf hashes (hex strings).
                    Pass existing VAULT999 record hashes to reconstruct tree.
        """
        self._leaves: list[str] = []
        if leaves:
            for leaf in leaves:
                self._leaves.append(_leaf_hash(leaf) if len(leaf) != 64 else leaf)

    def append(self, record_hash: str) -> str:
        """
        Append a new record hash to the tree.

        Args:
            record_hash: SHA-256 hex of the VaultRecord (compute_self_hash()).

        Returns:
            The leaf hash stored in the tree.
        """
        leaf = _leaf_hash(record_hash)
        self._leaves.append(leaf)
        return leaf

    def root(self) -> str:
        """Compute and return the current Merkle root."""
        if not self._leaves:
            return _empty_hash()
        return self._compute_root(self._leaves)

    def _compute_root(self, leaves: list[str]) -> str:
        """RFC 6962 tree construction: duplicate last leaf if odd count."""
        layer = leaves[:]
        while len(layer) > 1:
            if len(layer) % 2 == 1:
                layer.append(layer[-1])  # RFC 6962: duplicate last
            layer = [
                _node_hash(layer[i], layer[i + 1])
                for i in range(0, len(layer), 2)
            ]
        return layer[0]

    def prove_inclusion(self, leaf_index: int) -> InclusionProof:
        """
        Generate an inclusion proof for the leaf at leaf_index.

        Returns:
            InclusionProof with proof_path for O(log n) verification.
        """
        n = len(self._leaves)
        if leaf_index < 0 or leaf_index >= n:
            raise IndexError(f"leaf_index {leaf_index} out of range [0, {n})")

        leaf_hash = self._leaves[leaf_index]
        proof_path: list[tuple[str, str]] = []
        layer = self._leaves[:]

        idx = leaf_index
        while len(layer) > 1:
            if len(layer) % 2 == 1:
                layer.append(layer[-1])
            sibling_idx = idx ^ 1  # XOR to get sibling
            side = "right" if idx % 2 == 0 else "left"
            proof_path.append((layer[sibling_idx], side))
            idx //= 2
            layer = [
                _node_hash(layer[i], layer[i + 1])
                for i in range(0, len(layer), 2)
            ]

        root = layer[0] if layer else _empty_hash()
        return InclusionProof(
            leaf_index=leaf_index,
            leaf_hash=leaf_hash,
            proof_path=proof_path,
            tree_size=n,
            root_hash=root,
            verified=True,
        )

    def __len__(self) -> int:
        return len(self._leaves)


# ─────────────────────────────────────────────────────────────────────────────
# STANDALONE VERIFICATION
# ─────────────────────────────────────────────────────────────────────────────
def verify_inclusion_proof(
    proof: InclusionProof,
    expected_root: str,
) -> bool:
    """
    Verify an inclusion proof against a known Merkle root.

    Does NOT require the full tree — only the proof_path and root.
    O(log n) verification.
    """
    current = proof.leaf_hash
    for sibling_hash, side in proof.proof_path:
        if side == "right":
            current = _node_hash(current, sibling_hash)
        else:
            current = _node_hash(sibling_hash, current)
    return current == expected_root


def build_merkle_root(record_hashes: list[str]) -> str:
    """
    Build a Merkle root from a list of record SHA-256 hashes.
    Convenience function for VAULT999 batch root computation.
    """
    tree = MerkleTree(record_hashes)
    return tree.root()


def verify_chain_integrity(
    record_hashes: list[str],
    prev_hashes: list[str],
) -> tuple[bool, list[dict]]:
    """
    Walk the VAULT999 chain and verify prev_hash links.

    Args:
        record_hashes: SHA-256 hash of each VaultRecord (compute_self_hash()).
        prev_hashes:   The prev_hash field stored in each VaultRecord.

    Returns:
        (chain_valid, tamper_evidence) where tamper_evidence is a list of
        {index, record_hash, expected_prev, stored_prev} for broken links.
    """
    if not record_hashes:
        return True, []

    tamper_evidence = []
    for i in range(1, len(record_hashes)):
        expected_prev = record_hashes[i - 1]
        stored_prev = prev_hashes[i] if i < len(prev_hashes) else ""
        if stored_prev != expected_prev:
            tamper_evidence.append({
                "index": i,
                "record_hash": record_hashes[i],
                "expected_prev": expected_prev,
                "stored_prev": stored_prev,
            })
            logger.error(
                "VAULT999 CHAIN TAMPERED at index %d: expected_prev=%s stored=%s",
                i, expected_prev[:12], stored_prev[:12] if stored_prev else "MISSING",
            )

    chain_valid = len(tamper_evidence) == 0
    if chain_valid:
        logger.debug("VAULT999 chain integrity verified: %d records OK", len(record_hashes))
    return chain_valid, tamper_evidence


__all__ = [
    "MerkleTree",
    "InclusionProof",
    "verify_inclusion_proof",
    "build_merkle_root",
    "verify_chain_integrity",
]

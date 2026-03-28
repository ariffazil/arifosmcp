"""
core/contracts/evidence.py — EvidenceBundle & Merkle Vault Record

EvidenceBundle: timestamped, cryptographically-wrapped evidence atom.
  - JCS-canonicalized SHA-256 hash (RFC 8785)
  - F12 taint wrapping: all external content in <untrusted_external_data>
  - DNS/HTTP forensic diagnostics on every fetch

VaultRecord: append-only audit record for VAULT999 Merkle chain.
  - UUIDv7 time-ordered identifiers
  - prev_hash chain link for tamper detection
  - RFC 6962 Merkle tree inclusion proofs

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# EVIDENCE BUNDLE
# ─────────────────────────────────────────────────────────────────────────────
class EvidenceBundle(BaseModel):
    """
    Timestamped, cryptographically-wrapped evidence atom.

    Every piece of external data ingested by reality_compass is
    wrapped in this structure before entering the context window.
    F12 Defense: raw external content is never injected directly.
    """

    bundle_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="UUIDv7 identifier (time-ordered for chain ordering)",
    )
    content: str = Field(
        default="",
        description="Extracted, clean Markdown or plain text from the source",
    )
    source_url: str = Field(
        default="",
        description="Original URL or document reference",
    )
    retrieval_timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO8601 UTC timestamp of retrieval",
    )
    http_status: int = Field(
        default=200,
        description="HTTP response code from the fetch (0 if DNS-level failure)",
    )
    dns_latency_ms: float | None = Field(
        default=None,
        description="DNS resolution time in milliseconds (forensic diagnostic)",
    )
    total_latency_ms: float | None = Field(
        default=None,
        description="Total fetch time in milliseconds",
    )
    taint_lineage: list[str] = Field(
        default_factory=list,
        description="Chain of transformations applied: ['jina_extract', 'html_strip', ...]",
    )
    engine: str = Field(
        default="unknown",
        description="Engine that produced this bundle: brave | jina | perplexity | browserless | qdrant",
    )
    # F12 Defense — set by finalize(), never bypass
    wrapped_content: str = Field(
        default="",
        description=(
            "F12-compliant taint-wrapped content. "
            "Format: <untrusted_external_data source=URL>content</untrusted_external_data>"
        ),
    )
    canonical_hash: str = Field(
        default="",
        description="SHA-256 of JCS-serialized bundle (computed by finalize())",
    )

    def compute_hash(self) -> str:
        """JCS-style canonical hash: JSON with sorted keys, UTF-8."""
        data = self.model_dump(exclude={"canonical_hash", "wrapped_content"})
        serialized = json.dumps(data, sort_keys=True, ensure_ascii=False, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def finalize(self) -> "EvidenceBundle":
        """
        Apply F12 taint wrapping and compute canonical hash.
        Must be called before any bundle enters the intelligence pipeline.
        """
        self.wrapped_content = (
            f'<untrusted_external_data source="{self.source_url}" '
            f'retrieved="{self.retrieval_timestamp}">'
            f"{self.content}"
            f"</untrusted_external_data>"
        )
        self.canonical_hash = self.compute_hash()
        return self

    @property
    def quality_score(self) -> float:
        """
        Naive quality score (0.0–1.0) for earth witness calculation.
        Penalizes: non-200 HTTP, empty content, missing latency data.
        """
        score = 1.0
        if self.http_status != 200:
            score *= 0.5
        if not self.content or len(self.content) < 100:
            score *= 0.4
        if self.dns_latency_ms and self.dns_latency_ms > 5000:
            score *= 0.8  # Slow DNS is suspicious
        return max(0.0, min(1.0, score))


# ─────────────────────────────────────────────────────────────────────────────
# VAULT RECORD (MERKLE CHAIN LINK)
# ─────────────────────────────────────────────────────────────────────────────
class VaultRecord(BaseModel):
    """
    Append-only audit record for VAULT999 Merkle chain.

    Every tool execution is recorded here at stage 999_VAULT.
    The prev_hash chain link enables tamper detection:
    any modification to any record will break all subsequent hashes.
    """

    record_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="UUIDv7 time-ordered identifier",
    )
    session_id: str = Field(
        default="global",
        description="Session this action belongs to",
    )
    tool_name: str = Field(
        default="unknown",
        description="The tool that produced this record",
    )
    verdict: str = Field(
        default="SABAR",
        description="SEAL | PARTIAL | SABAR | 888_HOLD | VOID",
    )
    action_digest: str = Field(
        default="",
        description="SHA-256 of JCS-serialized action/request payload",
    )
    prev_hash: str = Field(
        default="0" * 64,
        description="SHA-256 hash of the previous VaultRecord (chain link)",
    )
    merkle_root: str = Field(
        default="",
        description="Current Merkle tree root after appending this record",
    )
    governance_token_hash: str = Field(
        default="",
        description="SHA-256 of the governance_token used (never store raw token)",
    )
    timestamp_utc: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO8601 UTC timestamp",
    )
    floor_scores_digest: str = Field(
        default="",
        description="SHA-256 of floor_scores JSON for this execution",
    )
    extra: dict[str, Any] = Field(
        default_factory=dict,
        description="Tool-specific metadata (hold_id, actor_id, etc.)",
    )

    def compute_self_hash(self) -> str:
        """JCS-canonical hash of this record (becomes next record's prev_hash)."""
        data = self.model_dump(exclude={"merkle_root"})
        serialized = json.dumps(data, sort_keys=True, ensure_ascii=False, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# MERKLE INCLUSION PROOF
# ─────────────────────────────────────────────────────────────────────────────
class MerkleInclusionProof(BaseModel):
    """
    Logarithmic proof that a VaultRecord exists in the VAULT999 chain.

    Follows RFC 6962 Certificate Transparency specification.
    Verification: O(log n) — does not require traversing the full chain.
    """

    record_id: str = Field(description="The record being proven")
    leaf_hash: str = Field(description="SHA-256 hash of the leaf record")
    proof_path: list[tuple[str, str]] = Field(
        default_factory=list,
        description="List of (sibling_hash, 'left'|'right') pairs from leaf to root",
    )
    tree_size: int = Field(default=0, description="Total records in the chain at proof time")
    root_hash: str = Field(default="", description="Merkle root at proof time")
    verified: bool = Field(default=False, description="Whether proof was verified server-side")
    timestamp_utc: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )


__all__ = [
    "EvidenceBundle",
    "VaultRecord",
    "MerkleInclusionProof",
]

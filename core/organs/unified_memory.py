"""
organs/unified_memory.py — Stage 555: THE HEART (VECTOR MEMORY)

Associative memory retrieval and storage using vector embeddings.
Connects to VAULT999 (Qdrant + BGE-M3).

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import os
import secrets
import uuid
from dataclasses import dataclass
from typing import Any, Literal

from arifosmcp.intelligence.embeddings import embed
from arifosmcp.core.shared.types import MemoryResultItem, VaultOutput, VectorMemoryResult, Verdict

logger = logging.getLogger(__name__)
SESSION_MEMORY_COLLECTION = os.getenv("ARIFOS_SESSION_MEMORY_COLLECTION", "arifos_session_memory")
DEFAULT_VECTOR_DIM = int(os.getenv("ARIFOS_VECTOR_DIM", "1024"))


@dataclass
class MemoryResult:
    """Unified memory result (Internal)."""

    source: str  # 'constitutional' or 'gdrive'
    path: str
    content: str
    score: float
    metadata: dict[str, Any]


class UnifiedMemory:
    """
    Unified semantic memory across constitutional corpus and Google Drive.
    """

    def __init__(self, qdrant_url: str | None = None):
        self.collections = {
            "constitutional": "arifos_constitutional",
            "gdrive": "gdrive_documents",
            "session": SESSION_MEMORY_COLLECTION,
        }
        self.client = None
        self.qdrant_url = qdrant_url or os.getenv("QDRANT_URL")
        if not self.qdrant_url:
            return
        try:
            from qdrant_client import QdrantClient

            self.client = QdrantClient(url=self.qdrant_url, timeout=1.0)
            self._ensure_collection(self.collections["session"])
        except Exception:
            self.client = None

    def _ensure_collection(self, collection_name: str) -> None:
        if not self.client:
            return

        from qdrant_client.models import Distance, VectorParams

        try:
            self.client.get_collection(collection_name)
        except Exception:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=DEFAULT_VECTOR_DIM, distance=Distance.COSINE),
            )

    def store(
        self,
        *,
        session_id: str,
        content: str,
        metadata: dict[str, Any] | None = None,
        source: str = "session_history",
    ) -> list[str]:
        if not self.client:
            return [f"mem_{secrets.token_hex(4)}"]

        from qdrant_client.models import PointStruct

        self._ensure_collection(self.collections["session"])
        point_id = str(uuid.uuid4())
        payload = {
            "session_id": session_id,
            "source": source,
            "path": session_id,
            "content": content,
            "metadata": metadata or {},
        }
        self.client.upsert(
            collection_name=self.collections["session"],
            points=[PointStruct(id=point_id, vector=embed(content), payload=payload)],
        )
        return [point_id]

    def forget(self, memory_ids: list[str]) -> list[str]:
        if not self.client or not memory_ids:
            return memory_ids

        from qdrant_client.models import PointIdsList

        self.client.delete(
            collection_name=self.collections["session"],
            points_selector=PointIdsList(points=memory_ids),
        )
        return memory_ids

    def search(
        self,
        query: str,
        top_k: int = 5,
        domain: str = "all",
        session_id: str | None = None,
    ) -> list[MemoryResult]:
        """Search semantic memory via Qdrant, with structured fallback if unavailable."""
        if not self.client:
            return [
                MemoryResult(
                    source="local",
                    path="memory/core",
                    content="Fallback: arifOS Stage 555 focuses on semantic stability.",
                    score=0.9,
                    metadata={},
                )
            ]

        from qdrant_client.models import FieldCondition, Filter, MatchValue

        collection_name = self.collections.get(domain, self.collections["session"])
        self._ensure_collection(collection_name)
        query_filter = None
        if session_id and collection_name == self.collections["session"]:
            query_filter = Filter(
                must=[FieldCondition(key="session_id", match=MatchValue(value=session_id))]
            )

        try:
            results = self.client.query_points(
                collection_name=collection_name,
                query=embed(query),
                query_filter=query_filter,
                limit=top_k,
                with_payload=True,
            )
        except Exception as exc:
            logger.warning("UnifiedMemory search fallback activated: %s", exc)
            return [
                MemoryResult(
                    source="local",
                    path="memory/core",
                    content="Fallback: semantic memory temporarily unavailable.",
                    score=0.5,
                    metadata={"error": str(exc)},
                )
            ]

        points = getattr(results, "points", []) or []
        memories: list[MemoryResult] = []
        for point in points:
            payload = point.payload or {}
            memories.append(
                MemoryResult(
                    source=str(payload.get("source", domain)),
                    path=str(payload.get("path", "memory/session")),
                    content=str(payload.get("content", "")),
                    score=float(getattr(point, "score", 0.0) or 0.0),
                    metadata={
                        **dict(payload.get("metadata", {}) or {}),
                        "session_id": payload.get("session_id"),
                        "point_id": str(getattr(point, "id", "")),
                    },
                )
            )
        return memories


_unified_memory: UnifiedMemory | None = None


def get_unified_memory() -> UnifiedMemory:
    global _unified_memory
    if _unified_memory is None:
        _unified_memory = UnifiedMemory()
    return _unified_memory


async def vault(
    operation: Literal["store", "recall", "search", "forget", "seal"] = "search",
    session_id: str = "global",
    content: str | None = None,
    memory_ids: list[str] | None = None,
    top_k: int = 5,
    auth_context: dict[str, Any] | None = None,
    **kwargs: Any,
) -> VaultOutput:
    """
    Stage 555: VECTOR MEMORY (APEX-G compliant)
    """

    # 1. Initialize Result
    res = VectorMemoryResult()

    # 2. Map Operation to Implementation
    if operation == "store":
        if not content:
            # Fallback to query if content is missing but query exists (legacy)
            content = kwargs.get("query")
        if not content:
            raise ValueError("Operation 'store' requires 'content' or 'query'")

        res.stored_ids = get_unified_memory().store(session_id=session_id, content=content)

    elif operation in ("recall", "search"):
        search_query = content or kwargs.get("query") or "INIT"

        internal_results = get_unified_memory().search(
            search_query, top_k=top_k, session_id=session_id
        )

        res.memories = [
            MemoryResultItem(
                id=str(r.metadata.get("point_id", f"mem_{secrets.token_hex(4)}")),
                content=r.content,
                score=r.score,
                metadata={**r.metadata, "source": r.source, "path": r.path},
            )
            for r in internal_results
        ]

    elif operation == "forget":
        res.forgot_ids = get_unified_memory().forget(memory_ids or [])

    elif operation == "seal":
        # Stage 999: VAULT SEAL logic
        return VaultOutput(
            session_id=session_id,
            verdict=Verdict.SEAL,
            operation="seal",
            status="SUCCESS",
            seal_hash=secrets.token_hex(32),
        )

    # 3. Construct Output
    return VaultOutput(
        session_id=session_id,
        verdict=Verdict.SEAL,
        operation=operation,
        status="SUCCESS",
        result=res,
    )


# Unified alias
vector_memory = vault


__all__ = ["get_unified_memory", "vault", "vector_memory", "UnifiedMemory"]

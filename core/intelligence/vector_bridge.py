"""
core/intelligence/vector_bridge.py — Qdrant Vector Memory Bridge

Background ingestion hook that converts extracted reality claims into
vector embeddings and syncs them to Qdrant for long-term memory continuity.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import hashlib
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any

import httpx

logger = logging.getLogger(__name__)


@dataclass
class VectorEntry:
    id: str
    text: str
    embedding: list[float] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    session_id: str = "global"
    actor_id: str = "anonymous"
    source: str = "reality_compass"
    claim_type: str = "statement"
    confidence: float = 1.0
    created_at: float = field(default_factory=time.time)
    is_pseudo: bool = False


@dataclass
class IngestionResult:
    success: bool
    points_upserted: int = 0
    collection: str = ""
    error: str | None = None
    latency_ms: float = 0.0


class QdrantVectorBridge:
    def __init__(self):
        self.qdrant_url = os.getenv("QDRANT_URL", "http://qdrant_memory:6333")
        self.collection_name = os.getenv("QDRANT_COLLECTION", "arifos_memory")
        self.embedding_dimension = int(os.getenv("EMBEDDING_DIMENSION", "1024"))
        self.batch_size = int(os.getenv("VECTOR_BATCH_SIZE", "100"))
        self.ollama_url = os.getenv("OLLAMA_URL", "http://ollama_engine:11434")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "bge-m3")
        self._client = None
        self._collection_initialized = False

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def ensure_collection(self) -> bool:
        if self._collection_initialized:
            return True

        client = await self._get_client()

        try:
            response = await client.get(f"{self.qdrant_url}/collections/{self.collection_name}")
            if response.status_code == 200:
                self._collection_initialized = True
                return True
        except Exception:
            pass

        create_payload = {"vectors": {"size": self.embedding_dimension, "distance": "Cosine"}}

        try:
            response = await client.put(
                f"{self.qdrant_url}/collections/{self.collection_name}", json=create_payload
            )
            if response.status_code == 200:
                self._collection_initialized = True
                logger.info(f"Created Qdrant collection: {self.collection_name}")
                return True
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return False

        return False

    async def embed_text(self, text: str) -> tuple[list[float] | None, bool]:
        """Embed text using Ollama, fallback to SHA-256 pseudo if failed."""
        if not text or len(text.strip()) < 3:
            return None, False

        client = await self._get_client()

        try:
            response = await client.post(
                f"{self.ollama_url}/api/embeddings",
                json={"model": self.embedding_model, "prompt": text[:8000]},
                timeout=30.0,
            )

            if response.status_code == 200:
                data = response.json()
                embedding = data.get("embedding")
                if embedding and len(embedding) == self.embedding_dimension:
                    return embedding, False
                elif embedding:
                    return embedding[: self.embedding_dimension] + [0.0] * max(
                        0, self.embedding_dimension - len(embedding)
                    ), False
        except Exception as e:
            logger.warning(f"F1_GUARD: Semantic embedding failed, using pseudo-fallback: {e}")
            return self._fallback_embedding(text), True

        logger.warning("F1_GUARD: Semantic embedding returned no data, using pseudo-fallback")
        return self._fallback_embedding(text), True

    def _fallback_embedding(self, text: str) -> list[float]:
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        embedding = []
        for i in range(0, min(64, len(text_hash)), 2):
            val = int(text_hash[i : i + 2], 16) / 255.0 - 0.5
            embedding.extend([val] * (self.embedding_dimension // 32))
        while len(embedding) < self.embedding_dimension:
            embedding.append(0.0)
        return embedding[: self.embedding_dimension]

    async def upsert_vectors(self, entries: list[VectorEntry]) -> IngestionResult:
        start_time = time.time()

        if not entries:
            return IngestionResult(success=True, points_upserted=0)

        await self.ensure_collection()
        client = await self._get_client()

        points = []
        for entry in entries:
            if entry.embedding is None:
                entry.embedding, entry.is_pseudo = await self.embed_text(entry.text)

            if entry.embedding is None:
                continue

            point = {
                "id": entry.id,
                "vector": entry.embedding,
                "payload": {
                    "text": entry.text[:2000],
                    "session_id": entry.session_id,
                    "actor_id": entry.actor_id,
                    "source": entry.source,
                    "claim_type": entry.claim_type,
                    "confidence": entry.confidence,
                    "created_at": entry.created_at,
                    "is_pseudo": entry.is_pseudo,
                    "metadata": entry.metadata,
                },
            }
            points.append(point)

        if not points:
            return IngestionResult(success=False, error="No valid embeddings generated")

        try:
            response = await client.upsert(
                f"{self.qdrant_url}/collections/{self.collection_name}/points",
                json={"points": points},
            )

            latency_ms = (time.time() - start_time) * 1000

            if response.status_code == 200:
                return IngestionResult(
                    success=True,
                    points_upserted=len(points),
                    collection=self.collection_name,
                    latency_ms=latency_ms,
                )
            else:
                return IngestionResult(
                    success=False,
                    error=f"Qdrant upsert failed: {response.status_code}",
                    latency_ms=latency_ms,
                )
        except Exception as e:
            return IngestionResult(
                success=False, error=str(e), latency_ms=(time.time() - start_time) * 1000
            )

    async def search_similar(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        score_threshold: float = 0.7,
        session_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        await self.ensure_collection()
        client = await self._get_client()

        filter_conditions = []
        if session_filter:
            filter_conditions.append({"key": "session_id", "match": {"value": session_filter}})

        search_payload = {
            "vector": query_embedding,
            "limit": top_k,
            "score_threshold": score_threshold,
            "with_payload": True,
        }

        if filter_conditions:
            search_payload["filter"] = {"must": filter_conditions}

        try:
            response = await client.post(
                f"{self.qdrant_url}/collections/{self.collection_name}/points/search",
                json=search_payload,
            )

            if response.status_code == 200:
                data = response.json()
                return [
                    {
                        "id": hit.get("id"),
                        "score": hit.get("score"),
                        "payload": hit.get("payload", {}),
                    }
                    for hit in data.get("result", [])
                ]
        except Exception as e:
            logger.error(f"Search failed: {e}")

        return []

    async def ingest_from_evidence_bundle(
        self,
        bundle: dict[str, Any],
        session_id: str = "global",
        actor_id: str = "anonymous",
    ) -> IngestionResult:
        entries: list[VectorEntry] = []

        claims = bundle.get("claims", [])
        for claim in claims:
            if isinstance(claim, dict):
                text = claim.get("text", "")
                if text:
                    entries.append(
                        VectorEntry(
                            id=hashlib.sha256(f"{session_id}:{text}".encode()).hexdigest()[:36],
                            text=text,
                            metadata=claim.get("metadata", {}),
                            session_id=session_id,
                            actor_id=actor_id,
                            source="evidence_bundle",
                            claim_type=claim.get("type", "statement"),
                            confidence=claim.get("confidence", 1.0),
                        )
                    )

        results = bundle.get("results", [])
        for result in results:
            if isinstance(result, dict):
                url = result.get("url", "")
                content = result.get("raw_content", "") or result.get("text", "")
                if content:
                    text_preview = content[:1000]
                    entries.append(
                        VectorEntry(
                            id=hashlib.sha256(url.encode()).hexdigest()[:36],
                            text=text_preview,
                            metadata={"url": url, "source_type": "fetch"},
                            session_id=session_id,
                            actor_id=actor_id,
                            source="reality_fetch",
                            claim_type="source_content",
                            confidence=0.9,
                        )
                    )

        return await self.upsert_vectors(entries)


qdrant_bridge = QdrantVectorBridge()


async def vector_memory_embedding(
    texts: list[str],
    session_id: str = "global",
    actor_id: str = "anonymous",
    metadata: dict[str, Any] | None = None,
) -> IngestionResult:
    entries = []
    for i, text in enumerate(texts):
        if text:
            entries.append(
                VectorEntry(
                    id=hashlib.sha256(f"{session_id}:{i}:{text[:100]}".encode()).hexdigest()[:36],
                    text=text,
                    metadata=metadata or {},
                    session_id=session_id,
                    actor_id=actor_id,
                    source="manual_embedding",
                )
            )

    return await qdrant_bridge.upsert_vectors(entries)


async def vector_memory_search(
    query: str,
    top_k: int = 5,
    session_id: str | None = None,
) -> list[dict[str, Any]]:
    embedding, is_pseudo = await qdrant_bridge.embed_text(query)
    if embedding is None:
        return []

    if is_pseudo:
        logger.warning("F1_GUARD: Query vector is pseudo-hash. Results will be structurally valid but semantically meaningless.")

    return await qdrant_bridge.search_similar(embedding, top_k=top_k, session_filter=session_id)

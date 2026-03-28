"""
arifosmcp/intelligence/tools/vector_bridge.py — Qdrant Auto-Ingest Bridge

Automatically syncs EvidenceBundles from reality_atlas to Qdrant vector store.
This is the missing plumbing that enables long-term memory continuity.

When reality_atlas merges a new EvidenceBundle:
1. Extract text claims and evidence
2. Generate BGE-M3 embeddings
3. Auto-sync to Qdrant collection
4. Preserve provenance for F3 Tri-Witness

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import logging
import os
import uuid
from typing import Any

from pydantic import BaseModel, Field

# Optional Qdrant import - graceful degradation if not installed
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, PointStruct, VectorParams
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

# Optional sentence-transformers for embeddings
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False

from arifosmcp.runtime.reality_models import EvidenceBundle

logger = logging.getLogger(__name__)

# Configuration from environment
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "arifos_memory")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
EMBEDDING_DIMS = int(os.getenv("EMBEDDING_DIMS", "1024"))
AUTO_SYNC_ENABLED = os.getenv("ARIFOS_AUTO_VECTOR_SYNC", "true").lower() in ("true", "1", "yes")


class VectorSyncResult(BaseModel):
    """Result of vector sync operation."""
    success: bool = False
    points_synced: int = 0
    errors: list[str] = Field(default_factory=list)
    collection: str = ""
    session_id: str = "global"


class VectorBridge:
    """
    Bridge between EvidenceBundles and Qdrant vector store.
    
    Implements automatic ingestion: when reality operations produce
    EvidenceBundles, they are automatically embedded and persisted.
    """
    
    def __init__(self):
        self._client: Any | None = None
        self._embedding_model: Any | None = None
        self._initialized = False
        
    def _get_client(self) -> QdrantClient | None:
        """Lazy initialization of Qdrant client."""
        if not QDRANT_AVAILABLE:
            return None
        if self._client is None:
            try:
                kwargs = {"url": QDRANT_URL}
                if QDRANT_API_KEY:
                    kwargs["api_key"] = QDRANT_API_KEY
                self._client = QdrantClient(**kwargs)
                self._ensure_collection()
            except Exception as e:
                logger.warning(f"Qdrant connection failed: {e}")
                return None
        return self._client
    
    def _get_embedding_model(self) -> Any | None:
        """Lazy initialization of embedding model."""
        if not EMBEDDING_AVAILABLE:
            return None
        if self._embedding_model is None:
            try:
                self._embedding_model = SentenceTransformer(EMBEDDING_MODEL)
                logger.info(f"Loaded embedding model: {EMBEDDING_MODEL}")
            except Exception as e:
                logger.warning(f"Embedding model load failed: {e}")
                return None
        return self._embedding_model
    
    def _ensure_collection(self) -> bool:
        """Ensure the collection exists with proper schema."""
        if not self._client:
            return False
        try:
            collections = self._client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if QDRANT_COLLECTION not in collection_names:
                self._client.create_collection(
                    collection_name=QDRANT_COLLECTION,
                    vectors_config=VectorParams(
                        size=EMBEDDING_DIMS,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"Created Qdrant collection: {QDRANT_COLLECTION}")
            return True
        except Exception as e:
            logger.error(f"Collection setup failed: {e}")
            return False
    
    def _generate_embedding(self, text: str) -> list[float] | None:
        """Generate embedding vector for text."""
        model = self._get_embedding_model()
        if not model:
            return None
        try:
            # BGE-M3 prefers prefixed input for asymmetric search
            prefixed = f"Represent this sentence for searching relevant passages: {text}"
            embedding = model.encode(prefixed, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            logger.warning(f"Embedding generation failed: {e}")
            return None
    
    def _compute_content_hash(self, text: str) -> str:
        """Compute deterministic ID from content."""
        return hashlib.sha256(text.encode()).hexdigest()[:16]
    
    def sync_bundle(
        self,
        bundle: EvidenceBundle,
        session_id: str = "global",
        actor_id: str = "anonymous",
    ) -> VectorSyncResult:
        """
        Sync an EvidenceBundle to Qdrant vector store.
        
        Extracts claims, generates embeddings, and persists with full provenance.
        """
        if not AUTO_SYNC_ENABLED:
            return VectorSyncResult(
                success=True,
                points_synced=0,
                collection=QDRANT_COLLECTION,
                session_id=session_id,
            )
        
        client = self._get_client()
        if not client:
            return VectorSyncResult(
                success=False,
                errors=["Qdrant not available"],
                collection=QDRANT_COLLECTION,
                session_id=session_id,
            )
        
        points: list[PointStruct] = []
        errors: list[str] = []
        
        # Process each claim in the bundle
        for claim in bundle.claims:
            try:
                # Skip empty claims
                if not claim.text or len(claim.text.strip()) < 10:
                    continue
                
                # Generate embedding
                embedding = self._generate_embedding(claim.text)
                if not embedding:
                    errors.append(f"Failed to embed claim: {claim.text[:50]}...")
                    continue
                
                # Compute deterministic ID
                point_id = self._compute_content_hash(claim.text + bundle.id)
                
                # Build payload with full provenance (F3 Tri-Witness)
                payload = {
                    "text": claim.text,
                    "type": claim.type,
                    "confidence": claim.confidence,
                    "evidence_count": len(claim.evidence),
                    "bundle_id": bundle.id,
                    "session_id": session_id,
                    "actor_id": actor_id,
                    "input_type": bundle.input.type,
                    "input_value": bundle.input.value,
                    "bundle_status": bundle.status.state,
                    "timestamp": uuid.uuid1().time,
                    # F3 Tri-Witness metadata
                    "tri_witness": {
                        "human": bundle.actor.actor_id,
                        "ai": "arifOS.reality_dossier",
                        "earth": bundle.input.value if bundle.input.type == "url" else "search_results",
                    },
                }
                
                points.append(PointStruct(id=point_id, vector=embedding, payload=payload))
                
            except Exception as e:
                errors.append(f"Claim processing error: {e}")
        
        # Batch upsert to Qdrant
        if points:
            try:
                client.upsert(
                    collection_name=QDRANT_COLLECTION,
                    points=points,
                    wait=False,  # Async for performance
                )
                logger.info(f"Synced {len(points)} points to {QDRANT_COLLECTION}")
            except Exception as e:
                errors.append(f"Qdrant upsert failed: {e}")
                return VectorSyncResult(
                    success=False,
                    points_synced=0,
                    errors=errors,
                    collection=QDRANT_COLLECTION,
                    session_id=session_id,
                )
        
        return VectorSyncResult(
            success=len(errors) == 0 or len(points) > 0,
            points_synced=len(points),
            errors=errors,
            collection=QDRANT_COLLECTION,
            session_id=session_id,
        )
    
    def search_memory(
        self,
        query: str,
        top_k: int = 5,
        filter_actor: str | None = None,
        min_confidence: float = 0.0,
    ) -> list[dict[str, Any]]:
        """Search vector memory for relevant passages."""
        client = self._get_client()
        if not client:
            return []
        
        embedding = self._generate_embedding(query)
        if not embedding:
            return []
        
        # Build filter if needed
        search_filter = None
        if filter_actor:
            from qdrant_client.models import FieldCondition, MatchValue
            search_filter = FieldCondition(
                key="actor_id",
                match=MatchValue(value=filter_actor),
            )
        
        try:
            results = client.search(
                collection_name=QDRANT_COLLECTION,
                query_vector=embedding,
                limit=top_k,
                query_filter=search_filter,
                score_threshold=min_confidence,
            )
            
            return [
                {
                    "text": r.payload.get("text", ""),
                    "score": r.score,
                    "bundle_id": r.payload.get("bundle_id"),
                    "session_id": r.payload.get("session_id"),
                    "confidence": r.payload.get("confidence"),
                    "tri_witness": r.payload.get("tri_witness"),
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []


# Singleton instance
vector_bridge = VectorBridge()


# ---------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------
async def auto_sync_bundle(
    bundle: EvidenceBundle,
    session_id: str = "global",
    actor_id: str = "anonymous",
) -> VectorSyncResult:
    """
    Auto-sync an EvidenceBundle to vector memory.
    
    Called automatically by reality_atlas when bundles are merged.
    """
    # Run in thread pool since embedding is CPU-bound
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        vector_bridge.sync_bundle,
        bundle,
        session_id,
        actor_id,
    )


async def search_vector_memory(
    query: str,
    top_k: int = 5,
    filter_actor: str | None = None,
    min_confidence: float = 0.0,
) -> list[dict[str, Any]]:
    """Search vector memory for relevant passages."""
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        vector_bridge.search_memory,
        query,
        top_k,
        filter_actor,
        min_confidence,
    )


async def search_hybrid_memory(
    query: str,
    top_k: int = 5,
    project_id: str = "default",
    use_cache: bool = True,
) -> list[dict[str, Any]]:
    """
    555_MEMORY: Hybrid vector search (LanceDB hot + Qdrant cold).
    
    Constitutional:
    - F1: Qdrant remains source of truth
    - F2: 24h freshness verification
    - F12: Injection guard on query
    - F13: Large writes trigger audit
    
    Args:
        query: Search query text
        top_k: Number of results
        project_id: Tenant isolation
        use_cache: Prefer LanceDB hot path
        
    Returns:
        List of results with source attribution (lancedb/qdrant)
    """
    from arifosmcp.intelligence.tools.hybrid_vector_memory import get_hybrid_memory
    
    memory = await get_hybrid_memory()
    results = await memory.search(
        query=query,
        k=top_k,
        use_cache=use_cache,
        project_id=project_id,
    )
    
    return [
        {
            "id": r.id,
            "content": r.content,
            "score": r.score,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            "source": r.source,
            "metadata": r.metadata,
        }
        for r in results
    ]


def get_vector_stats() -> dict[str, Any]:
    """Get vector store statistics."""
    client = vector_bridge._get_client()
    if not client:
        return {"available": False, "reason": "Qdrant not connected"}
    
    try:
        info = client.get_collection(QDRANT_COLLECTION)
        return {
            "available": True,
            "collection": QDRANT_COLLECTION,
            "vectors_count": info.vectors_count,
            "indexed_vectors_count": info.indexed_vectors_count,
            "status": info.status,
            "embedding_model": EMBEDDING_MODEL if EMBEDDING_AVAILABLE else "not_loaded",
            "auto_sync": AUTO_SYNC_ENABLED,
        }
    except Exception as e:
        return {"available": False, "reason": str(e)}


__all__ = [
    "VectorBridge",
    "VectorSyncResult",
    "auto_sync_bundle",
    "search_vector_memory",
    "search_hybrid_memory",
    "get_vector_stats",
    "vector_bridge",
]

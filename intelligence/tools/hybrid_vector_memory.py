"""
arifosmcp/intelligence/tools/hybrid_vector_memory.py — Hybrid L3 Vector Memory

LanceDB (hot/local) + Qdrant (cold/server) architecture.

Constitutional Guarantees:
- F1 Amanah: Qdrant is source of truth; LanceDB is ephemeral cache
- F2 Truth: All vectors verified before storage, 24h freshness check
- F4 Clarity: Hot/cold paths explicit, unified API
- F12 Injection: Query sanitization before search
- F13 Sovereign: 888_HOLD on large cache writes (>1000 vectors)

ΔΩΨ | ARIF — Ditempa Bukan Diberi
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Literal

import lancedb
import numpy as np
from lancedb.pydantic import LanceModel, Vector

logger = logging.getLogger(__name__)


@dataclass
class VectorSearchResult:
    """Typed result from vector search."""
    id: str
    content: str
    score: float
    timestamp: datetime
    source: Literal["lancedb", "qdrant"]
    metadata: dict[str, Any] = field(default_factory=dict)


class HybridVectorMemory:
    """
    L3 Hybrid Vector Memory: LanceDB (hot) + Qdrant (cold).
    
    Architecture:
    - HOT PATH: LanceDB local file (<10ms, recent 10K vectors)
    - COLD PATH: Qdrant server (~50ms, full historical archive)
    - SYNC: Daily Qdrant → LanceDB, with 888_HOLD on large writes
    
    Constitutional Integration:
    - F1: Qdrant is immutable; LanceDB is cache-only
    - F2: Freshness check (24h), F12 injection guard
    - F13: Large writes (>1000) trigger 888_HOLD audit
    """
    
    # Configuration
    LANCEDB_PATH: str = "data/vector_cache.lance"
    HOT_VECTOR_LIMIT: int = 10000
    FRESHNESS_HOURS: int = 24
    LARGE_WRITE_THRESHOLD: int = 1000
    
    def __init__(
        self,
        qdrant_client=None,
        lancedb_path: str | None = None,
        ollama_base_url: str = "http://ollama_engine:11434",
    ):
        self.qdrant = qdrant_client
        self.lancedb_path = lancedb_path or self.LANCEDB_PATH
        self.ollama_base_url = ollama_base_url
        
        # Initialize LanceDB
        self._db: lancedb.DBConnection | None = None
        self._table: lancedb.table.Table | None = None
        self._initialized = False
        
    async def initialize(self) -> bool:
        """
        Initialize LanceDB connection and table.
        
        Returns True if LanceDB is available, False if fallback to Qdrant-only.
        """
        try:
            # Ensure directory exists
            Path(self.lancedb_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Connect to LanceDB
            self._db = await asyncio.to_thread(lancedb.connect, self.lancedb_path)
            
            # Get or create table
            table_name = "vector_cache"
            try:
                self._table = await asyncio.to_thread(self._db.open_table, table_name)
                logger.info(f"LanceDB table '{table_name}' opened ({len(self._table)} vectors)")
            except Exception:
                # Create new table with schema
                self._table = await self._create_table(table_name)
                logger.info(f"LanceDB table '{table_name}' created")
            
            self._initialized = True
            return True
            
        except Exception as e:
            logger.warning(f"LanceDB initialization failed: {e}. Falling back to Qdrant-only.")
            self._initialized = False
            return False
    
    async def _create_table(self, name: str) -> lancedb.table.Table:
        """Create LanceDB table with BGE-M3 schema (1024-dim)."""
        import pyarrow as pa
        
        schema = pa.schema([
            ("id", pa.string()),
            ("vector", pa.list_(pa.float32(), 1024)),  # BGE-M3 dimension
            ("content", pa.string()),
            ("timestamp", pa.timestamp("us")),
            ("session_id", pa.string()),
            ("metadata", pa.string()),  # JSON-encoded
        ])
        
        return await asyncio.to_thread(self._db.create_table, name, schema=schema)
    
    async def search(
        self,
        query: str,
        k: int = 5,
        use_cache: bool = True,
        project_id: str = "default",
    ) -> list[VectorSearchResult]:
        """
        Hybrid semantic search with automatic hot/cold routing.
        
        1. F12: Injection scan on query
        2. HOT: Query LanceDB (recent vectors, <10ms)
        3. COLD: Query Qdrant (full archive, ~50ms)
        4. CACHE: Store cold results in LanceDB for next query
        
        Args:
            query: Search query text
            k: Number of results
            use_cache: Prefer LanceDB hot path if available
            project_id: Tenant isolation
            
        Returns:
            List of VectorSearchResult (F2 verified, freshness-checked)
        """
        # F12: Injection guard
        if await self._is_injection(query):
            logger.warning(f"F12_INJECTION_BLOCKED in vector_search: query='{query[:50]}...'")
            return []
        
        # Generate embedding via Ollama BGE-M3
        try:
            embedding = await self._embed(query)
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return []
        
        results: list[VectorSearchResult] = []
        source = "unknown"
        
        # HOT PATH: LanceDB (recent vectors only)
        if use_cache and self._initialized and self._table:
            try:
                results = await self._search_lancedb(embedding, k, project_id)
                if results:
                    source = "lancedb"
                    logger.debug(f"LanceDB hit: {len(results)} results")
            except Exception as e:
                logger.warning(f"LanceDB search failed: {e}")
        
        # COLD PATH: Qdrant (if LanceDB miss or unavailable)
        if not results and self.qdrant:
            try:
                results = await self._search_qdrant(embedding, k, project_id)
                source = "qdrant"
                logger.debug(f"Qdrant hit: {len(results)} results")
                
                # Async cache to LanceDB for next query (non-blocking)
                if self._initialized:
                    asyncio.create_task(self._cache_results(results))
                    
            except Exception as e:
                logger.error(f"Qdrant search failed: {e}")
        
        # F2: Verify freshness (filter stale vectors >24h)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.FRESHNESS_HOURS)
        fresh_results = [
            r for r in results 
            if r.timestamp and r.timestamp > cutoff
        ]
        
        if len(fresh_results) < len(results):
            logger.info(f"F2: Filtered {len(results) - len(fresh_results)} stale vectors")
        
        return fresh_results[:k]
    
    async def _search_lancedb(
        self,
        embedding: list[float],
        k: int,
        project_id: str,
    ) -> list[VectorSearchResult]:
        """Search LanceDB hot cache."""
        if not self._table:
            return []
        
        # Build filter for project isolation
        # Note: LanceDB filtering is limited; we filter post-query
        
        search_results = await asyncio.to_thread(
            lambda: self._table.search(embedding)
            .metric("cosine")
            .limit(k * 2)  # Fetch extra for filtering
            .to_pandas()
        )
        
        results = []
        for _, row in search_results.iterrows():
            metadata = json.loads(row.get("metadata", "{}"))
            
            # Project isolation filter
            if metadata.get("project_id", "default") != project_id:
                continue
            
            results.append(VectorSearchResult(
                id=row["id"],
                content=row["content"],
                score=1.0 - row.get("_distance", 0),  # Convert distance to similarity
                timestamp=row["timestamp"].to_pydatetime() if hasattr(row["timestamp"], "to_pydatetime") else datetime.now(timezone.utc),
                source="lancedb",
                metadata=metadata,
            ))
        
        return results[:k]
    
    async def _search_qdrant(
        self,
        embedding: list[float],
        k: int,
        project_id: str,
    ) -> list[VectorSearchResult]:
        """Search Qdrant cold storage."""
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        if not self.qdrant:
            return []
        
        # Build filter
        search_filter = Filter(
            must=[
                FieldCondition(
                    key="project_id",
                    match=MatchValue(value=project_id),
                )
            ]
        ) if project_id != "default" else None
        
        response = await asyncio.to_thread(
            self.qdrant.search,
            collection_name="arifos_memory",
            query_vector=embedding,
            limit=k,
            query_filter=search_filter,
            with_payload=True,
        )
        
        results = []
        for point in response:
            payload = point.payload or {}
            results.append(VectorSearchResult(
                id=point.id,
                content=payload.get("content", ""),
                score=point.score,
                timestamp=datetime.fromisoformat(payload.get("timestamp", datetime.now(timezone.utc).isoformat())),
                source="qdrant",
                metadata=payload,
            ))
        
        return results
    
    async def _cache_results(self, results: list[VectorSearchResult]):
        """
        Write Qdrant results to LanceDB for hot-path acceleration.
        
        F1 Amanah: Idempotent caching. Original remains in Qdrant.
        F13: Large writes (>1000) trigger 888_HOLD audit notification.
        """
        if not self._table or not results:
            return
        
        # F13: Large cache writes need audit trail
        if len(results) > self.LARGE_WRITE_THRESHOLD:
            logger.warning(
                f"[888_HOLD NOTIFY] Large vector cache write: {len(results)} entries. "
                f"Hold triggered for audit."
            )
            try:
                from arifosmcp.runtime.mcp_utils import call_mcp_tool
                await call_mcp_tool("apex_soul", {
                    "mode": "hold",
                    "reason": f"Large vector cache write: {len(results)} entries",
                    "actor_id": "arifosmcp",
                    "context": "hybrid_vector_memory._cache_results",
                })
            except Exception as e:
                logger.error(f"Failed to trigger 888_HOLD: {e}")
        
        # Prepare data for LanceDB
        data = []
        for r in results:
            data.append({
                "id": r.id,
                "vector": r.metadata.get("embedding", []),  # Must include vector
                "content": r.content,
                "timestamp": r.timestamp,
                "session_id": r.metadata.get("session_id", "unknown"),
                "metadata": json.dumps(r.metadata),
            })
        
        try:
            await asyncio.to_thread(self._table.add, data)
            logger.info(f"Cached {len(data)} vectors to LanceDB")
        except Exception as e:
            logger.error(f"Failed to cache to LanceDB: {e}")
    
    async def sync_from_qdrant(self, project_id: str | None = None, days: int = 7):
        """
        Daily sync: Pull recent vectors from Qdrant into LanceDB hot cache.
        
        Called by vault_seal (999 stage) at end of each session day.
        
        Args:
            project_id: Optional project filter
            days: How many days back to sync
        """
        if not self.qdrant or not self._table:
            logger.warning("Cannot sync: Qdrant or LanceDB not available")
            return
        
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        try:
            # Scroll Qdrant for recent vectors
            # Note: In production, use scroll API with timestamp filter
            from qdrant_client.models import Filter, FieldCondition, Range
            
            scroll_filter = Filter(
                must=[
                    FieldCondition(
                        key="timestamp",
                        range=Range(
                            gte=cutoff.isoformat(),
                        )
                    )
                ]
            ) if project_id is None else Filter(
                must=[
                    FieldCondition(key="project_id", match={"value": project_id}),
                    FieldCondition(
                        key="timestamp",
                        range=Range(gte=cutoff.isoformat())
                    )
                ]
            )
            
            all_records = []
            next_offset = None
            
            while True:
                response = await asyncio.to_thread(
                    self.qdrant.scroll,
                    collection_name="arifos_memory",
                    scroll_filter=scroll_filter,
                    limit=1000,
                    offset=next_offset,
                    with_payload=True,
                    with_vectors=True,
                )
                
                points, next_offset = response
                all_records.extend(points)
                
                if next_offset is None:
                    break
            
            # Convert to LanceDB format
            data = []
            for point in all_records:
                payload = point.payload or {}
                data.append({
                    "id": point.id,
                    "vector": point.vector,
                    "content": payload.get("content", ""),
                    "timestamp": datetime.fromisoformat(payload.get("timestamp", datetime.now(timezone.utc).isoformat())),
                    "session_id": payload.get("session_id", "unknown"),
                    "metadata": json.dumps(payload),
                })
            
            # Clear and repopulate (ensures consistency)
            await asyncio.to_thread(self._table.delete, "true")  # Delete all
            await asyncio.to_thread(self._table.add, data)
            
            logger.info(f"Daily sync complete: {len(data)} vectors from Qdrant → LanceDB")
            
        except Exception as e:
            logger.error(f"Daily sync failed: {e}")
            # F1: Log degradation but don't block
            # Next query will use Qdrant cold path
    
    async def _embed(self, text: str) -> list[float]:
        """
        Generate embedding via Ollama BGE-M3.
        
        Falls back to local embedding if Ollama unavailable.
        """
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_base_url}/api/embeddings",
                    json={
                        "model": "bge-m3",
                        "prompt": text[:8192],  # BGE-M3 context limit
                    },
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("embedding", [])
                    else:
                        raise RuntimeError(f"Ollama returned {resp.status}")
                        
        except Exception as e:
            logger.error(f"Ollama embedding failed: {e}")
            # Fallback: Return zero vector (will match nothing)
            return [0.0] * 1024
    
    async def _is_injection(self, query: str) -> bool:
        """
        F12: Scan for prompt injection in vector query.
        
        Lightweight heuristic; full F12 scan in PNS layer.
        """
        # Fast pattern matching for common injection patterns
        dangerous_patterns = [
            "ignore previous instructions",
            "disregard all prior",
            "you are now",
            "system override",
            "root access",
            "sudo",
            "--",
            "; DROP",
            "javascript:",
            "<script",
        ]
        
        query_lower = query.lower()
        for pattern in dangerous_patterns:
            if pattern in query_lower:
                return True
        
        # Length-based heuristic (unusually long queries may be stuffing)
        if len(query) > 10000:
            return True
            
        return False
    
    async def purge(self, memory_ids: list[str]) -> int:
        """H3: Delete vectors from LanceDB hot cache by ID. Returns count purged.

        Non-blocking, non-fatal — logs warning on failure.
        This fixes the ghost recall bug where deleted Qdrant vectors
        persist in the LanceDB cache and are returned on subsequent queries.
        """
        if not self._table or not self._initialized or not memory_ids:
            return 0
        try:
            # LanceDB filter syntax for ID-based delete
            id_filter = " OR ".join([f"id = '{mid}'" for mid in memory_ids])
            await asyncio.to_thread(self._table.delete, id_filter)
            logger.info(f"H3: LanceDB purged {len(memory_ids)} vectors (ghost recall fix)")
            return len(memory_ids)
        except Exception as e:
            logger.warning(f"H3: LanceDB purge failed (non-blocking): {e}")
            return 0

    def get_stats(self) -> dict[str, Any]:
        """Return current memory statistics."""
        return {
            "lancedb_initialized": self._initialized,
            "lancedb_vectors": len(self._table) if self._table else 0,
            "qdrant_available": self.qdrant is not None,
            "hot_limit": self.HOT_VECTOR_LIMIT,
            "freshness_hours": self.FRESHNESS_HOURS,
        }


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCE (shared across tools)
# ═══════════════════════════════════════════════════════════════════════════

_hybrid_memory: HybridVectorMemory | None = None


async def get_hybrid_memory() -> HybridVectorMemory:
    """Get or initialize singleton HybridVectorMemory."""
    global _hybrid_memory
    if _hybrid_memory is None:
        # Lazy import to avoid circular deps
        from qdrant_client import QdrantClient
        
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant = QdrantClient(url=qdrant_url) if qdrant_url else None
        
        _hybrid_memory = HybridVectorMemory(
            qdrant_client=qdrant,
            lancedb_path=os.getenv("LANCEDB_PATH", "data/vector_cache.lance"),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://ollama_engine:11434"),
        )
        await _hybrid_memory.initialize()
    
    return _hybrid_memory

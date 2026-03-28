"""
L3: Vector Semantic Layer (LanceDB implementation)
High-speed embedded vector storage for episodic and semantic continuity.
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import lancedb

    LANCEDB_AVAILABLE = True
except ImportError:
    lancedb = None  # type: ignore
    LANCEDB_AVAILABLE = False

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class VectorMemoryPayload(BaseModel):
    session_id: str
    insight_type: str
    content: str
    timestamp: str


class LanceDBProvider:
    """
    Manages the L3 Semantic Memory using LanceDB.
    Runs locally, heavily optimizing insight extraction and temporal pattern recognition.
    """

    def __init__(self, db_path: str = "VAULT999/lancedb_store"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db = None
        self._table = None
        if not LANCEDB_AVAILABLE:
            logger.warning("LanceDB not available — L3 semantic storage disabled")

    async def connect(self):
        """Initializes connection to LanceDB and creates schema if missing."""
        if not LANCEDB_AVAILABLE:
            logger.warning("LanceDB not installed — cannot connect")
            return
        try:
            self._db = await lancedb.connect_async(str(self.db_path))
            logger.info(f"LanceDB L3 Semantic Storage connected at {self.db_path}")

            # Open or create the L3_Insights table
            try:
                self._table = await self._db.open_table("L3_Insights")
            except Exception:
                # If table doesn't exist, we will create it upon first insertion
                logger.info("LanceDB L3_Insights table not found, will be created on first seal.")
        except Exception as e:
            logger.error(f"Failed to initialize LanceDB: {e}")

    async def ingest_memory(self, payload: VectorMemoryPayload, vector: List[float]):
        """
        Embeds and stores an episodic insight into the L3 Semantic Layer.
        """
        if not self._db:
            await self.connect()

        data = [
            {
                "vector": vector,
                "session_id": payload.session_id,
                "insight_type": payload.insight_type,
                "content": payload.content,
                "timestamp": payload.timestamp,
            }
        ]

        if not self._table:
            self._table = await self._db.create_table("L3_Insights", data=data)
            logger.info("Created new LanceDB L3_Insights table.")
        else:
            await self._table.add(data)

        logger.info(f"L3 Semantic Insight Stored for session {payload.session_id}")

    async def semantic_search(
        self, query_vector: List[float], limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieves contiguous patterns from the L3 memory store using LanceDB's fast indexing.
        """
        if not self._table:
            try:
                if not self._db:
                    await self.connect()
                self._table = await self._db.open_table("L3_Insights")
            except Exception:
                return []  # No L3 memory yet

        try:
            results = await self._table.search(query_vector).limit(limit).to_list()
            return results
        except Exception as e:
            logger.error(f"LanceDB semantic search failed: {e}")
            return []


# Singleton
l3_memory_store = LanceDBProvider()

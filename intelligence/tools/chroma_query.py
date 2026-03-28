"""
arifosmcp.intelligence/tools/chroma_query.py — Qdrant Vector Store Query

ACLIP Console tool: lets AI agents query persistent memory
via the qdrant_memory container (QDRANT_URL env var).
API-compatible with the former ChromaDB interface — same signatures,
same return shape — so callers (console_tools, mcp_bridge) need no changes.
"""

from __future__ import annotations

import os
from typing import Any

from arifosmcp.intelligence.tools.aclip_base import ok, partial, void
from arifosmcp.core.shared.atlas import normalize_semantic_text

_DEFAULT_QDRANT_URL = "http://localhost:6333"


def query_memory(
    query: str,
    collection: str = "default",
    n_results: int = 5,
    where: dict[str, Any] | None = None,
    include_embeddings: bool = False,
    _chroma_path: str | None = None,  # kept for API compat — unused
) -> dict[str, Any]:
    """Query the Qdrant vector store with a natural language query."""
    query = normalize_semantic_text(query)
    qdrant_url = os.environ.get("QDRANT_URL", _DEFAULT_QDRANT_URL)

    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import FieldCondition, Filter, MatchValue
    except ImportError:
        return void("qdrant-client not installed", hint="pip install qdrant-client>=1.7.0")

    try:
        client = QdrantClient(url=qdrant_url)
    except Exception as e:
        return void(f"Failed to connect to Qdrant at {qdrant_url}: {e}")

    try:
        from arifosmcp.intelligence.embeddings import embed

        query_vector = embed(query)
    except Exception as e:
        return void(f"Failed to embed query: {e}")

    qdrant_filter = None
    if where:
        try:
            qdrant_filter = Filter(
                must=[FieldCondition(key=k, match=MatchValue(value=v)) for k, v in where.items()]
            )
        except Exception:
            pass  # skip malformed filter rather than hard-fail

    try:
        # Try modern Qdrant API (v1.8+) first, fallback to legacy API
        try:
            from qdrant_client.models import PointStruct

            query_result = client.query_points(
                collection_name=collection,
                query=query_vector,
                limit=n_results,
                query_filter=qdrant_filter,
                with_payload=True,
                with_vectors=include_embeddings,
            )
            results = query_result.points
        except (AttributeError, TypeError):
            # Fallback to legacy search API (pre-v1.8)
            results = client.search(
                collection_name=collection,
                query_vector=query_vector,
                limit=n_results,
                query_filter=qdrant_filter,
                with_payload=True,
                with_vectors=include_embeddings,
            )
    except Exception as e:
        try:
            cols = [c.name for c in client.get_collections().collections]
        except Exception:
            cols = []
        return partial(
            {"available_collections": cols},
            error=f"Query failed: {e}",
            hint=f"Available collections: {cols}" if cols else "No collections found",
        )

    hits = []
    for point in results:
        hit = {
            "id": str(point.id),
            "document": point.payload.get("content", str(point.payload)),
            "distance": round(1.0 - point.score, 4),  # cosine sim → distance
            "metadata": {k: v for k, v in point.payload.items() if k != "content"},
        }
        if include_embeddings and point.vector is not None:
            hit["embedding"] = point.vector
        hits.append(hit)

    return ok(
        {
            "collection": collection,
            "query": query,
            "count": len(hits),
            "results": hits,
        }
    )


def list_collections(_chroma_path: str | None = None) -> dict[str, Any]:
    """List all available Qdrant collections."""
    qdrant_url = os.environ.get("QDRANT_URL", _DEFAULT_QDRANT_URL)

    try:
        from qdrant_client import QdrantClient
    except ImportError:
        return void("qdrant-client not installed", hint="pip install qdrant-client>=1.7.0")

    try:
        client = QdrantClient(url=qdrant_url)
    except Exception as e:
        return void(str(e))

    try:
        cols = client.get_collections().collections
        return ok(
            {
                "qdrant_url": qdrant_url,
                "count": len(cols),
                "collections": [{"name": c.name} for c in cols],
            }
        )
    except Exception as e:
        return void(str(e))

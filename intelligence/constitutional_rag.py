"""
arifosmcp/intelligence/constitutional_rag.py — A-RIF Constitutional RAG Loader

Loads the AAA canon corpus from Hugging Face (ariffazil/AAA) into the
ConstitutionalMemoryStore at runtime, making the constitution queryable
via vector search rather than just hardcoded prompts.

Integration Points:
1. Load canons on first init_anchor (000_INIT) if not already loaded
2. Tag canon entries with source="constitutional_rag" and area=MAIN
3. On vault_ledger seal, record which AAA dataset revision was active
4. On vector_query, canon results get source_credibility=1.0 in H9 ranking

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# Default HF dataset coordinates
AAA_DATASET_REPO = "ariffazil/AAA"
AAA_CANONS_FILE = "theory/canons.jsonl"


class ConstitutionalRAGLoader:
    """Loads AAA canons from Hugging Face into ConstitutionalMemoryStore.

    Uses the `datasets` library when available, falling back to direct
    HTTP fetch from the Hugging Face Hub API.

    Attributes:
        _loaded: Whether canons have already been ingested this session.
        _revision: The dataset commit hash for provenance tracking.
        _canon_count: Number of canons loaded.
    """

    def __init__(self) -> None:
        self._loaded: bool = False
        self._revision: str = "unknown"
        self._canon_count: int = 0

    def is_loaded(self) -> bool:
        """Check if canons have been loaded this session."""
        return self._loaded

    def get_revision(self) -> str:
        """Return the AAA dataset revision string (commit hash)."""
        return self._revision

    async def load_canons(
        self,
        store: Any | None = None,
        project_id: str = "default",
    ) -> dict[str, Any]:
        """Load AAA canons into constitutional memory store.

        Args:
            store: ConstitutionalMemoryStore instance. If None, creates one.
            project_id: Target project for memory storage.

        Returns:
            dict with status, canon_count, revision, and any errors.
        """
        if self._loaded:
            logger.info("A-RIF: Canons already loaded (revision=%s)", self._revision)
            return {
                "status": "ALREADY_LOADED",
                "revision": self._revision,
                "canon_count": self._canon_count,
            }

        canons: list[dict[str, Any]] = []
        revision = "unknown"

        # Strategy 1: Try `datasets` library (preferred)
        try:
            canons, revision = await self._load_via_datasets()
        except Exception as e:
            logger.warning("A-RIF: datasets library unavailable (%s), trying HTTP fetch", e)
            # Strategy 2: Direct HTTP fetch from HF Hub
            try:
                canons, revision = await self._load_via_http()
            except Exception as e2:
                logger.error("A-RIF: All canon loading strategies failed: %s", e2)
                return {"status": "FAILED", "error": str(e2)}

        if not canons:
            logger.warning("A-RIF: No canons found in dataset")
            return {"status": "EMPTY", "canon_count": 0}

        # Store canons into ConstitutionalMemoryStore
        stored_count = 0
        errors: list[str] = []

        if store is None:
            try:
                from arifosmcp.agentzero.memory.constitutional_memory import (
                    ConstitutionalMemoryStore,
                )
                store = ConstitutionalMemoryStore()
            except Exception as e:
                logger.error("A-RIF: Cannot create ConstitutionalMemoryStore: %s", e)
                return {"status": "STORE_UNAVAILABLE", "error": str(e)}

        from arifosmcp.agentzero.memory.constitutional_memory import MemoryArea

        await store.initialize_project(project_id)

        for canon in canons:
            content = canon.get("text") or canon.get("content") or json.dumps(canon)
            try:
                ok, memory_id, error = await store.store(
                    content=content,
                    area=MemoryArea.MAIN,
                    project_id=project_id,
                    source="constitutional_rag",
                    source_agent="aaa_canon_loader",
                )
                if ok:
                    stored_count += 1
                else:
                    errors.append(error or "unknown")
            except Exception as e:
                errors.append(str(e))

        self._loaded = True
        self._revision = revision
        self._canon_count = stored_count

        # Publish revision to environment for Vault999 provenance binding
        os.environ["AAA_DATASET_REVISION"] = revision

        logger.info(
            "A-RIF: Loaded %d/%d canons (revision=%s, errors=%d)",
            stored_count,
            len(canons),
            revision[:12],
            len(errors),
        )

        return {
            "status": "LOADED",
            "canon_count": stored_count,
            "total_canons": len(canons),
            "revision": revision,
            "errors": errors[:5] if errors else [],
        }

    async def _load_via_datasets(self) -> tuple[list[dict[str, Any]], str]:
        """Load canons using HuggingFace datasets library."""
        import asyncio
        from datasets import load_dataset

        ds = await asyncio.to_thread(
            load_dataset,
            AAA_DATASET_REPO,
            data_files=AAA_CANONS_FILE,
            split="train",
        )

        # Extract revision from dataset info
        revision = getattr(ds.info, "download_checksums", {})
        if not revision:
            # Try version field
            revision = getattr(ds.info, "version", "unknown")
        revision = str(revision)[:40] if revision else "unknown"

        canons = [dict(row) for row in ds]
        return canons, revision

    async def _load_via_http(self) -> tuple[list[dict[str, Any]], str]:
        """Load canons via direct HTTP fetch from HF Hub API."""
        import aiohttp

        # Get repo info for revision
        api_url = f"https://huggingface.co/api/datasets/{AAA_DATASET_REPO}"
        file_url = (
            f"https://huggingface.co/datasets/{AAA_DATASET_REPO}"
            f"/resolve/main/{AAA_CANONS_FILE}"
        )

        revision = "unknown"
        canons: list[dict[str, Any]] = []

        hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
        headers: dict[str, str] = {}
        if hf_token:
            headers["Authorization"] = f"Bearer {hf_token}"

        async with aiohttp.ClientSession() as session:
            # Get revision
            try:
                async with session.get(api_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        revision = data.get("sha", "unknown")
            except Exception as e:
                logger.warning("A-RIF: Could not fetch dataset revision: %s", e)

            # Get canons file
            async with session.get(file_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"HF fetch failed with status {resp.status}")
                text = await resp.text()
                for line in text.strip().split("\n"):
                    line = line.strip()
                    if line:
                        try:
                            canons.append(json.loads(line))
                        except json.JSONDecodeError:
                            logger.warning("A-RIF: Skipping invalid JSONL line")

        return canons, revision


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON (shared across the runtime)
# ═══════════════════════════════════════════════════════════════════════════

_rag_loader: ConstitutionalRAGLoader | None = None


def get_rag_loader() -> ConstitutionalRAGLoader:
    """Get or create singleton ConstitutionalRAGLoader."""
    global _rag_loader
    if _rag_loader is None:
        _rag_loader = ConstitutionalRAGLoader()
    return _rag_loader


__all__ = ["ConstitutionalRAGLoader", "get_rag_loader"]

"""
arifosmcp/init_000/sync_registry.py

Sync the 3-layer Model Registry from JSON files into SQLite.

This bridges the file-based registry (arifOS-model-registry/) with the
runtime database for faster lookups and ACID guarantees.

Usage:
    python -m arifosmcp.init_000.sync_registry

Timestamp: 2026-03-28
ZKPC Root: 3-layer-binding-v2026.03.28
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from arifosmcp.init_000.models import init_db
from arifosmcp.init_000 import db


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─── Path Resolution ──────────────────────────────────────────────────────────


def _registry_path() -> Path | None:
    """Find the arifOS-model-registry directory."""
    candidates = [
        Path("C:/ariffazil/arifOS/arifOS-model-registry"),
        Path("/opt/arifos/arifOS-model-registry"),
        Path(__file__).parent.parent.parent.parent / "arifOS-model-registry",
    ]
    for p in candidates:
        if p.exists() and p.is_dir():
            return p
    return None


# ─── Sync Functions ───────────────────────────────────────────────────────────


def sync_provider_souls(registry_path: Path) -> int:
    """Load provider_souls/*.json into SQLite."""
    souls_dir = registry_path / "provider_souls"
    if not souls_dir.exists():
        print(f"⚠️  Provider souls directory not found: {souls_dir}")
        return 0

    count = 0
    for json_file in souls_dir.glob("*.json"):
        # Skip test fixtures
        if json_file.name.startswith("wrong_"):
            continue
            
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Map to db schema
        db.upsert_provider_soul({
            "provider_key": data.get("provider_key", ""),
            "family_key": data.get("family_key", ""),
            "soul_label": data.get("soul_label", ""),
            "communication_style": data.get("communication_style", []),
            "reasoning_style": data.get("reasoning_style", []),
            "default_role_fit": data.get("default_role_fit", ["assistant"]),
            "notes": data.get("in_one_sentence", ""),
        })
        count += 1
    
    return count


def sync_deployments(registry_path: Path) -> int:
    """Load runtime_profiles/*.json into SQLite deployments table."""
    profiles_dir = registry_path / "runtime_profiles"
    if not profiles_dir.exists():
        print(f"⚠️  Runtime profiles directory not found: {profiles_dir}")
        return 0

    count = 0
    for json_file in profiles_dir.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Map to db schema
        db.upsert_deployment({
            "deployment_id": data.get("deployment_id", json_file.stem),
            "provider_key": data.get("provider_key", ""),
            "family_key": data.get("family_key", ""),
            "model_id": data.get("model_id", ""),
            "model_variant": data.get("model_variant"),
            "tools_live": data.get("tools_live", []),
            "web_access": data.get("web_on", False),
            "memory_mode": data.get("memory_mode", "session_only"),
            "execution_mode": data.get("execution_mode", "advisory"),
            "side_effects_allowed": data.get("side_effects_allowed", False),
            "auth_level": data.get("auth_level", "read_only"),
            "verified_at": data.get("verified_at") or _now(),
            "is_active": True,
        })
        count += 1
    
    return count


# ─── Main Entry ───────────────────────────────────────────────────────────────


def sync_all() -> dict[str, Any]:
    """
    Full sync from JSON registry to SQLite.
    
    Returns:
        {"souls": int, "deployments": int, "status": str}
    """
    # Initialize database schema
    init_db()
    
    registry_path = _registry_path()
    if not registry_path:
        return {
            "souls": 0,
            "deployments": 0,
            "status": "error: registry not found"
        }
    
    print(f"📦 Syncing from: {registry_path}")
    
    souls_count = sync_provider_souls(registry_path)
    deployments_count = sync_deployments(registry_path)
    
    return {
        "souls": souls_count,
        "deployments": deployments_count,
        "status": "ok"
    }


if __name__ == "__main__":
    result = sync_all()
    print(f"\n✅ Sync complete:")
    print(f"   Souls: {result['souls']}")
    print(f"   Deployments: {result['deployments']}")
    print(f"   Status: {result['status']}")

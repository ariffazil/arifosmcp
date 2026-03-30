"""
arifosmcp/runtime/vault_redis.py — Redis-backed VAULT999

Replaces file-based vault with Redis storage for persistence across restarts.
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

import redis.asyncio as redis
from cryptography.fernet import Fernet


class RedisVaultStore:
    """Redis-backed vault with optional Fernet encryption."""
    
    def __init__(self, host: str = "redis", port: int = 6379, db: int = 0):
        self.host = host
        self.port = port
        self.db = db
        self._redis: redis.Redis | None = None
        self._encryption_key = os.environ.get("STORAGE_ENCRYPTION_KEY")
        if self._encryption_key:
            self._fernet = Fernet(self._encryption_key.encode())
        else:
            self._fernet = None
    
    async def _get_redis(self) -> redis.Redis:
        """Lazy Redis connection."""
        if self._redis is None:
            self._redis = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True
            )
        return self._redis
    
    async def seal(self, entry: dict[str, Any]) -> str:
        """
        Seal an entry to Redis vault.
        
        Returns:
            Hash of the sealed entry (for Merkle chain)
        """
        r = await self._get_redis()
        
        # Compute Merkle hash
        entry_json = json.dumps(entry, sort_keys=True, default=str)
        entry_hash = f"0x{hash(entry_json) & 0xFFFFFFFFFFFFFFFF:016x}"
        entry["hash"] = entry_hash
        
        # Get previous hash for chain
        prev_entry = await r.lindex("vault999:chain", -1)
        if prev_entry:
            prev_data = json.loads(prev_entry)
            entry["prev_hash"] = prev_data.get("hash", "0x" + "0" * 64)
        else:
            entry["prev_hash"] = "0x" + "0" * 64
        
        entry["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # Store in Redis list (chronological)
        entry_json = json.dumps(entry, default=str)
        
        # Encrypt if key available
        if self._fernet:
            entry_json = self._fernet.encrypt(entry_json.encode()).decode()
        
        await r.rpush("vault999:chain", entry_json)
        
        # Also index by session_id for fast lookup
        session_id = entry.get("session_id", "unknown")
        await r.sadd(f"vault999:sessions:{session_id}", entry_json)
        
        return entry_hash
    
    async def get_chain(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent vault entries (newest first)."""
        r = await self._get_redis()
        entries = await r.lrange("vault999:chain", -limit, -1)
        
        result = []
        for entry_json in reversed(entries):  # Newest first
            if self._fernet:
                try:
                    entry_json = self._fernet.decrypt(entry_json.encode()).decode()
                except Exception:
                    pass  # Not encrypted or bad key
            try:
                result.append(json.loads(entry_json))
            except json.JSONDecodeError:
                continue
        return result
    
    async def get_session_entries(self, session_id: str) -> list[dict[str, Any]]:
        """Get all entries for a specific session."""
        r = await self._get_redis()
        entries = await r.smembers(f"vault999:sessions:{session_id}")
        
        result = []
        for entry_json in entries:
            if self._fernet:
                try:
                    entry_json = self._fernet.decrypt(entry_json.encode()).decode()
                except Exception:
                    pass
            try:
                result.append(json.loads(entry_json))
            except json.JSONDecodeError:
                continue
        # Sort by timestamp
        result.sort(key=lambda x: x.get("timestamp", ""))
        return result
    
    async def verify_chain(self) -> tuple[bool, str]:
        """
        Verify Merkle chain integrity.
        
        Returns:
            (is_valid, message)
        """
        r = await self._get_redis()
        entries = await r.lrange("vault999:chain", 0, -1)
        
        if not entries:
            return True, "Empty chain (valid)"
        
        prev_hash = "0x" + "0" * 64
        for i, entry_json in enumerate(entries):
            if self._fernet:
                try:
                    entry_json = self._fernet.decrypt(entry_json.encode()).decode()
                except Exception as e:
                    return False, f"Entry {i}: Decryption failed: {e}"
            
            try:
                entry = json.loads(entry_json)
            except json.JSONDecodeError as e:
                return False, f"Entry {i}: JSON decode failed: {e}"
            
            # Verify prev_hash linkage
            if entry.get("prev_hash") != prev_hash:
                return False, f"Entry {i}: Hash chain broken"
            
            prev_hash = entry.get("hash", "0x" + "0" * 64)
        
        return True, f"Chain verified: {len(entries)} entries intact"
    
    async def get_last_hash(self) -> str:
        """Get hash of most recent entry (for new entry linking)."""
        r = await self._get_redis()
        last = await r.lindex("vault999:chain", -1)
        if not last:
            return "0x" + "0" * 64
        
        if self._fernet:
            try:
                last = self._fernet.decrypt(last.encode()).decode()
            except Exception:
                pass
        
        try:
            entry = json.loads(last)
            return entry.get("hash", "0x" + "0" * 64)
        except json.JSONDecodeError:
            return "0x" + "0" * 64


# Global instance
_vault_store: RedisVaultStore | None = None


def get_vault_store() -> RedisVaultStore:
    """Get singleton Redis vault store."""
    global _vault_store
    if _vault_store is None:
        _vault_store = RedisVaultStore()
    return _vault_store

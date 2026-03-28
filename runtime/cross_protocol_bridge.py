"""
arifosmcp/runtime/cross_protocol_bridge.py — Cross-Protocol 888_HOLD Bridge

Enables real-time broadcast of 888_HOLD states from any protocol (A2A, MCP)
to all WebMCP browser clients via Redis pub/sub + WebSocket.

F1 Amanah: All handoffs logged to VAULT999 with pre-execution hash.

ΔΩΨ | ARIF — Ditempa Bukan Diberi
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Coroutine

import aiofiles
import redis.asyncio as redis

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class HoldEvent:
    """Immutable 888_HOLD event for cross-protocol broadcast."""
    hold_id: str
    source_protocol: str  # "a2a", "mcp", "webmcp"
    action_type: str
    reason: str
    risk_level: str  # low, medium, high, critical
    floor_violations: list[str]
    session_id: str
    actor_id: str
    timestamp: str = ""
    pre_execution_hash: str = ""  # F1 Amanah: hash of action payload
    
    def __post_init__(self):
        if not self.timestamp:
            object.__setattr__(
                self, 
                "timestamp", 
                datetime.now(timezone.utc).isoformat()
            )


class CrossProtocolHoldBridge:
    """
    Redis-backed bridge for 888_HOLD events.
    
    Publishes HOLD events from A2A/MCP → Redis → WebMCP WebSocket consumers.
    """
    
    # Redis channel patterns
    CHANNEL_HOLD_NEW = "arifos:hold:new"
    CHANNEL_HOLD_RESOLVED = "arifos:hold:resolved"
    CHANNEL_PREFIX_HOLD = "arifos:hold:"
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._redis: redis.Redis | None = None
        self._pubsub: redis.client.PubSub | None = None
        self._subscribers: list[Callable[[HoldEvent], Coroutine]] = []
        self._running = False
        
    async def connect(self):
        """Initialize Redis connection."""
        self._redis = await redis.from_url(
            self.redis_url, 
            decode_responses=True
        )
        self._pubsub = self._redis.pubsub()
        logger.info("CrossProtocolHoldBridge connected to Redis")
        
    async def disconnect(self):
        """Cleanup Redis connection."""
        if self._pubsub:
            await self._pubsub.unsubscribe()
        if self._redis:
            await self._redis.close()
        self._running = False
        
    def _compute_pre_execution_hash(self, payload: dict) -> str:
        """
        F1 AMANAH: Compute pre-execution hash for reversibility proof.
        
        This hash is logged to VAULT999 BEFORE the action is approved.
        If the connection drops, the hash proves the intent existed.
        """
        canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(canonical.encode()).hexdigest()[:32]
        
    async def publish_hold(
        self,
        hold_event: HoldEvent,
        action_payload: dict | None = None,
    ) -> str:
        """
        Publish 888_HOLD event to all protocols.
        
        Args:
            hold_event: The hold event metadata
            action_payload: Full action payload for F1 hash computation
            
        Returns:
            The pre_execution_hash (logged to VAULT999)
        """
        if not self._redis:
            raise RuntimeError("Bridge not connected. Call connect() first.")
            
        # F1 AMANAH: Compute pre-execution hash
        pre_hash = ""
        if action_payload:
            pre_hash = self._compute_pre_execution_hash(action_payload)
            # Create new event with hash (immutable, so reconstruct)
            hold_event = HoldEvent(
                **{
                    **asdict(hold_event),
                    "pre_execution_hash": pre_hash,
                }
            )
            
        # Serialize and publish
        event_json = json.dumps(asdict(hold_event))
        
        # Publish to general new-holds channel
        await self._redis.publish(self.CHANNEL_HOLD_NEW, event_json)
        
        # Publish to specific hold channel (for targeted subscriptions)
        specific_channel = f"{self.CHANNEL_PREFIX_HOLD}{hold_event.hold_id}"
        await self._redis.publish(specific_channel, event_json)
        
        logger.warning(
            f"[888_HOLD BROADCAST] {hold_event.hold_id} from {hold_event.source_protocol} "
            f"pre_hash={pre_hash[:16]}..."
        )
        
        return pre_hash
        
    async def publish_resolution(
        self,
        hold_id: str,
        decision: str,  # "APPROVED" or "VOID"
        decided_by: str,
        justification: str = "",
    ):
        """Publish HOLD resolution to all subscribers."""
        if not self._redis:
            return
            
        resolution = {
            "hold_id": hold_id,
            "decision": decision,
            "decided_by": decided_by,
            "justification": justification,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        await self._redis.publish(
            self.CHANNEL_HOLD_RESOLVED, 
            json.dumps(resolution)
        )
        
        logger.info(f"[888_HOLD RESOLVED] {hold_id} = {decision} by {decided_by}")
        
    async def subscribe(self, callback: Callable[[HoldEvent], Coroutine]):
        """Subscribe to HOLD events (used by WebMCP Gateway)."""
        self._subscribers.append(callback)
        
        if not self._running:
            self._running = True
            asyncio.create_task(self._listen_loop())
            
    async def _listen_loop(self):
        """Background task: listen for Redis messages and fan-out to subscribers."""
        if not self._pubsub:
            return
            
        await self._pubsub.psubscribe(f"{self.CHANNEL_PREFIX_HOLD}*")
        
        async for message in self._pubsub.listen():
            if message["type"] not in ("pmessage", "message"):
                continue
                
            try:
                data = json.loads(message["data"])
                event = HoldEvent(**data)
                
                # Fan out to all subscribers
                for callback in self._subscribers:
                    try:
                        await callback(event)
                    except Exception as e:
                        logger.error(f"Subscriber callback failed: {e}")
                        
            except Exception as e:
                logger.error(f"Failed to parse HOLD event: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCE (shared across protocols)
# ═══════════════════════════════════════════════════════════════════════════

_hold_bridge: CrossProtocolHoldBridge | None = None


async def get_hold_bridge() -> CrossProtocolHoldBridge:
    """Get or create the singleton hold bridge."""
    global _hold_bridge
    if _hold_bridge is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        _hold_bridge = CrossProtocolHoldBridge(redis_url)
        await _hold_bridge.connect()
    return _hold_bridge

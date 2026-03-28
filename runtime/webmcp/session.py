"""
Web Session Management
F11 Command Auth for browser sessions.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass
from typing import Any, Optional

import redis.asyncio as redis

from arifosmcp.core.enforcement.auth_continuity import mint_auth_context


@dataclass
class WebSession:
    """Web browser session with constitutional auth."""
    
    session_id: str
    auth_context: dict[str, Any]
    created_at: float
    expires_at: float
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    
    @property
    def is_expired(self) -> bool:
        return time.time() > self.expires_at
    
    @property
    def age_seconds(self) -> float:
        return time.time() - self.created_at
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "auth_context": self.auth_context,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "user_agent": self.user_agent,
            "ip_address": self.ip_address,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WebSession":
        return cls(**data)


class WebSessionManager:
    """
    Manages browser sessions with F11 Command Auth.
    
    Links browser cookies to arifOS auth_context with
    cryptographic continuity via VAULT999.
    """
    
    def __init__(self, redis_client: redis.Redis, config: Any):
        self.redis = redis_client
        self.config = config
        self._key_prefix = "arifos:web:session:"
    
    async def mint_session(
        self,
        actor_id: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        human_approval: bool = False,
    ) -> WebSession:
        """
        Mint new web session with F11 auth continuity.
        
        Args:
            actor_id: Declared identity
            user_agent: Browser user agent
            ip_address: Client IP for geo-binding
            human_approval: Whether human has pre-approved
            
        Returns:
            WebSession with auth_context
        """
        session_id = f"web-{uuid.uuid4().hex[:16]}"
        now = time.time()
        
        # Mint F11-compliant auth_context
        auth_context = mint_auth_context(
            session_id=session_id,
            actor_id=actor_id,
            token_fingerprint=hashlib.sha256(
                f"{session_id}:{actor_id}:{now}".encode()
            ).hexdigest()[:16],
            approval_scope=["web", "read", "search"] if not human_approval else ["*"],
            parent_signature="",
            authority_level="web_session",
        )
        
        session = WebSession(
            session_id=session_id,
            auth_context=auth_context,
            created_at=now,
            expires_at=now + self.config.SESSION_TTL,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        
        # Store in Redis with TTL (F11 continuity)
        await self.redis.setex(
            f"{self._key_prefix}{session_id}",
            self.config.SESSION_TTL,
            json.dumps(session.to_dict()),
        )
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[WebSession]:
        """Retrieve session by ID."""
        data = await self.redis.get(f"{self._key_prefix}{session_id}")
        if not data:
            return None
        
        session = WebSession.from_dict(json.loads(data))
        
        # Check expiration (F11)
        if session.is_expired:
            await self.revoke_session(session_id, "expired")
            return None
        
        return session
    
    async def refresh_session(self, session_id: str) -> Optional[WebSession]:
        """Extend session TTL (F11 continuity)."""
        session = await self.get_session(session_id)
        if not session:
            return None
        
        # Extend expiration
        session.expires_at = time.time() + self.config.SESSION_TTL
        
        # Update Redis
        await self.redis.setex(
            f"{self._key_prefix}{session_id}",
            self.config.SESSION_TTL,
            json.dumps(session.to_dict()),
        )
        
        return session
    
    async def revoke_session(self, session_id: str, reason: str) -> None:
        """
        Revoke session (kill switch - F11).
        
        Args:
            session_id: Session to revoke
            reason: Audit reason
        """
        # Delete from Redis
        await self.redis.delete(f"{self._key_prefix}{session_id}")
        
        # Log to VAULT999
        await self._log_revocation(session_id, reason)
    
    async def _log_revocation(self, session_id: str, reason: str) -> None:
        """Log session revocation to VAULT999 (F1 Amanah)."""
        # This would call vault_seal in production
        pass
    
    async def list_active_sessions(self, actor_id: Optional[str] = None) -> list[WebSession]:
        """List all active web sessions."""
        keys = await self.redis.keys(f"{self._key_prefix}*")
        sessions = []
        
        for key in keys:
            data = await self.redis.get(key)
            if data:
                session = WebSession.from_dict(json.loads(data))
                if actor_id is None or session.auth_context.get("actor_id") == actor_id:
                    sessions.append(session)
        
        return sessions

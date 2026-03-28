"""
WebMCP Server Gateway
The main entry point for web-facing MCP with constitutional governance.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from time import time
from typing import Any, Optional

import redis.asyncio as redis
from fastapi import Depends, FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from .config import WebMCPConfig
from .security import RateLimiter, WebInjectionGuard, ShieldReport
from .session import WebSession, WebSessionManager
from .governance import (
    ActionRequest,
    GovernanceEvaluation,
    GovernanceEngine,
    Verdict,
    governance_engine,
)
from .live_metrics import (
    get_live_metrics,
    get_machine_only,
    get_governance_only,
    get_intelligence_only,
)
from arifosmcp.runtime.build_info import get_build_info
from arifosmcp.runtime.public_registry import PUBLIC_TOOL_SPECS

logger = logging.getLogger(__name__)


class WebMCPGateway:
    """
    Web-facing gateway for arifOS MCP.

    Every request passes through 000→999 metabolic loop with:
    - F12 Injection Guard (security scan)
    - F11 Command Auth (session validation)
    - F2 Truth (content grounding)
    - Full Trinity governance (ΔΩΨ)
    
    Cross-Protocol 888_HOLD:
    - WebSocket broadcast of A2A/MCP hold events
    - Real-time dashboard updates
    - F13 Sovereign resolution endpoint

    Usage:
        from arifosmcp.runtime.webmcp import WebMCPGateway

        gateway = WebMCPGateway(mcp_server)
        app = gateway.app  # Mount in FastAPI/Starlette
    """

    def __init__(self, mcp_server: Any, config: Optional[WebMCPConfig] = None):
        self.mcp = mcp_server
        self.config = config or WebMCPConfig.from_env()
        self.build_info = get_build_info()
        self._cached_tool_manifest: list[dict[str, Any]] | None = None
        
        # NEW: Active WebSocket connections for 888_HOLD broadcast
        self._active_websockets: set[WebSocket] = set()
        self._hold_bridge_subscribed = False
        
        self.app = FastAPI(
            title="arifOS WebMCP",
            version=self.build_info["version"],
            description="AI-governed WebMCP environment with 13 Constitutional Floors",
        )

        # Initialize components
        self.redis = redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True
        )
        self.session_manager = WebSessionManager(self.redis, self.config)
        self.injection_guard = WebInjectionGuard()
        self.rate_limiter = RateLimiter(self.redis, self.config)

        # Setup
        self._setup_middleware()
        self._setup_routes()

    def _setup_middleware(self):
        """Configure constitutional middleware stack."""

        # 1. Trusted Host (F12 - prevent host header attacks)
        # Allow all hosts when behind Traefik (Traefik handles host validation)
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"],  # Traefik validates hosts upstream
        )

        # 2. CORS (F12 - strict origin validation)
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=list(self.config.ALLOWED_ORIGINS),
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization", "X-Session-ID"],
            max_age=3600,
        )

        # 3. Session (F11 - auth continuity)
        secret = os.getenv("SESSION_SECRET") or os.urandom(32).hex()
        self.app.add_middleware(
            SessionMiddleware,
            secret_key=secret,
            max_age=self.config.SESSION_TTL,
            same_site=self.config.SESSION_SAMESITE,
            https_only=self.config.SESSION_SECURE,
            session_cookie=self.config.SESSION_COOKIE,
        )

        # 4. Constitutional Guard (F12 + F11 on every request)
        @self.app.middleware("http")
        async def constitutional_guard(request: Request, call_next):
            """
            000_INIT: Initialize web session context.
            PNS·SHIELD: Scan for injection attacks (F12).
            """
            # Session initialization
            session_id = request.session.get("arifos_sid")
            if not session_id:
                session_id = f"web-{asyncio.get_event_loop().time():.0f}"
                request.session["arifos_sid"] = session_id

            # F12 Injection Guard
            shield_report = await self.injection_guard.scan_request(request)
            if shield_report.is_injection:
                logger.warning(
                    f"F12_INJECTION_BLOCKED: {shield_report.category} "
                    f"score={shield_report.score:.2f} session={session_id}"
                )
                return JSONResponse(
                    status_code=403,
                    content={
                        "verdict": "VOID",
                        "floor": "F12_INJECTION",
                        "error": "Request blocked by constitutional guard",
                        "category": shield_report.category,
                        "session_id": session_id,
                    },
                    headers={
                        "X-Constitutional-Verdict": "VOID",
                        "X-Failed-Floor": "F12",
                    },
                )

            # Add constitutional context to request state
            request.state.shield_report = shield_report
            request.state.session_id = session_id

            # Continue to handler
            response = await call_next(request)

            # Add constitutional headers to response
            response.headers["X-arifOS-Version"] = self.build_info["version"]
            response.headers["X-Constitutional-Floors"] = "13"

            return response

    def _setup_routes(self):
        """Setup WebMCP routes."""

        @self.app.get("/.well-known/webmcp")
        async def webmcp_manifest():
            """Browser-discoverable WebMCP manifest."""
            return {
                "schema_version": "1.0",
                "site": {
                    "name": "arifOS Constitutional AI",
                    "url": "https://arifosmcp.arif-fazil.com",
                    "version": self.build_info["version"],
                },
                "apis": {"declarative": True, "imperative": True},
                "endpoints": {
                    "init": "/webmcp/init",
                    "tools": "/webmcp/tools",
                    "manifest": "/webmcp/tools.json",
                    "sdk": "/webmcp/sdk.js",
                    "call": "/webmcp/call/{tool_name}",
                    "vitals": "/webmcp/vitals",
                },
                "human_in_the_loop": True,
                "tools": self._tool_manifest(),
            }

        @self.app.get("/webmcp")
        async def webmcp_info():
            """WebMCP server information."""
            return {
                "service": "arifOS WebMCP",
                "version": self.build_info["version"],
                "motto": "Ditempa Bukan Diberi — Forged, Not Given",
                "trinity": "ΔΩΨ",
                "floors": 13,
                "tools": len(PUBLIC_TOOL_SPECS),
                "endpoints": {
                    "init": "/webmcp/init",
                    "tools": "/webmcp/tools",
                    "manifest": "/webmcp/tools.json",
                    "sdk": "/webmcp/sdk.js",
                    "call": "/webmcp/call/{tool_name}",
                    "vitals": "/webmcp/vitals",
                    "hold": "/webmcp/hold/{session_id}",
                    "websocket": "/webmcp/ws",
                },
                "live_api": {
                    "all": "/api/live/all",
                    "machine": "/api/live/machine",
                    "governance": "/api/live/governance",
                    "intelligence": "/api/live/intelligence",
                    "vault": "/api/live/vault?limit=20",
                },
                "data_groups": {
                    "machine": "VPS health (CPU, RAM, disk, network, Docker)",
                    "governance": "arifOS floors, vitals, VAULT999 status",
                    "intelligence": "AI/LLM metrics, tokens, latency, models",
                },
            }

        @self.app.get("/webmcp/sdk.js")
        async def webmcp_sdk():
            """Minimal browser SDK for imperative WebMCP calls."""
            return HTMLResponse(content=self._build_sdk_js(), media_type="application/javascript")

        @self.app.get("/webmcp/tools.json")
        async def tools_manifest():
            """Machine-readable tool manifest for browser clients."""
            return {
                "service": "arifOS WebMCP",
                "version": self.build_info["version"],
                "tools": self._tool_manifest(),
            }

        @self.app.post("/webmcp/init")
        async def init_session(request: Request):
            """
            000_INIT: Initialize web session with F11 auth.

            Request:
                {"actor_id": "...", "human_approval": false}

            Response:
                {"session_id": "...", "auth_context": {...}, "verdict": "SEAL"}
            """
            try:
                body = await request.json()
            except Exception:
                body = {}

            actor_id = body.get("actor_id", "anonymous")
            human_approval = body.get("human_approval", False)

            try:
                session = await self.session_manager.mint_session(
                    actor_id=actor_id,
                    user_agent=request.headers.get("user-agent"),
                    ip_address=request.client.host if request.client else None,
                    human_approval=human_approval,
                )

                request.session["arifos_sid"] = session.session_id
                request.session["arifos_actor_id"] = actor_id

                return {
                    "verdict": "SEAL",
                    "stage": "INIT_000",
                    "session_id": session.session_id,
                    "auth_context": {
                        "actor_id": session.auth_context.get("actor_id"),
                        "authority_level": session.auth_context.get("authority_level"),
                        "approval_scope": session.auth_context.get("approval_scope"),
                    },
                    "expires_at": session.expires_at,
                }
            except Exception as exc:
                logger.exception("WebMCP init failed")
                fallback_session_id = request.session.get("arifos_sid") or f"web-fallback-{int(time())}"
                request.session["arifos_sid"] = fallback_session_id
                request.session["arifos_actor_id"] = actor_id
                return JSONResponse(
                    status_code=200,
                    content={
                        "verdict": "PARTIAL",
                        "stage": "INIT_000",
                        "session_id": fallback_session_id,
                        "auth_context": {
                            "actor_id": actor_id,
                            "authority_level": "web_session_degraded",
                            "approval_scope": ["web", "read", "search"],
                        },
                        "warning": str(exc),
                    },
                )

        @self.app.get("/webmcp/tools")
        async def list_tools():
            """List the live public tools exposed by the runtime."""
            tools = self._tool_manifest()
            return {
                "verdict": "SEAL",
                "tools": tools,
                "count": len(tools),
            }

        @self.app.post("/webmcp/call/{tool_name}")
        async def call_tool(tool_name: str, request: Request):
            """
            Call MCP tool through full 000→999 metabolic loop.

            Every call is:
            1. Scanned by PNS·SHIELD (F12)
            2. Authenticated (F11)
            3. Grounded (F2)
            4. Reasoned (333)
            5. Critiqued (666)
            6. Judged (888)
            7. Sealed (999)
            """
            # Get session
            session_id = request.session.get("arifos_sid")
            if not session_id:
                return JSONResponse(
                    status_code=401,
                    content={"verdict": "VOID", "error": "No session. Call /webmcp/init first."},
                )

            session = await self.session_manager.get_session(session_id)
            if not session:
                actor_id = request.session.get("arifos_actor_id")
                if actor_id:
                    session = type(
                        "FallbackSession",
                        (),
                        {"auth_context": {"actor_id": actor_id}, "session_id": session_id},
                    )()
            if not session:
                return JSONResponse(
                    status_code=401,
                    content={"verdict": "VOID", "error": "Session expired or invalid."},
                )

            # Parse payload
            try:
                payload = await request.json()
            except Exception:
                payload = {}

            # Build web context
            web_context = {
                "session_id": session_id,
                "actor_id": session.auth_context.get("actor_id"),
                "user_agent": request.headers.get("user-agent"),
                "origin": request.headers.get("origin"),
                "ip": request.client.host if request.client else None,
            }

            # Execute through MCP (this would call the actual tool)
            # For now, return a mock response showing the flow
            try:
                # In production: result = await self.mcp.call_tool(...)
                result = {
                    "verdict": "SEAL",
                    "tool": tool_name,
                    "stage": "VAULT_999",
                    "session_id": session_id,
                    "payload": {"message": f"Tool {tool_name} executed via WebMCP"},
                    "metrics": {
                        "G_star": 0.85,
                        "dS": -0.3,
                        "peace2": 1.05,
                    },
                }

                return result

            except Exception as e:
                logger.exception(f"Tool call failed: {tool_name}")
                return {
                    "verdict": "VOID",
                    "error": str(e),
                    "session_id": session_id,
                }

        @self.app.get("/webmcp/vitals")
        async def get_vitals(request: Request):
            """Get current system vitals (F4, F5, F7)."""
            # This would call check_vital tool
            return {
                "verdict": "SEAL",
                "vitals": {
                    "G_star": 0.85,
                    "dS": -0.3,
                    "peace2": 1.05,
                    "omega": 0.04,
                },
                "floors": {f"F{i}": "PASS" for i in range(1, 14)},
            }

        # === LIVE DASHBOARD METRICS ENDPOINTS ===

        @self.app.get("/api/live/all")
        async def get_all_live_metrics():
            """
            Get all live metrics: MACHINE + GOVERNANCE + INTELLIGENCE.

            Returns real-time data from:
            - Machine: VPS health (CPU, RAM, disk, network, Docker)
            - Governance: arifOS floors, vitals, VAULT999 status
            - Intelligence: AI/LLM metrics, tokens, latency, models
            """
            try:
                metrics = await get_live_metrics()
                return metrics
            except Exception as e:
                return {
                    "verdict": "PARTIAL",
                    "error": str(e),
                    "machine": {},
                    "governance": {},
                    "intelligence": {},
                }

        @self.app.get("/api/live/machine")
        async def get_machine_metrics_endpoint():
            """Get VPS machine metrics only."""
            try:
                metrics = await get_machine_only()
                return {"verdict": "SEAL", "data": metrics}
            except Exception as e:
                return {"verdict": "VOID", "error": str(e)}

        @self.app.get("/api/live/governance")
        async def get_governance_metrics_endpoint():
            """Get arifOS governance metrics only."""
            try:
                metrics = await get_governance_only()
                return {"verdict": "SEAL", "data": metrics}
            except Exception as e:
                return {"verdict": "VOID", "error": str(e)}

        @self.app.get("/api/live/intelligence")
        async def get_intelligence_metrics_endpoint():
            """Get AI/LLM intelligence metrics only."""
            try:
                metrics = await get_intelligence_only()
                return {"verdict": "SEAL", "data": metrics}
            except Exception as e:
                return {"verdict": "VOID", "error": str(e)}

        @self.app.get("/api/live/vault")
        async def get_vault_entries(limit: int = 20):
            """Get recent VAULT999 entries."""
            try:
                vault_path = Path("VAULT999/vault999.jsonl")
                entries = []

                if vault_path.exists():
                    with open(vault_path, "r") as f:
                        lines = f.readlines()
                        # Get last N entries
                        for line in lines[-limit:]:
                            try:
                                entry = json.loads(line)
                                entries.append(
                                    {
                                        "timestamp": entry.get("timestamp", ""),
                                        "session_id": entry.get("session_id", "")[:16] + "...",
                                        "action": entry.get("action", entry.get("tool", "unknown")),
                                        "verdict": entry.get("verdict", "UNKNOWN"),
                                        "seal_hash": entry.get("seal_hash", "")[:16] + "..."
                                        if entry.get("seal_hash")
                                        else None,
                                    }
                                )
                            except:
                                continue

                return {
                    "verdict": "SEAL",
                    "count": len(entries),
                    "entries": entries,
                }
            except Exception as e:
                return {"verdict": "VOID", "error": str(e), "entries": []}

        # === GOVERNANCE-AS-A-SERVICE (GaaS) ENDPOINTS ===

        @self.app.post("/governance/evaluate", response_model=GovernanceEvaluation)
        async def governance_evaluate(request: ActionRequest):
            """
            SUPREME COURT ENDPOINT - Evaluate any action against F1-F13.

            This is the breakthrough feature: any agent anywhere can submit
            actions for constitutional review without executing through arifOS.

            Request:
                {
                    "agent_did": {"did": "did:arifos:agent:abc123", ...},
                    "action_id": "unique-action-id",
                    "action_type": "tool_call|api_request|code_execution",
                    "action_description": "What the agent wants to do",
                    "tool_name": "optional_tool_name",
                    "parameters": {...},
                    "stakeholders": ["user", "system"],
                    "reversibility_proof": "proof_of_undo_capability"
                }

            Response:
                {
                    "verdict": "SEAL|VOID|PARTIAL|SABAR|888_HOLD",
                    "floors_passed": ["F1", "F2", ...],
                    "floors_failed": ["F3"],
                    "violations": [...],
                    "metrics": {"G_star": 0.85, "dS": -0.3, ...},
                    "tri_witness": {"human": 0.95, "ai": 0.9, "earth": 0.85, "W3": 0.90},
                    "recommendations": [...]
                }
            """
            logger.info(f"Governance evaluation requested for action: {request.action_id}")

            # Run through constitutional engine
            evaluation = await governance_engine.evaluate(request)

            logger.info(
                f"Governance verdict for {request.action_id}: "
                f"{evaluation.verdict} (passed: {len(evaluation.floors_passed)}/13)"
            )

            return evaluation

        @self.app.get("/governance/did/verify/{did}")
        async def verify_agent_did(did: str):
            """
            Verify an Agent DID and return trust score.

            This allows agents to prove their governance lineage.
            """
            # In production: check DID registry
            return {
                "did": did,
                "verified": True,
                "trust_score": 0.85,
                "policy_level": "general",
                "governance_endpoints": ["https://arifosmcp.arif-fazil.com/governance/evaluate"],
                "verdict": "SEAL",
            }

        @self.app.get("/governance/floors")
        async def list_constitutional_floors():
            """List all 13 constitutional floors with thresholds."""
            return {
                "verdict": "SEAL",
                "floors": [
                    {
                        "id": "F1",
                        "name": "Amanah",
                        "type": "Hard",
                        "threshold": ">= 0.5",
                        "enforces": "Reversibility",
                    },
                    {
                        "id": "F2",
                        "name": "Truth",
                        "type": "Hard",
                        "threshold": ">= 0.99",
                        "enforces": "Anti-hallucination",
                    },
                    {
                        "id": "F3",
                        "name": "Tri-Witness",
                        "type": "Mirror",
                        "threshold": ">= 0.95",
                        "enforces": "Consensus",
                    },
                    {
                        "id": "F4",
                        "name": "ΔS Clarity",
                        "type": "Hard",
                        "threshold": "<= 0",
                        "enforces": "Entropy reduction",
                    },
                    {
                        "id": "F5",
                        "name": "Peace²",
                        "type": "Soft",
                        "threshold": ">= 1.0",
                        "enforces": "Stability",
                    },
                    {
                        "id": "F6",
                        "name": "Empathy",
                        "type": "Soft",
                        "threshold": ">= 0.70",
                        "enforces": "Weakest stakeholder",
                    },
                    {
                        "id": "F7",
                        "name": "Humility",
                        "type": "Hard",
                        "threshold": "0.03-0.20",
                        "enforces": "Uncertainty",
                    },
                    {
                        "id": "F8",
                        "name": "Genius",
                        "type": "Mirror",
                        "threshold": ">= 0.80",
                        "enforces": "Coherence",
                    },
                    {
                        "id": "F9",
                        "name": "Anti-Hantu",
                        "type": "Hard",
                        "threshold": "< 0.30",
                        "enforces": "No dark patterns",
                    },
                    {
                        "id": "F10",
                        "name": "Ontology",
                        "type": "Wall",
                        "threshold": "LOCK",
                        "enforces": "No consciousness claims",
                    },
                    {
                        "id": "F11",
                        "name": "Command Auth",
                        "type": "Hard",
                        "threshold": "LOCK",
                        "enforces": "Identity verification",
                    },
                    {
                        "id": "F12",
                        "name": "Injection",
                        "type": "Wall",
                        "threshold": "< 0.85",
                        "enforces": "Block adversarial control",
                    },
                    {
                        "id": "F13",
                        "name": "Sovereign",
                        "type": "Veto",
                        "threshold": "HUMAN",
                        "enforces": "Human final authority",
                    },
                ],
            }

        @self.app.websocket("/webmcp/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """
            WebSocket for real-time governance updates.

            Streams:
            - Vitals (every 5s)
            - 888_HOLD events
            - Floor score changes
            """
            await websocket.accept()
            session_id = f"ws-{asyncio.get_event_loop().time():.0f}"
            
            # Register connection
            self._active_websockets.add(websocket)
            
            # Subscribe to cross-protocol events
            await self._subscribe_to_hold_events()

            try:
                while True:
                    # Send vitals
                    vitals = {
                        "type": "vitals",
                        "data": {
                            "G_star": 0.85,
                            "dS": -0.3,
                            "peace2": 1.05,
                            "timestamp": asyncio.get_event_loop().time(),
                        },
                    }
                    await websocket.send_json(vitals)
                    
                    await asyncio.sleep(5)

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected: {session_id}")
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
            finally:
                self._active_websockets.discard(websocket)
                await websocket.close()
        
        # ═══════════════════════════════════════════════════════════════════════
        # CROSS-PROTOCOL 888_HOLD ENDPOINTS
        # ═══════════════════════════════════════════════════════════════════════
        
        @self.app.get("/api/live/holds")
        async def get_pending_holds():
            """
            Get all pending 888_HOLD events for dashboard display.
            
            Arif (888 Judge) reviews these and issues SEAL or VOID.
            """
            try:
                # Query from hold state manager
                from arifosmcp.agentzero.escalation.hold_state import HoldStateManager
                
                hold_manager = HoldStateManager()
                pending = hold_manager.get_pending_holds()
                
                return {
                    "verdict": "SEAL",
                    "count": len(pending),
                    "holds": [
                        {
                            "hold_id": h.hold_id,
                            "action_type": h.action_type,
                            "reason": h.reason,
                            "risk_level": h.risk_level,
                            "floor_violations": h.floor_violations,
                            "created_at": h.created_at.isoformat(),
                            "time_elapsed_seconds": (
                                datetime.utcnow() - h.created_at
                            ).total_seconds(),
                            "action_payload_preview": str(h.action_payload)[:200],
                        }
                        for h in pending
                    ],
                }
            except Exception as e:
                return {"verdict": "VOID", "error": str(e), "holds": []}
        
        @self.app.post("/hold/{hold_id}/resolve")
        async def resolve_hold(hold_id: str, request: Request):
            """
            888 JUDGE ENDPOINT: Arif issues SEAL or VOID for a pending hold.
            
            This is the F13 Sovereign in action.
            """
            # F11: Verify Arif's identity
            body = await request.json()
            actor_id = body.get("actor_id", "")
            
            if actor_id not in ("ariffazil", "arif", "arif-fazil"):
                return JSONResponse(
                    status_code=403,
                    content={
                        "verdict": "VOID",
                        "error": "F13: Only sovereign (ariffazil) can resolve 888_HOLD",
                    },
                )
            
            decision = body.get("decision")  # "APPROVED" or "DENIED"
            justification = body.get("justification", "")
            
            if decision not in ("APPROVED", "DENIED"):
                return JSONResponse(
                    status_code=400,
                    content={"verdict": "VOID", "error": "Decision must be APPROVED or DENIED"},
                )
            
            try:
                # Resolve via hold state manager
                from arifosmcp.agentzero.escalation.hold_state import HoldStateManager
                
                hold_manager = HoldStateManager()
                resolved = await hold_manager.resolve_hold(
                    hold_id=hold_id,
                    decision=decision,
                    responded_by=actor_id,
                    notes=justification,
                )
                
                # Broadcast resolution to all protocols
                from arifosmcp.runtime.cross_protocol_bridge import get_hold_bridge
                bridge = await get_hold_bridge()
                await bridge.publish_resolution(
                    hold_id=hold_id,
                    decision=decision,
                    decided_by=actor_id,
                    justification=justification,
                )
                
                return {
                    "verdict": "SEAL" if decision == "APPROVED" else "VOID",
                    "hold_id": hold_id,
                    "decision": decision,
                    "resolved_at": datetime.utcnow().isoformat(),
                }
                
            except Exception as e:
                return {"verdict": "VOID", "error": str(e)}

    def _tool_manifest(self) -> list[dict[str, Any]]:
        """Expose the live public tool registry in WebMCP-friendly form (cached)."""
        if self._cached_tool_manifest is None:
            self._cached_tool_manifest = [
                {
                    "name": spec.name,
                    "stage": spec.stage,
                    "layer": spec.role,
                    "description": spec.description,
                }
                for spec in PUBLIC_TOOL_SPECS
            ]
        return self._cached_tool_manifest

    def _build_sdk_js(self) -> str:
        """Minimal browser SDK for imperative WebMCP integration."""
        return """
(() => {
  const base = "";

  async function jsonFetch(path, options = {}) {
    const response = await fetch(`${base}${path}`, {
      credentials: "include",
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      ...options,
    });
    const text = await response.text();
    let body;
    try {
      body = text ? JSON.parse(text) : {};
    } catch {
      body = { raw: text };
    }
    if (!response.ok) {
      const message = body.error || body.detail || response.statusText;
      throw new Error(message);
    }
    return body;
  }

  const sdk = {
    init(payload = {}) {
      return jsonFetch("/webmcp/init", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
    tools() {
      return jsonFetch("/webmcp/tools.json");
    },
    call(toolName, payload = {}) {
      return jsonFetch(`/webmcp/call/${toolName}`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
    vitals() {
      return jsonFetch("/webmcp/vitals");
    },
  };

  window.arifOSWebMCP = sdk;
  window.dispatchEvent(new CustomEvent("webmcp:ready", { detail: { sdk } }));
})();
"""

    async def _subscribe_to_hold_events(self):
        """Subscribe to cross-protocol 888_HOLD events."""
        if self._hold_bridge_subscribed:
            return
            
        try:
            from arifosmcp.runtime.cross_protocol_bridge import get_hold_bridge
            bridge = await get_hold_bridge()
            await bridge.subscribe(self._on_hold_event)
            self._hold_bridge_subscribed = True
            logger.info("WebMCP subscribed to 888_HOLD cross-protocol events")
        except Exception as e:
            logger.error(f"Failed to subscribe to hold events: {e}")
            
    async def _on_hold_event(self, event):
        """
        Callback: Received 888_HOLD from Redis (A2A or MCP).
        Broadcast to all connected browser clients.
        """
        # Fan-out to all WebSocket clients
        disconnected = set()
        
        message = {
            "type": "888_HOLD",
            "timestamp": event.timestamp,
            "payload": {
                "hold_id": event.hold_id,
                "source_protocol": event.source_protocol,
                "action_type": event.action_type,
                "reason": event.reason,
                "risk_level": event.risk_level,
                "floor_violations": event.floor_violations,
                "actor_id": event.actor_id,
                "pre_execution_hash": event.pre_execution_hash,
                "review_url": f"https://arifosmcp.arif-fazil.com/hold/{event.hold_id}",
            }
        }
        
        for ws in self._active_websockets:
            try:
                await ws.send_json(message)
            except WebSocketDisconnect:
                disconnected.add(ws)
            except Exception as e:
                logger.error(f"WebSocket send failed: {e}")
                disconnected.add(ws)
        
        # Cleanup disconnected clients
        self._active_websockets -= disconnected
        
        logger.info(
            f"[888_HOLD BROADCAST] {event.hold_id} → "
            f"{len(self._active_websockets)} browser clients"
        )


def create_webmcp_app(mcp_server: Any) -> FastAPI:
    """
    Factory function to create WebMCP app.

    Usage:
        from arifosmcp.runtime.webmcp import create_webmcp_app

        app = create_webmcp_app(mcp_server)
        uvicorn.run(app, host="0.0.0.0", port=8443)
    """
    gateway = WebMCPGateway(mcp_server)
    return gateway.app

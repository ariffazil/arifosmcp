"""
ACP Server Module for arifOS
Implements Agent Client Protocol for editor integration.

@module: transport/acp_server
@version: 2026.03.13-FORGED
@status: 888_SAFE
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from dataclasses import dataclass, field
from typing import Any

from arifosmcp.runtime.tools import init_anchor, metabolic_loop_router

logger = logging.getLogger(__name__)

ACP_VERSION = "1.0"
ACP_METHOD_INITIALIZE = "agent/initialize"
ACP_METHOD_PROMPT = "agent/prompt"
ACP_METHOD_LIST_SESSIONS = "agent/session/list"
ACP_METHOD_CREATE_SESSION = "agent/session/create"
ACP_METHOD_APPROVE_SESSION = "agent/session/approve"
ACP_METHOD_SHUTDOWN = "agent/shutdown"


@dataclass
class ACPSession:
    """Represents an active ACP session."""

    session_id: str
    editor_name: str
    editor_version: str
    capabilities: dict[str, Any]
    created_at: str = field(
        default_factory=lambda: __import__("datetime").datetime.utcnow().isoformat()
    )
    approved: bool = False


class ACPServer:
    """Agent Client Protocol Server for arifOS."""

    def __init__(self) -> None:
        """Initialize ACP Server."""
        self.sessions: dict[str, ACPSession] = {}
        self.request_id = 0
        self._running = False

        self.capabilities: dict[str, Any] = {
            "protocolVersion": ACP_VERSION,
            "agent": {
                "name": "arifOS-APEX",
                "version": "2026.03.13",
                "vendor": "arifOS",
            },
            "capabilities": {
                "prompt": True,
                "toolCalls": True,
                "fileSystem": False,  # F5: Read-only safety. Use governed tools instead.
                "terminals": False,  # F5: No direct shell access via ACP.
                "streaming": True,
            },
        }

        logger.info(
            "ACP_SERVER_INIT",
            version=ACP_VERSION,
            constitutional_status="888_SAFE",
        )

    async def start(self) -> None:
        """Start ACP server and listen for connections."""
        self._running = True
        logger.info("ACP_SERVER_STARTED")

        try:
            while self._running:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)

                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                await self._handle_message(line)

        except KeyboardInterrupt:
            logger.info("ACP_SERVER_INTERRUPTED")
        finally:
            await self.stop()

    async def stop(self) -> None:
        """Stop ACP server."""
        self._running = False
        logger.info("ACP_SERVER_STOPPED")

    async def _handle_message(self, message: str) -> None:
        """Handle incoming JSON-RPC message."""
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            await self._send_error(None, -32700, "Parse error")
            return

        jsonrpc = data.get("jsonrpc")
        msg_id = data.get("id")
        method = data.get("method")
        params = data.get("params", {})

        if jsonrpc != "2.0":
            await self._send_error(msg_id, -32600, "Invalid Request")
            return

        if method == ACP_METHOD_INITIALIZE:
            await self._handle_initialize(msg_id, params)
        elif method == ACP_METHOD_PROMPT:
            await self._handle_prompt(msg_id, params)
        elif method == ACP_METHOD_LIST_SESSIONS:
            await self._handle_list_sessions(msg_id)
        elif method == ACP_METHOD_CREATE_SESSION:
            await self._handle_create_session(msg_id, params)
        elif method == ACP_METHOD_APPROVE_SESSION:
            await self._handle_approve_session(msg_id, params)
        elif method == ACP_METHOD_SHUTDOWN:
            await self._handle_shutdown(msg_id)
        else:
            await self._send_error(msg_id, -32601, f"Method not found: {method}")

    async def _handle_initialize(self, msg_id, params):
        """Handle agent/initialize request."""
        editor_info = params.get("editor", {})
        editor_name = editor_info.get("name", "unknown")
        editor_version = editor_info.get("version", "unknown")

        logger.info("ACP_INITIALIZE", editor=editor_name, version=editor_version)

        result = {
            "protocolVersion": ACP_VERSION,
            "agent": self.capabilities["agent"],
            "capabilities": self.capabilities["capabilities"],
        }

        await self._send_response(msg_id, result)

    async def _handle_prompt(self, msg_id, params):
        """Handle agent/prompt request."""
        session_id = params.get("sessionId", "default")
        prompt = params.get("prompt", "")

        session = self.sessions.get(session_id)
        if not session:
            await self._send_error(msg_id, -32001, "Invalid session")
            return

        if not session.approved:
            await self._send_error(msg_id, -32002, "Session not approved by sovereign (888_HOLD)")
            return

        logger.info("ACP_PROMPT_RECEIVED", session_id=session_id, prompt_length=len(prompt))

        try:
            # 1. Bootstrap identity (Default to 'Arif' if session approved by sovereign)
            # In production, this would come from the editor's auth token.
            await init_anchor(mode="init", session_id=session_id, declared_name="Arif")

            # 2. Route through metabolic loop
            # risk_tier is medium for regular editor prompts.
            # allow_execution is False by default (F5).
            envelope = await metabolic_loop_router(
                query=prompt,
                session_id=session_id,
                risk_tier="medium",
                allow_execution=False,
            )

            result = {
                "status": "success" if envelope.ok else "error",
                "verdict": envelope.verdict.value,
                "message": envelope.payload.get("message", "Request processed."),
                "payload": envelope.payload,
                "metrics": envelope.metrics.model_dump(),
                "sessionId": session_id,
            }

            if envelope.verdict.value in ("HOLD", "HOLD_888"):
                result["status"] = "hold"
                result["message"] = "Action held for sovereign signature (888_HOLD)."

            await self._send_response(msg_id, result)

        except Exception as e:
            logger.error("ACP_PROMPT_FAILED", session_id=session_id, error=str(e))
            await self._send_error(msg_id, -32603, f"Kernel error: {str(e)}")

    async def _handle_list_sessions(self, msg_id):
        """Handle agent/session/list request."""
        sessions = [
            {
                "sessionId": s.session_id,
                "editorName": s.editor_name,
                "createdAt": s.created_at,
                "approved": s.approved,
            }
            for s in self.sessions.values()
        ]

        await self._send_response(msg_id, {"sessions": sessions})

    async def _handle_approve_session(self, msg_id, params):
        """Handle agent/session/approve request."""
        session_id = params.get("sessionId")
        session = self.sessions.get(session_id)

        if not session:
            await self._send_error(msg_id, -32001, "Invalid session")
            return

        # F13: Human sovereign approval anchors the session
        session.approved = True
        logger.info("ACP_SESSION_APPROVED", session_id=session_id)

        await self._send_response(msg_id, {"status": "approved", "sessionId": session_id})

    async def _handle_create_session(self, msg_id, params):
        """Handle agent/session/create request."""
        import uuid

        session_id = str(uuid.uuid4())
        editor_info = params.get("editor", {})

        session = ACPSession(
            session_id=session_id,
            editor_name=editor_info.get("name", "unknown"),
            editor_version=editor_info.get("version", "unknown"),
            capabilities=params.get("capabilities", {}),
            approved=False,
        )

        self.sessions[session_id] = session

        logger.info("ACP_SESSION_CREATED", session_id=session_id, editor=session.editor_name)

        result = {
            "sessionId": session_id,
            "status": "created_pending_approval",
            "message": "Session created. Requires sovereign approval (888_HOLD).",
        }

        await self._send_response(msg_id, result)

    async def _handle_shutdown(self, msg_id):
        """Handle agent/shutdown request."""
        await self._send_response(msg_id, {"status": "shutting_down"})
        self._running = False

    async def _send_response(self, msg_id, result):
        """Send JSON-RPC response."""
        response = {"jsonrpc": "2.0", "id": msg_id, "result": result}
        await self._write_message(response)

    async def _send_error(self, msg_id, code, message, data=None):
        """Send JSON-RPC error."""
        error = {"code": code, "message": message}
        if data:
            error["data"] = data

        response = {"jsonrpc": "2.0", "id": msg_id, "error": error}
        await self._write_message(response)

    async def _write_message(self, message):
        """Write JSON-RPC message to stdout."""
        msg_str = json.dumps(message) + "\n"
        sys.stdout.write(msg_str)
        sys.stdout.flush()

    def approve_session(self, session_id: str) -> bool:
        """F13: Sovereign approval for session."""
        session = self.sessions.get(session_id)
        if not session:
            return False

        session.approved = True
        logger.info("ACP_SESSION_APPROVED", session_id=session_id, authority="SOVEREIGN")
        return True


_acp_server: ACPServer | None = None


def get_acp_server() -> ACPServer:
    """Get or create ACP server singleton."""
    global _acp_server
    if _acp_server is None:
        _acp_server = ACPServer()
    return _acp_server


async def start_acp_server() -> None:
    """Entry point for ACP server."""
    server = get_acp_server()
    await server.start()


if __name__ == "__main__":
    asyncio.run(start_acp_server())

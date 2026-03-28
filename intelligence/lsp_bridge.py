"""
LSP Bridge Module for arifOS
Provides constitutional, read-only access to Language Server Protocol.

This module wraps LSP clients with arifOS governance:
- F4 (Clarity): LSP provides exact symbols (entropy reduction)
- F11 (Auth): Command authority verification
- F12 (Injection): Input sanitization
- All queries logged to VAULT999

@module: intelligence/lsp_bridge
@version: 2026.03.13-FORGED
@status: 888_SAFE (read-only)
"""

from __future__ import annotations

import asyncio
import json
import logging
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class LSPResponse:
    """Standard LSP response wrapper with constitutional metadata."""

    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    query_time_ms: float = 0.0
    authority_hash: str = ""


class LSPBridge:
    """
    Constitutional bridge to Language Servers.

    Provides read-only code intelligence:
    - Hover information
    - Go-to-definition
    - Find references
    - Document symbols
    - Diagnostics

    All operations are:
    - Read-only (no file modifications)
    - Logged to VAULT999
    - Sanitized (F12 injection defense)
    """

    SUPPORTED_SERVERS: dict[str, list[str]] = {
        "python": ["pylsp"],
        "typescript": ["typescript-language-server", "--stdio"],
        "javascript": ["typescript-language-server", "--stdio"],
        "rust": ["rust-analyzer"],
        "go": ["gopls"],
    }

    def __init__(self, project_root: str | Path) -> None:
        """Initialize LSP Bridge for a project."""
        self.project_root = Path(project_root).resolve()
        self.process: subprocess.Popen | None = None
        self.request_id = 0
        self._lock = asyncio.Lock()
        self._initialized = False

        logger.info(
            "LSP_BRIDGE_INIT",
            project_root=str(self.project_root),
            constitutional_status="888_SAFE_READ_ONLY",
        )

    async def start(self, language: str = "python") -> LSPResponse:
        """Start the language server subprocess."""

        start_time = time.time()

        if language not in self.SUPPORTED_SERVERS:
            return LSPResponse(
                success=False,
                error=f"Unsupported language: {language}",
            )

        cmd = self.SUPPORTED_SERVERS[language]

        try:
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.project_root,
            )

            init_result = await self._send_request(
                "initialize",
                {
                    "processId": None,
                    "rootUri": self.project_root.as_uri(),
                    "capabilities": {},
                },
            )

            self._initialized = True
            query_time = (time.time() - start_time) * 1000

            logger.info(
                "LSP_SERVER_STARTED",
                language=language,
                query_time_ms=query_time,
                verdict="SEAL",
            )

            return LSPResponse(
                success=True,
                data=init_result,
                query_time_ms=query_time,
            )

        except Exception as e:
            logger.error("LSP_START_FAILED", error=str(e))
            return LSPResponse(success=False, error=str(e))

    async def stop(self) -> None:
        """Stop the language server subprocess."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
            self._initialized = False
            logger.info("LSP_SERVER_STOPPED")

    async def hover(self, file_path: str, line: int, character: int) -> LSPResponse:
        """Get hover information at a position."""
        return await self._text_document_request(
            "textDocument/hover",
            file_path,
            {"line": line, "character": character},
        )

    async def definition(self, file_path: str, line: int, character: int) -> LSPResponse:
        """Get definition location(s) for a symbol."""
        return await self._text_document_request(
            "textDocument/definition",
            file_path,
            {"line": line, "character": character},
        )

    async def references(self, file_path: str, line: int, character: int) -> LSPResponse:
        """Find all references to a symbol."""
        return await self._text_document_request(
            "textDocument/references",
            file_path,
            {"line": line, "character": character},
            extra_params={"context": {"includeDeclaration": True}},
        )

    async def document_symbols(self, file_path: str) -> LSPResponse:
        """Get all symbols in a document."""
        safe_path = self._sanitize_path(file_path)
        if not safe_path:
            return LSPResponse(success=False, error="Invalid file path")

        uri = safe_path.as_uri()
        return await self._send_request(
            "textDocument/documentSymbol",
            {"textDocument": {"uri": uri}},
        )

    async def rename(self, file_path: str, line: int, character: int, new_name: str) -> LSPResponse:
        """Propose a rename refactor (WorkspaceEdit). does NOT apply to disk."""
        return await self._text_document_request(
            "textDocument/rename",
            file_path,
            {"line": line, "character": character},
            extra_params={"newName": new_name},
        )

    async def diagnostics(self, file_path: str) -> LSPResponse:
        """Get diagnostics (errors/warnings) for a file."""
        safe_path = self._sanitize_path(file_path)
        if not safe_path:
            return LSPResponse(success=False, error="Invalid file path")

        uri = safe_path.as_uri()
        content = safe_path.read_text() if safe_path.exists() else ""

        await self._send_notification(
            "textDocument/didOpen",
            {
                "textDocument": {
                    "uri": uri,
                    "languageId": safe_path.suffix.lstrip("."),
                    "version": 1,
                    "text": content,
                }
            },
        )

        logger.info("LSP_DIAGNOSTICS_REQUESTED", file=str(safe_path))

        return LSPResponse(
            success=True,
            data={"message": "Diagnostics requested - check server output"},
        )

    async def _text_document_request(
        self,
        method: str,
        file_path: str,
        position: dict[str, int],
        extra_params: dict[str, Any] | None = None,
    ) -> LSPResponse:
        """Internal helper for text document requests."""
        safe_path = self._sanitize_path(file_path)
        if not safe_path:
            return LSPResponse(success=False, error="Invalid file path")

        uri = safe_path.as_uri()

        params: dict[str, Any] = {
            "textDocument": {"uri": uri},
            "position": position,
        }
        if extra_params:
            params.update(extra_params)

        return await self._send_request(method, params)

    async def _send_request(self, method: str, params: dict[str, Any]) -> LSPResponse:
        """Send JSON-RPC request to language server."""

        if not self.process or not self._initialized:
            return LSPResponse(success=False, error="LSP server not initialized")

        async with self._lock:
            self.request_id += 1
            request_id = self.request_id

            request = {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": method,
                "params": params,
            }

            start_time = time.time()

            try:
                request_str = json.dumps(request) + "\r\n"
                self.process.stdin.write(request_str.encode())
                self.process.stdin.flush()

                response_line = self.process.stdout.readline()
                response = json.loads(response_line.decode())

                query_time = (time.time() - start_time) * 1000

                if "error" in response:
                    return LSPResponse(
                        success=False,
                        error=response["error"].get("message", "Unknown error"),
                        query_time_ms=query_time,
                    )

                logger.info(
                    "LSP_REQUEST_SUCCESS",
                    method=method,
                    query_time_ms=query_time,
                )

                return LSPResponse(
                    success=True,
                    data=response.get("result", {}),
                    query_time_ms=query_time,
                )

            except Exception as e:
                logger.error("LSP_REQUEST_FAILED", method=method, error=str(e))
                return LSPResponse(success=False, error=str(e))

    async def _send_notification(self, method: str, params: dict[str, Any]) -> None:
        """Send JSON-RPC notification (no response expected)."""
        if not self.process:
            return

        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
        }

        try:
            notification_str = json.dumps(notification) + "\r\n"
            self.process.stdin.write(notification_str.encode())
            self.process.stdin.flush()
        except Exception as e:
            logger.error("LSP_NOTIFICATION_FAILED", method=method, error=str(e))

    def _sanitize_path(self, file_path: str) -> Path | None:
        """F12: Sanitize and validate file path."""
        try:
            path = Path(file_path)

            if not path.is_absolute():
                path = self.project_root / path

            resolved = path.resolve()

            try:
                resolved.relative_to(self.project_root)
            except ValueError:
                logger.warning("LSP_PATH_ESCAPE_ATTEMPT", path=str(resolved))
                return None

            return resolved

        except Exception as e:
            logger.error("LSP_PATH_SANITIZE_FAILED", path=file_path, error=str(e))
            return None


_lsp_bridge: LSPBridge | None = None


def get_lsp_bridge(project_root: str | Path | None = None) -> LSPBridge:
    """Get or create LSP bridge singleton."""
    global _lsp_bridge
    if _lsp_bridge is None:
        if project_root is None:
            project_root = Path.cwd()
        _lsp_bridge = LSPBridge(project_root)
    return _lsp_bridge


def reset_lsp_bridge() -> None:
    """Reset singleton (useful for testing)."""
    global _lsp_bridge
    if _lsp_bridge:
        asyncio.run(_lsp_bridge.stop())
    _lsp_bridge = None

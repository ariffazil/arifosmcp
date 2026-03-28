"""
LSP Tools for arifOS MCP
Exposes Language Server Protocol via MCP tools.

@module: tools/lsp_tools
@version: 2026.03.13-FORGED
@status: 888_SAFE
"""

from __future__ import annotations

import logging
from typing import Any

from arifosmcp.intelligence.lsp_bridge import get_lsp_bridge
from arifosmcp.runtime.models import (
    AuthorityLevel,
    CanonicalAuthority,
    CanonicalError,
    CanonicalMeta,
    CanonicalMetrics,
    RuntimeEnvelope,
    RuntimeStatus,
    Stage,
    Verdict,
)

try:
    from fastmcp import FastMCP

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

logger = logging.getLogger(__name__)


async def lsp_query(
    file_path: str,
    query_type: str,
    line: int = 0,
    character: int = 0,
) -> RuntimeEnvelope | dict[str, Any]:
    """Query Language Server for code intelligence."""
    logger.info("LSP_TOOL_CALLED", tool="lsp_query", file=file_path, query_type=query_type)

    bridge = get_lsp_bridge()

    if not bridge._initialized:
        init_result = await bridge.start("python")
        if not init_result.success:
            return _make_error_response(f"Failed to start LSP: {init_result.error}")

    if query_type == "hover":
        result = await bridge.hover(file_path, line, character)
    elif query_type == "definition":
        result = await bridge.definition(file_path, line, character)
    elif query_type == "references":
        result = await bridge.references(file_path, line, character)
    elif query_type == "symbols":
        result = await bridge.document_symbols(file_path)
    elif query_type == "diagnostics":
        result = await bridge.diagnostics(file_path)
    else:
        return _make_error_response(f"Unknown query_type: {query_type}")

    return _make_success_response("lsp_query", result)


async def lsp_get_symbols(file_path: str) -> RuntimeEnvelope | dict[str, Any]:
    """Get all symbols in a file."""
    logger.info("LSP_TOOL_CALLED", tool="lsp_get_symbols", file=file_path)

    bridge = get_lsp_bridge()

    if not bridge._initialized:
        init_result = await bridge.start("python")
        if not init_result.success:
            return _make_error_response(f"Failed to start LSP: {init_result.error}")

    result = await bridge.document_symbols(file_path)
    return _make_success_response("lsp_get_symbols", result)


async def lsp_get_diagnostics(file_path: str) -> RuntimeEnvelope | dict[str, Any]:
    """Get errors and warnings for a file."""
    logger.info("LSP_TOOL_CALLED", tool="lsp_get_diagnostics", file=file_path)

    bridge = get_lsp_bridge()

    if not bridge._initialized:
        init_result = await bridge.start("python")
        if not init_result.success:
            return _make_error_response(f"Failed to start LSP: {init_result.error}")

    result = await bridge.diagnostics(file_path)
    return _make_success_response("lsp_get_diagnostics", result)


async def lsp_go_to_definition(
    file_path: str, line: int, character: int
) -> RuntimeEnvelope | dict[str, Any]:
    """Find where a symbol is defined."""
    logger.info("LSP_TOOL_CALLED", tool="lsp_go_to_definition", file=file_path)

    bridge = get_lsp_bridge()

    if not bridge._initialized:
        init_result = await bridge.start("python")
        if not init_result.success:
            return _make_error_response(f"Failed to start LSP: {init_result.error}")

    result = await bridge.definition(file_path, line, character)
    return _make_success_response("lsp_go_to_definition", result)


async def lsp_find_references(
    file_path: str, line: int, character: int
) -> RuntimeEnvelope | dict[str, Any]:
    """Find all references to a symbol."""
    logger.info("LSP_TOOL_CALLED", tool="lsp_find_references", file=file_path)

    bridge = get_lsp_bridge()

    if not bridge._initialized:
        init_result = await bridge.start("python")
        if not init_result.success:
            return _make_error_response(f"Failed to start LSP: {init_result.error}")

    result = await bridge.references(file_path, line, character)
    return _make_success_response("lsp_find_references", result)


async def lsp_rename(
    file_path: str, line: int, character: int, new_name: str
) -> RuntimeEnvelope | dict[str, Any]:
    """Propose a rename refactor. Returns a WorkspaceEdit (888_HOLD required)."""
    logger.info("LSP_TOOL_CALLED", tool="lsp_rename", file=file_path, new_name=new_name)

    bridge = get_lsp_bridge()

    if not bridge._initialized:
        init_result = await bridge.start("python")
        if not init_result.success:
            return _make_error_response(f"Failed to start LSP: {init_result.error}")

    result = await bridge.rename(file_path, line, character, new_name)

    # Refactors MUST triggered 888_HOLD even if they are just proposals.
    envelope = _make_success_response("lsp_rename", result)
    envelope.verdict = Verdict.HOLD_888
    return envelope


def _make_success_response(tool_name: str, lsp_result: Any) -> RuntimeEnvelope:
    """Create standard RuntimeEnvelope for successful response."""
    data = lsp_result.data if hasattr(lsp_result, "data") else lsp_result

    return RuntimeEnvelope(
        ok=True,
        tool=tool_name,
        stage=Stage.SENSE_111,
        verdict=Verdict.SEAL,
        status=RuntimeStatus.SUCCESS,
        metrics=CanonicalMetrics(
            truth=1.0,  # LSP results are ground truth for code semantics
            clarity_delta=0.5,
        ),
        authority=CanonicalAuthority(
            actor_id="system",
            level=AuthorityLevel.SYSTEM,
        ),
        payload=data if isinstance(data, dict) else {"result": data},
        meta=CanonicalMeta(
            motto="DitemPA BUKAN DIBERI",
        ),
    )


def _make_error_response(error_message: str) -> RuntimeEnvelope:
    """Create standard RuntimeEnvelope for error response."""
    return RuntimeEnvelope(
        ok=False,
        tool="lsp_bridge",
        stage=Stage.SENSE_111,
        verdict=Verdict.VOID,
        status=RuntimeStatus.ERROR,
        errors=[CanonicalError(code="LSP_ERROR", message=error_message)],
    )


def register_lsp_tools(mcp: FastMCP) -> None:
    """Register all LSP tools with FastMCP server."""
    if not MCP_AVAILABLE:
        logger.warning("FastMCP not available - LSP tools not registered")
        return

    @mcp.tool()
    async def lsp_query_tool(
        file_path: str, query_type: str, line: int = 0, character: int = 0
    ) -> dict[str, Any]:
        return await lsp_query(file_path, query_type, line, character)

    @mcp.tool()
    async def lsp_get_symbols_tool(file_path: str) -> dict[str, Any]:
        return await lsp_get_symbols(file_path)

    @mcp.tool()
    async def lsp_get_diagnostics_tool(file_path: str) -> dict[str, Any]:
        return await lsp_get_diagnostics(file_path)

    @mcp.tool()
    async def lsp_go_to_definition_tool(
        file_path: str, line: int, character: int
    ) -> dict[str, Any]:
        return await lsp_go_to_definition(file_path, line, character)

    @mcp.tool()
    async def lsp_find_references_tool(file_path: str, line: int, character: int) -> dict[str, Any]:
        return await lsp_find_references(file_path, line, character)

    @mcp.tool()
    async def lsp_rename_tool(
        file_path: str, line: int, character: int, new_name: str
    ) -> dict[str, Any]:
        """Propose a rename refactor (888_HOLD required)."""
        return await lsp_rename(file_path, line, character, new_name)

    logger.info("LSP_TOOLS_REGISTERED", count=6)

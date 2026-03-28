"""
arifOS ChatGPT MCP Integration — ΔΩΨ | DITEMPA BUKAN DIBERI

This module provides ChatGPT-compatible tools for OpenAI's MCP integration:
- Deep Research: search + fetch tools
- Chat Mode: All 11 mega-tools with readOnlyHint annotations

Official Docs:
- https://developers.openai.com/api/docs/mcp
- https://gofastmcp.com/integrations/chatgpt
"""

from .chatgpt_tools import search, fetch, chatgpt_tools, register_chatgpt_tools

__all__ = ["search", "fetch", "chatgpt_tools", "register_chatgpt_tools"]

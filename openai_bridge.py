"""
arifOS OpenAI Bridge — ChatGPT Company Knowledge MCP Schema

Thin wrapper exposing arifOS search/fetch via OpenAI MCP content array format.
Each tool returns list[dict] with {type, text} where text is JSON-encoded payload.

OpenAI schema: https://developers.openai.com/docs/mcp
Bridge:        https://gofastmcp.com
"""

from __future__ import annotations

import json
import os
from typing import Any

__all__ = []  # Empty unless bridge is enabled

if os.getenv("ARIFOS_OPENAI_BRIDGE", "0") != "1":
    __doc__ = None
else:
    from .runtime.reality_handlers import RealityHandler
    from .runtime.reality_models import BundleInput

    _handler = RealityHandler()

    _ANON = {
        "actor_id": "openai-bridge",
        "authority_level": "user",
        "token_fingerprint": None,
    }

    async def search(query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        OpenAI MCP search — returns content array with JSON {results: [{id, title, url}]}

        Arity: query=str
        OpenAI schema: content[].text = json.dumps({results: [{id, title, url}]})
        """
        inp = BundleInput(type="query", value=query, top_k=top_k, fetch_top_k=0)
        bundle = await _handler.handle_compass(inp, _ANON)

        results = []
        for r in bundle.results:
            if hasattr(r, "results") and r.results:  # SearchResult
                for item in r.results:
                    uid = item.get("href", item.get("url", query))[:32]
                    results.append({
                        "id": uid,
                        "title": item.get("title", "Untitled"),
                        "url": item.get("href", item.get("url", "")),
                    })

        return [{"type": "text", "text": json.dumps({"results": results})}]

    async def fetch(url: str, render: str = "auto") -> list[dict[str, Any]]:
        """
        OpenAI MCP fetch — returns content array with JSON {id, title, text, url, metadata}

        Arity: url=str
        OpenAI schema: content[].text = json.dumps({id, title, text, url, metadata})
        """
        inp = BundleInput(type="url", value=url, render=render)
        bundle = await _handler.handle_compass(inp, _ANON)

        content_text = ""
        for r in bundle.results:
            if hasattr(r, "raw_content") and r.raw_content:
                content_text = r.raw_content[:8000]
                break

        return [{
            "type": "text",
            "text": json.dumps({
                "id": url[:32],
                "title": url.split("/")[-1] or "Document",
                "text": content_text,
                "url": url,
                "metadata": {"source": "arifOS", "bridge": "openai-mcp"}
            })
        }]

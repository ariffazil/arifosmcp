from __future__ import annotations

import os
from typing import Any

from arifosmcp.intelligence.tools.envelope import unified_tool_output

DEFAULT_OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
REQUEST_TIMEOUT_SECONDS = 45.0


@unified_tool_output(tool_name="ollama_local_generate", stage="333_MIND")
async def ollama_local_generate(
    *,
    prompt: str,
    model: str = "qwen2.5:3b",
    system: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 512,
) -> dict[str, Any]:
    clean_prompt = prompt.strip()
    if not clean_prompt:
        return {
            "ok": False,
            "error": "Prompt is empty.",
            "verdict": "PARTIAL",
            "issue": "INPUT_VALIDATION",
        }

    options = {
        "temperature": max(0.0, min(float(temperature), 1.5)),
        "num_predict": max(1, min(int(max_tokens), 2048)),
    }

    payload: dict[str, Any] = {
        "model": model.strip() or "qwen2.5:3b",
        "prompt": clean_prompt,
        "stream": False,
        "options": options,
    }
    if system and system.strip():
        payload["system"] = system.strip()

    import httpx
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.post(f"{DEFAULT_OLLAMA_URL}/api/generate", json=payload)
            response.raise_for_status()
            body = response.json()
    except Exception as e:
        # P0 hardening: Fail CLOSED. No fabricated response — empty string forces
        # _1_agi.py to detect ok=False and surface SABAR rather than synthesise
        # from error text. Caller must check ok before using response.
        return {
            "ok": False,
            "verdict": "VOID",
            "status": "OLLAMA_UNREACHABLE",
            "model": payload["model"],
            "response": "",
            "error": f"Ollama unreachable: {type(e).__name__}",
            "done": False,
        }

    return {
        "ok": True,
        "verdict": "SEAL",
        "status": "SUCCESS",
        "model": body.get("model", payload["model"]),
        "response": body.get("response", ""),
        "done": bool(body.get("done", False)),
        "total_duration": body.get("total_duration"),
        "load_duration": body.get("load_duration"),
        "eval_count": body.get("eval_count"),
        "prompt_eval_count": body.get("prompt_eval_count"),
    }


__all__ = ["DEFAULT_OLLAMA_URL", "ollama_local_generate"]

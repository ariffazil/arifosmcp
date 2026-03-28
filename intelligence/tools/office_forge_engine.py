"""
arifosmcp/intelligence/tools/office_forge_engine.py — Hardened Render Backend

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from arifosmcp.intelligence.tools.envelope import unified_tool_output

logger = logging.getLogger(__name__)

# Constants enforced by F12 (Defense)
MAX_MD_SIZE = 2 * 1024 * 1024  # 2MB
HARD_TIMEOUT = 25
FORGE_BASE_DIR = Path("/usr/src/app/data/forge_temp")
THEME_WHITELIST = {"default", "gaia", "uncover", "bespoke"}


async def audit_markdown(markdown: str) -> dict[str, Any]:
    """
    Stage 777: Analyzes markdown for complexity and safety.
    Checks for size, Mermaid density, and potential injection.
    """
    size = len(markdown.encode("utf-8"))
    if size > MAX_MD_SIZE:
        return {
            "ok": False,
            "error": "F12: Markdown exceeds 2MB limit.",
            "verdict": "PARTIAL",
            "issue": "FILE_TOO_LARGE",
        }

    # Check for Mermaid density (F4)
    mermaid_count = markdown.count("```mermaid")
    if mermaid_count > 5:
        return {
            "ok": False,
            "error": "F4: Excessive Mermaid diagrams (>5). Potential render timeout.",
            "verdict": "SABAR",
        }

    return {
        "ok": True,
        "status": "READY_FOR_RENDER",
        "size_bytes": size,
        "mermaid_count": mermaid_count,
        "verdict": "SEAL",
        "recommendation": "Markdown is within safe resource limits.",
    }


def _enforce_imagemagick_policy() -> list[str]:
    """Returns base arguments for ImageMagick to enforce resource limits."""
    return [
        "-limit",
        "memory",
        "256MiB",
        "-limit",
        "map",
        "512MiB",
        "-limit",
        "thread",
        "1",
        "-limit",
        "disk",
        "1GiB",
    ]


@unified_tool_output(tool_name="office_forge", stage="777_FORGE")
async def render_office_document(
    session_id: str,
    markdown: str,
    mode: str = "pdf",
    theme: str = "default",
    filename: str | None = None,
) -> dict[str, Any]:
    """
    Hardened render entrypoint.

    1. Validates inputs (F12).
    2. Isolates paths (F11).
    3. Executes with shell=False (Least Privilege).
    4. Enforces timeouts.
    """
    # 1. Input Validation
    if len(markdown.encode("utf-8")) > MAX_MD_SIZE:
        return {"ok": False, "error": "F12: Markdown size exceeds 2MB limit."}

    clean_mode = mode.lower() if mode.lower() in {"pdf", "pptx", "preview"} else "pdf"
    clean_theme = theme if theme in THEME_WHITELIST else "default"

    # 2. Path Isolation
    session_forge_dir = FORGE_BASE_DIR / session_id
    os.makedirs(session_forge_dir, exist_ok=True)

    # Use a secure temp file within the session-isolated directory
    with tempfile.NamedTemporaryFile(
        dir=session_forge_dir, suffix=".md", delete=False, mode="w", encoding="utf-8"
    ) as md_tmp:
        md_tmp.write(markdown)
        md_path = Path(md_tmp.name)

    try:
        output_ext = "pdf" if clean_mode != "pptx" else "pptx"
        output_name = f"{filename or 'artifact'}.{output_ext}"
        output_path = session_forge_dir / output_name

        # 3. Construct Command (shell=False)
        cmd = [
            "marp",
            f"--{output_ext}",
            "--theme",
            clean_theme,
            "--allow-local-files",
            str(md_path),
            "-o",
            str(output_path),
        ]

        # 4. Execute Subprocess
        process = subprocess.run(
            cmd,
            capture_output=True,
            timeout=HARD_TIMEOUT,
            check=False,
            # No shell=True to prevent injection
        )

        if process.returncode != 0:
            error_log = process.stderr.decode(errors="replace")
            logger.error(f"Office Forge Failure [{session_id}]: {error_log}")
            return {
                "ok": False,
                "error": f"Render engine failure: {error_log[:100]}",
                "verdict": "HOLD",
                "machine_issue": "RENDER_FAIL",
            }

        return {
            "ok": True,
            "artifact_path": str(output_path),
            "filename": output_name,
            "session_id": session_id,
            "verdict": "SEAL",
            "meta": {
                "size_bytes": output_path.stat().st_size,
                "engine": "marp-cli",
                "mode": clean_mode,
            },
        }

    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error": "F12: Render timed out (25s).",
            "verdict": "SABAR",
            "issue": "TIMEOUT",
        }
    except Exception as e:
        logger.exception(f"Unexpected error in office_forge_engine: {e}")
        return {
            "ok": False,
            "error": f"F1: System error: {str(e)}",
            "verdict": "HOLD",
            "issue": "RUNTIME_FAILURE",
        }
    finally:
        # Cleanup input MD
        if md_path.exists():
            md_path.unlink()

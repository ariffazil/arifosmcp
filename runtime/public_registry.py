from __future__ import annotations

import tomllib
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from .tool_specs import (
    ToolSpec,
    ResourceSpec,
    PromptSpec,
    PUBLIC_TOOL_SPECS,
    PUBLIC_RESOURCE_SPECS,
    PUBLIC_PROMPT_SPECS,
    MEGA_TOOLS,
)

ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = ROOT / "pyproject.toml"
DEFAULT_PUBLIC_BASE_URL = "https://arifosmcp.arif-fazil.com"

# Canonical 11 Mega-Tools
CANONICAL_PUBLIC_TOOLS = frozenset(spec.name for spec in PUBLIC_TOOL_SPECS)
EXPECTED_TOOL_COUNT = 11

# Mandatory schema for resource discovery
RUNTIME_ENVELOPE_SCHEMA = {
    "type": "object",
    "properties": {
        "ok": {"type": "boolean"},
        "verdict": {"type": "string"},
        "payload": {"type": "object"},
    }
}


@lru_cache
def get_pyproject_metadata() -> dict[str, Any]:
    """Load metadata from pyproject.toml."""
    try:
        with open(PYPROJECT_PATH, "rb") as f:
            return tomllib.load(f).get("project", {})
    except Exception:
        return {}


def release_version_label() -> str:
    """Return the canonical version string from pyproject.toml."""
    return str(get_pyproject_metadata().get("version", "2026.03.20-SOVEREIGN11"))


def release_version() -> str:
    return release_version_label()


def public_tool_names() -> tuple[str, ...]:
    """Return the names of all public tools."""
    return tuple(spec.name for spec in PUBLIC_TOOL_SPECS)


def public_tool_specs() -> tuple[ToolSpec, ...]:
    """Return all public tool specifications."""
    return PUBLIC_TOOL_SPECS


def public_tool_spec_by_name() -> dict[str, ToolSpec]:
    """Return a map of tool names to their specifications."""
    return {spec.name: spec for spec in PUBLIC_TOOL_SPECS}


PUBLIC_TOOL_SPEC_BY_NAME = public_tool_spec_by_name()


def is_public_profile(profile: str) -> bool:
    """Return True if the profile is a public-facing profile."""
    return profile.lower() in {"public", "chatgpt", "agnostic_public"}


def normalize_tool_profile(profile: str | None) -> str:
    """Normalize the tool profile string."""
    if not profile:
        return "public"
    return profile.lower().strip()


def build_server_json(public_base_url: str = DEFAULT_PUBLIC_BASE_URL) -> dict[str, Any]:
    """Build the canonical server.json manifest with the live public tool surface."""
    tools = []
    for spec in PUBLIC_TOOL_SPECS:
        tools.append(
            {
                "name": spec.name,
                "description": spec.description,
                "inputSchema": spec.input_schema,
            }
        )

    resources = []
    resource_templates = []
    for spec in PUBLIC_RESOURCE_SPECS:
        if spec.is_template:
            resource_templates.append({
                "uriTemplate": spec.uri,
                "name": spec.name,
                "description": spec.description,
                "mimeType": spec.mime_type
            })
        else:
            resources.append({
                "uri": spec.uri,
                "name": spec.name,
                "description": spec.description,
                "mimeType": spec.mime_type
            })

    prompts = []
    for spec in PUBLIC_PROMPT_SPECS:
        prompts.append({
            "name": spec.name,
            "description": spec.description,
            "arguments": spec.arguments or []
        })

    return {
        "mcpVersion": "2025-11-25",
        "name": "arifOS-APEX-G",
        "version": release_version_label(),
        "description": (
            f"Constitutional governance server — {len(PUBLIC_TOOL_SPECS)} canonical MCP tools "
            "with F1-F13 floor enforcement, metabolic routing, prompts, and resources."
        ),
        "vendor": {"name": "Muhammad Arif bin Fazil", "url": "https://arif-fazil.com"},
        "license": "AGPL-3.0-only",
        "homepage": "https://github.com/ariffazil/arifosmcp",
        "repository": "https://github.com/ariffazil/arifosmcp",
        "capabilities": {
            "constitutional_floors": 13,
            "metabolic_routing": True,
            "vault999": "postgresql+redis+merkle",
            "vector_memory": "qdrant+bge-m3-1024dim",
            "prompts": len(PUBLIC_PROMPT_SPECS),
            "resources": len(PUBLIC_RESOURCE_SPECS),
        },
        "serverUrl": public_base_url,
        "tools": tools,
        "resources": resources,
        "resourceTemplates": resource_templates,
        "prompts": prompts,
        "schema": {
            "input": {spec.name: spec.input_schema for spec in PUBLIC_TOOL_SPECS}
        }
    }


def get_legacy_redirect(name: str) -> tuple[str, str] | None:
    """Redirect legacy tool names to the new mega-tool surface (tool, mode)."""
    from arifosmcp.capability_map import CAPABILITY_MAP
    return CAPABILITY_MAP.get(name)


def tool_names_for_profile(profile: str) -> list[str]:
    """Return tool names for a given profile."""
    if is_public_profile(profile):
        return list(public_tool_names())
    return list(public_tool_names())


def build_internal_server_json(public_base_url: str = DEFAULT_PUBLIC_BASE_URL) -> dict[str, Any]:
    """Build the internal profile manifest (includes non-public tools)."""
    return build_server_json(public_base_url=public_base_url)


def build_mcp_discovery_json(public_base_url: str = DEFAULT_PUBLIC_BASE_URL) -> dict[str, Any]:
    """Build MCP discovery manifest for internal profile endpoints."""
    return build_internal_server_json(public_base_url=public_base_url)


def build_mcp_manifest(public_base_url: str = DEFAULT_PUBLIC_BASE_URL) -> dict[str, Any]:
    """Build the standard MCP manifest (alias for build_server_json)."""
    return build_server_json(public_base_url=public_base_url)


def verify_no_drift() -> dict[str, Any]:
    """Ensure registry matches expectations."""
    actual_names = {spec.name for spec in PUBLIC_TOOL_SPECS}
    missing = CANONICAL_PUBLIC_TOOLS - actual_names
    extra = actual_names - CANONICAL_PUBLIC_TOOLS
    is_ok = len(actual_names) == EXPECTED_TOOL_COUNT and not missing and not extra
    return {
        "ok": is_ok,
        "actual_count": len(actual_names),
        "expected_count": EXPECTED_TOOL_COUNT,
        "missing": list(missing),
        "extra": list(extra),
    }


def public_resource_uris() -> list[str]:
    return [spec.uri for spec in PUBLIC_RESOURCE_SPECS if not spec.is_template]


def public_tool_input_schemas() -> dict[str, Any]:
    return {spec.name: spec.input_schema for spec in PUBLIC_TOOL_SPECS}

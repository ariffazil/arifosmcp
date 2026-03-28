from __future__ import annotations

import os
from typing import Any


def _env_present(*names: str) -> bool:
    return any(os.getenv(name, "").strip() for name in names)


def _secret_file_present(*names: str) -> bool:
    for name in names:
        file_path = os.getenv(name, "").strip()
        if not file_path:
            continue
        try:
            with open(file_path, encoding="utf-8") as handle:
                if handle.read().strip():
                    return True
        except OSError:
            continue
    return False


def _env_truthy(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _configured(*names: str) -> str:
    return "configured" if _env_present(*names) else "not_configured"


def _url_configured(*names: str) -> str:
    return "configured" if _env_present(*names) else "not_configured"


def _aggregate_class_status(values: list[str]) -> str:
    configured = {"configured", "open_dev_mode"}
    if values and all(value in configured for value in values):
        return "configured"
    if any(value in configured for value in values):
        return "partial"
    return "not_configured"


def build_runtime_capability_map() -> dict[str, Any]:
    """
    Build a redacted runtime capability map.

    This intentionally reports capability and credential class state without
    exposing any raw secret/token/password values to the model or the user.
    """

    open_mode = _env_truthy("ARIFOS_GOVERNANCE_OPEN_MODE")
    if open_mode:
        continuity_signing = "open_dev_mode"
    elif _secret_file_present(
        "ARIFOS_GOVERNANCE_SECRET_FILE",
        "ARIFOS_GOVERNANCE_TOKEN_SECRET_FILE",
    ) or _env_present("ARIFOS_GOVERNANCE_SECRET", "ARIFOS_GOVERNANCE_TOKEN_SECRET"):
        continuity_signing = "configured"
    else:
        continuity_signing = "ephemeral_process_local"

    server_identity = {
        "continuity_signing": continuity_signing,
        "human_label": "server identity",
    }

    storage = {
        "vault_postgres": "configured"
        if _env_present("DATABASE_URL") or _env_present("POSTGRES_PASSWORD")
        else "not_configured",
        "session_cache": "configured" if _env_present("REDIS_URL") else "not_configured",
        "vector_memory": "configured" if _env_present("QDRANT_URL") else "not_configured",
    }

    providers = {
        "openai": _configured("OPENAI_API_KEY"),
        "anthropic": _configured("ANTHROPIC_API_KEY"),
        "google": _configured("GOOGLE_API_KEY"),
        "openrouter": _configured("OPENROUTER_API_KEY"),
        "venice": _configured("VENICE_API_KEY"),
        "ollama_local": _url_configured("OLLAMA_URL"),
        "brave": _configured("BRAVE_API_KEY"),
        "jina": _configured("JINA_API_KEY"),
        "perplexity": _configured("PPLX_API_KEY", "PERPLEXITY_API_KEY"),
        "firecrawl": _configured("FIRECRAWL_API_KEY"),
        "browserless": _configured("BROWSERLESS_TOKEN"),
    }

    ops = {
        "webhook_deploy": _configured("WEBHOOK_SECRET"),
        "grafana_access": _configured("GRAFANA_PASSWORD", "GF_SECURITY_ADMIN_PASSWORD"),
        "openclaw_restart": _configured("OPENCLAW_RESTART_TOKEN"),
        "api_bearer_auth": _configured("ARIFOS_API_KEY", "ARIFOS_API_TOKEN"),
    }

    llm_provider_states = [
        providers["openai"],
        providers["anthropic"],
        providers["google"],
        providers["openrouter"],
        providers["venice"],
        providers["ollama_local"],
    ]
    grounding_provider_states = [
        providers["brave"],
        providers["jina"],
        providers["perplexity"],
        providers["firecrawl"],
        providers["browserless"],
    ]

    capabilities = {
        "governed_continuity": "enabled"
        if continuity_signing in {"configured", "open_dev_mode"}
        else "degraded",
        "vault_persistence": "enabled" if storage["vault_postgres"] == "configured" else "degraded",
        "vector_memory": "enabled" if storage["vector_memory"] == "configured" else "degraded",
        "external_grounding": "enabled"
        if any(state == "configured" for state in grounding_provider_states)
        else "limited",
        "model_provider_access": "enabled"
        if any(state == "configured" for state in llm_provider_states)
        else "disabled",
        "local_model_runtime": "enabled"
        if providers["ollama_local"] == "configured"
        else "disabled",
        "auto_deploy": "enabled" if ops["webhook_deploy"] == "configured" else "disabled",
    }

    credential_classes = {
        "server_identity": continuity_signing,
        "storage_access": _aggregate_class_status(list(storage.values())),
        "provider_access": _aggregate_class_status(list(providers.values())),
        "ops_controls": _aggregate_class_status(list(ops.values())),
    }

    notes: list[str] = [
        (
            "Capability map is redacted by design. It reports what the server can do, "
            "never raw credential values."
        ),
        (
            "Agents should reason from capability state and credential classes, "
            "not from private secrets/tokens/passwords."
        ),
    ]
    if continuity_signing == "ephemeral_process_local":
        notes.append(
            "Continuity signing is ephemeral. Anchored auth_context will break "
            "across restart or replica changes."
        )
    if continuity_signing == "open_dev_mode":
        notes.append(
            "Open development mode is active. This is convenient for local "
            "testing but not acceptable for production."
        )

    return {
        "schema": "capability-map/v1",
        "redaction_policy": "no_raw_credential_values",
        "server_identity": server_identity,
        "credential_classes": credential_classes,
        "capabilities": capabilities,
        "storage": storage,
        "providers": providers,
        "ops": ops,
        "notes": notes,
    }

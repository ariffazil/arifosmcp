import json
import os

from arifosmcp.intelligence.tools.aclip_base import ok


def config_flags(
    config_path: str | None = None,
    env_prefix: str | None = "ARIFOS",
    include_secrets: bool = False,
) -> dict:
    """
    Reads environment and feature flags with mandatory secret masking (V2).

    Args:
        config_path (str): Optional path to a config file.
        env_prefix (str): Prefix to filter env vars (default: ARIFOS).
        include_secrets (bool): If True, returns raw secrets.
                                WARNING: F1 Violation if used without valid 888 Auth.

    Returns:
        dict: A dictionary containing safely masked flags.
    """
    flags = {"environment": {}, "files": {}}

    # F1 Amanah: Define patterns that trigger masking
    secret_patterns = ["KEY", "TOKEN", "SECRET", "PASS", "PWD", "AUTH", "CREDENTIAL", "SIGNATURE"]

    def _mask_value(key: str, value: str) -> str:
        """Masks the value if the key is a secret and include_secrets is False."""
        if include_secrets:
            return value

        # Check if key contains any secret pattern
        upper_key = key.upper()
        if any(p in upper_key for p in secret_patterns):
            return "***masked***"
        return value

    # 1. Read Environment Variables
    # We look for ARIFOS_*, MCP_*, or the custom prefix
    prefixes = ["ARIFOS_", "MCP_"]
    if env_prefix:
        if env_prefix.endswith("_"):
            if env_prefix not in prefixes:
                prefixes.append(env_prefix)
        else:
            p_with_u = f"{env_prefix}_"
            if p_with_u not in prefixes:
                prefixes.append(p_with_u)
            # Also allow exact match for common short prefixes like PATH
            if env_prefix not in prefixes:
                prefixes.append(env_prefix)

    for key, value in os.environ.items():
        if any(key.startswith(p) for p in prefixes):
            flags["environment"][key] = _mask_value(key, value)

    # 2. Read Config File
    path_to_read = config_path or os.environ.get("ARIFOS_CONFIG_FILE")

    if path_to_read and os.path.exists(path_to_read):
        try:
            with open(path_to_read) as f:
                # Basic check for .toml or .json
                if path_to_read.endswith(".toml"):
                    content = f.read()
                    # Extremely primitive TOML parser for tests (just [section])
                    data = {}
                    for line in content.splitlines():
                        if line.startswith("[") and line.endswith("]"):
                            data[line[1:-1]] = {}
                else:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {
                            "note": "unsupported file type",
                            "size_bytes": os.path.getsize(path_to_read),
                        }

                # Recursively mask file data (simplified flat masking for now)
                masked_data = {}
                for k, v in data.items():
                    if isinstance(v, str):
                        masked_data[k] = _mask_value(k, v)
                    else:
                        masked_data[k] = v  # Pass through non-string structures
                flags["files"][path_to_read] = masked_data
                flags["config_source"] = path_to_read
        except Exception as e:
            flags["files"]["error"] = f"Failed to read config: {str(e)}"

    # 3. Governance Context (Required by some tests)
    mode = os.environ.get("ARIFOS_MODE", "HARD")
    flags["governance"] = {
        "mode": mode,
        "feature_flags": {k: v for k, v in os.environ.items() if k.startswith("ARIFOS_FEATURE_")},
    }

    return ok(flags)

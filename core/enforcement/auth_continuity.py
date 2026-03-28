"""
core/enforcement/auth_continuity.py — F11 Amanah Handshake

Strict session continuity through cryptographic chaining.
Ensures that a session cannot be hijacked or forged between tool calls.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import hashlib
import hmac
import json
import os
import secrets
import time
import warnings
from typing import Any

# HMAC signs the actor's context so the kernel can verify it across calls
# without keeping a large in-memory state for every hop.


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _read_secret_file(*env_names: str) -> str:
    for env_name in env_names:
        file_path = os.getenv(env_name, "").strip()
        if not file_path:
            continue
        try:
            with open(file_path, encoding="utf-8") as handle:
                secret = handle.read().strip()
        except OSError as exc:
            warnings.warn(
                f"{env_name} points to unreadable secret file '{file_path}': {exc}",
                RuntimeWarning,
                stacklevel=2,
            )
            continue
        if secret:
            return secret
        warnings.warn(
            f"{env_name} points to empty secret file '{file_path}'.",
            RuntimeWarning,
            stacklevel=2,
        )
    return ""


def _read_secret_env(*env_names: str) -> str:
    for env_name in env_names:
        secret = os.getenv(env_name, "").strip()
        if secret:
            return secret
    return ""


def _load_governance_token_secret() -> str:
    if _env_flag("ARIFOS_GOVERNANCE_OPEN_MODE"):
        return "arifos-open-governance-dev-mode"

    secret = _read_secret_file(
        "ARIFOS_GOVERNANCE_SECRET_FILE",
        "ARIFOS_GOVERNANCE_TOKEN_SECRET_FILE",
    ) or _read_secret_env("ARIFOS_GOVERNANCE_SECRET", "ARIFOS_GOVERNANCE_TOKEN_SECRET")
    if secret:
        return secret

    # عارف — "The One Who Knows". The sovereign ignition word.
    # Default identity for the system named after its creator.
    # Override via ARIFOS_GOVERNANCE_SECRET env var if deploying for others.
    return "ARIF"


def _load_previous_governance_token_secret() -> str:
    if _env_flag("ARIFOS_GOVERNANCE_OPEN_MODE"):
        return ""

    return _read_secret_file(
        "ARIFOS_GOVERNANCE_SECRET_PREVIOUS_FILE",
        "ARIFOS_GOVERNANCE_TOKEN_SECRET_PREVIOUS_FILE",
    ) or _read_secret_env(
        "ARIFOS_GOVERNANCE_SECRET_PREVIOUS",
        "ARIFOS_GOVERNANCE_TOKEN_SECRET_PREVIOUS",
    )


_GOVERNANCE_TOKEN_SECRET = _load_governance_token_secret()
_GOVERNANCE_TOKEN_SECRET_PREVIOUS = _load_previous_governance_token_secret()
_AUTH_VERIFY_CACHE_TTL_SECONDS = 60
_auth_verify_cache: dict[str, tuple[bool, str, float, str]] = {}


def _sign_auth_context_with_secret(unsigned_context: dict[str, Any], secret: str) -> str:
    canonical = json.dumps(
        unsigned_context, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    )
    return hmac.new(
        secret.encode(),
        canonical.encode(),
        hashlib.sha256,
    ).hexdigest()


def sign_auth_context(unsigned_context: dict[str, Any]) -> str:
    return _sign_auth_context_with_secret(unsigned_context, _GOVERNANCE_TOKEN_SECRET)


def mint_auth_context(
    session_id: str,
    actor_id: str,
    token_fingerprint: str,
    approval_scope: list[str],
    parent_signature: str,
    ttl: int = 900,
    authority_level: str = "anonymous",
    prev_vault_hash: str | None = None,
) -> dict[str, Any]:
    now = int(time.time())
    unsigned_context = {
        "session_id": session_id,
        "actor_id": actor_id,
        "authority_level": authority_level,
        "token_fingerprint": token_fingerprint,
        "nonce": secrets.token_hex(12),
        "iat": now,
        "exp": now + ttl,
        "approval_scope": approval_scope,
        "parent_signature": parent_signature,
        "prev_vault_hash": prev_vault_hash,
    }
    return {
        **unsigned_context,
        "signature": sign_auth_context(unsigned_context),
    }


def verify_auth_context(session_id: str, auth_context: dict[str, Any]) -> tuple[bool, str]:
    signature_fields = [
        "session_id",
        "actor_id",
        "authority_level",
        "token_fingerprint",
        "nonce",
        "iat",
        "exp",
        "approval_scope",
        "parent_signature",
        "prev_vault_hash",
    ]
    # Required for structure
    for field in signature_fields:
        if field == "prev_vault_hash":
            continue # Optional field for signature reconstruction if present
        if field not in auth_context:
            return False, f"missing field: {field}"
    
    if "signature" not in auth_context:
        return False, "missing field: signature"

    if str(auth_context.get("session_id", "")) != session_id:
        return False, "session_id mismatch"

    exp = int(auth_context.get("exp", 0))
    if exp <= int(time.time()):
        return False, "auth_context expired"

    unsigned_context = {
        field: auth_context[field] for field in signature_fields if field in auth_context
    }
    expected_signatures = [
        _sign_auth_context_with_secret(unsigned_context, _GOVERNANCE_TOKEN_SECRET)
    ]
    if _GOVERNANCE_TOKEN_SECRET_PREVIOUS:
        expected_signatures.append(
            _sign_auth_context_with_secret(unsigned_context, _GOVERNANCE_TOKEN_SECRET_PREVIOUS)
        )

    presented_signature = auth_context.get("signature", "")
    if not any(
        hmac.compare_digest(presented_signature, expected) for expected in expected_signatures
    ):
        return False, "signature mismatch"

    return True, ""


def _auth_cache_key(session_id: str, auth_context: dict[str, Any]) -> str:
    signature = str(auth_context.get("signature", ""))
    expires_at = str(auth_context.get("exp", ""))
    fingerprint = str(auth_context.get("token_fingerprint", ""))
    payload = f"{session_id}:{signature}:{expires_at}:{fingerprint}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def verify_auth_context_cached(session_id: str, auth_context: dict[str, Any]) -> tuple[bool, str]:
    now = time.time()
    cache_key = _auth_cache_key(session_id, auth_context)
    cached = _auth_verify_cache.get(cache_key)
    if cached and (now - cached[2]) <= _AUTH_VERIFY_CACHE_TTL_SECONDS:
        return cached[0], cached[1]

    result = verify_auth_context(session_id, auth_context)
    _auth_verify_cache[cache_key] = (result[0], result[1], now, session_id)

    if len(_auth_verify_cache) > 2048:
        stale_keys = [
            key
            for key, (_, _, ts, _) in _auth_verify_cache.items()
            if (now - ts) > _AUTH_VERIFY_CACHE_TTL_SECONDS
        ]
        for key in stale_keys:
            _auth_verify_cache.pop(key, None)

    return result


def clear_auth_context_cache(session_id: str | None = None) -> None:
    if session_id is None:
        _auth_verify_cache.clear()
        return

    keys_to_remove = [
        key for key, (_, _, _, sid) in _auth_verify_cache.items() if sid == session_id
    ]
    for key in keys_to_remove:
        _auth_verify_cache.pop(key, None)


_REVOKED_SESSIONS: dict[str, tuple[str, float, str]] = {}
_REVOCATION_TTL_SECONDS = 86400


def revoke_session(session_id: str, reason: str, revoked_by: str = "system") -> dict[str, Any]:
    now = time.time()
    _REVOKED_SESSIONS[session_id] = (reason, now, revoked_by)
    clear_auth_context_cache(session_id)
    _prune_expired_revocations()
    return {
        "session_id": session_id,
        "revoked": True,
        "reason": reason,
        "revoked_by": revoked_by,
        "revoked_at": now,
    }


def is_session_revoked(session_id: str) -> tuple[bool, str | None]:
    if session_id in _REVOKED_SESSIONS:
        reason, _, _ = _REVOKED_SESSIONS[session_id]
        return True, reason
    return False, None


def _prune_expired_revocations() -> None:
    now = time.time()
    stale = [
        sid for sid, (_, ts, _) in _REVOKED_SESSIONS.items() if (now - ts) > _REVOCATION_TTL_SECONDS
    ]
    for sid in stale:
        _REVOKED_SESSIONS.pop(sid, None)


def get_all_revoked_sessions() -> list[dict[str, Any]]:
    _prune_expired_revocations()
    return [
        {"session_id": sid, "reason": reason, "revoked_at": ts, "revoked_by": by}
        for sid, (reason, ts, by) in _REVOKED_SESSIONS.items()
    ]


def verify_auth_context_with_revocation(
    session_id: str, auth_context: dict[str, Any]
) -> tuple[bool, str]:
    revoked, reason = is_session_revoked(session_id)
    if revoked:
        return False, f"session revoked: {reason}"
    return verify_auth_context(session_id, auth_context)

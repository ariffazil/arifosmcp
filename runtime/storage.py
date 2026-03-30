"""
arifosmcp/runtime/storage.py — Hardened Storage Backends (Redis + Encryption)
Wired for arifOS VPS Environment: srv1325122.hstgr.cloud

Note: py-key-value-aio[redis] must be installed in the image for Redis backend.
Until the image is rebuilt, falls back gracefully to None (in-memory / file-based).
"""

import os
import logging
from typing import Any

logger = logging.getLogger(__name__)


def _env_truthy(name: str) -> bool:
    value = os.getenv(name, "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def _should_use_redis_storage() -> bool:
    """Choose Redis only when it is explicitly requested for this process."""
    backend = os.getenv("ARIFOS_STORAGE_BACKEND", "").strip().lower()
    if backend:
        return backend == "redis"

    if _env_truthy("ARIFOS_MINIMAL_STDIO"):
        logger.info("ARIFOS_MINIMAL_STDIO enabled; using in-memory session state.")
        return False

    if os.getenv("REDIS_HOST"):
        return True

    logger.info("REDIS_HOST is unset; using in-memory session state.")
    return False


def build_encrypted_redis_store() -> Any:
    """
    Build a Fernet-encrypted Redis store.
    Returns None gracefully if dependencies aren't installed yet.
    """
    try:
        from cryptography.fernet import Fernet
        from key_value.aio.stores.redis import RedisStore
        from key_value.aio.wrappers.encryption import FernetEncryptionWrapper
    except ImportError as exc:
        logger.warning("Redis storage deps not available (%s). Vault will use file backend.", exc)
        return None

    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    encryption_key = os.getenv("STORAGE_ENCRYPTION_KEY")

    if not encryption_key:
        logger.warning("STORAGE_ENCRYPTION_KEY not set. Using ephemeral key (data lost on restart).")
        encryption_key = Fernet.generate_key().decode()

    try:
        redis_store = RedisStore(
            host=redis_host,
            port=redis_port,
            db=int(os.getenv("REDIS_DB", "0")),
        )
        encrypted_store = FernetEncryptionWrapper(
            key_value=redis_store,
            fernet=Fernet(encryption_key.encode()),
        )
        logger.info("Redis storage initialised: %s:%d", redis_host, redis_port)
        return encrypted_store
    except Exception as exc:
        logger.error("Failed to initialise Redis storage: %s", exc)
        return None


def get_storage() -> Any:
    """Return the primary storage backend. None = fall through to file/memory."""
    if _should_use_redis_storage():
        return build_encrypted_redis_store()
    return None

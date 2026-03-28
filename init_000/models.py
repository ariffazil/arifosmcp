"""
arifosmcp/init_000/models.py

Database table definitions for init_000.

4 tables only:
- provider_soul_profiles  : routing archetype / soul shorthand
- deployments              : runtime truth source
- session_anchors         : per-session bound snapshot
- drift_events            : mismatch log

Using sqlite3 (stdlib) for Phase 1.
Migration to Postgres is planned — all table creation is isolated here.
"""

from __future__ import annotations

import sqlite3
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

# ─── Path Resolution ──────────────────────────────────────────────────────────


def _db_path() -> Path:
    """Path to the SQLite database file."""
    db_dir = Path(__file__).parent / "data"
    db_dir.mkdir(exist_ok=True)
    return db_dir / "init_000.db"


# ─── Connection Helper ───────────────────────────────────────────────────────


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_db_path()), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# ─── Schema Definition ────────────────────────────────────────────────────────

SCHEMA_SQL = """
-- Provider soul profiles: routing archetype shorthand per provider/family
CREATE TABLE IF NOT EXISTS provider_soul_profiles (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_key          TEXT NOT NULL,
    family_key            TEXT NOT NULL,
    soul_label            TEXT NOT NULL,
    communication_style   TEXT NOT NULL DEFAULT '[]',  -- JSON array
    reasoning_style       TEXT NOT NULL DEFAULT '[]',  -- JSON array
    default_role_fit      TEXT NOT NULL DEFAULT '[]',  -- JSON array
    notes                 TEXT,
    version               TEXT NOT NULL DEFAULT '1.0',
    is_active             INTEGER NOT NULL DEFAULT 1,
    created_at            TEXT NOT NULL,
    updated_at            TEXT NOT NULL,
    UNIQUE(provider_key, family_key)
);

-- Deployments: runtime truth source — the law of the running system
CREATE TABLE IF NOT EXISTS deployments (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    deployment_id         TEXT NOT NULL UNIQUE,
    provider_key          TEXT NOT NULL,
    family_key            TEXT NOT NULL,
    model_id               TEXT NOT NULL,
    model_variant          TEXT,
    tools_live            TEXT NOT NULL DEFAULT '[]',  -- JSON array
    web_access            INTEGER NOT NULL DEFAULT 0,
    memory_mode           TEXT NOT NULL DEFAULT 'session_only',
    execution_mode        TEXT NOT NULL DEFAULT 'advisory',
    side_effects_allowed  INTEGER NOT NULL DEFAULT 0,
    auth_level            TEXT NOT NULL DEFAULT 'read_only',
    verified_at           TEXT NOT NULL,
    expires_at            TEXT,
    is_active             INTEGER NOT NULL DEFAULT 1,
    created_at            TEXT NOT NULL,
    updated_at            TEXT NOT NULL
);

-- Session anchors: snapshot of what init bound for each session
CREATE TABLE IF NOT EXISTS session_anchors (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id            TEXT NOT NULL UNIQUE,
    deployment_id         TEXT NOT NULL,
    provider_key_snapshot  TEXT NOT NULL,
    family_key_snapshot    TEXT NOT NULL,
    soul_label_snapshot    TEXT NOT NULL,
    bound_role            TEXT NOT NULL DEFAULT 'assistant',
    self_claim_boundary   TEXT NOT NULL DEFAULT '{}',  -- JSON object
    identity_verified     INTEGER NOT NULL DEFAULT 0,
    runtime_verified      INTEGER NOT NULL DEFAULT 0,
    created_at            TEXT NOT NULL,
    ended_at              TEXT,
    status                TEXT NOT NULL DEFAULT 'active',
    FOREIGN KEY (deployment_id) REFERENCES deployments(deployment_id)
);

-- Drift events: log mismatches after init
CREATE TABLE IF NOT EXISTS drift_events (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id              TEXT NOT NULL UNIQUE,
    session_id            TEXT NOT NULL,
    deployment_id         TEXT NOT NULL,
    event_type            TEXT NOT NULL,
    expected_value        TEXT,
    claimed_value         TEXT,
    severity              TEXT NOT NULL DEFAULT 'low',
    resolved              INTEGER NOT NULL DEFAULT 0,
    created_at            TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES session_anchors(session_id),
    FOREIGN KEY (deployment_id) REFERENCES deployments(deployment_id)
);
"""


def init_db() -> None:
    """Create all tables. Safe to call multiple times (CREATE TABLE IF NOT EXISTS)."""
    conn = get_connection()
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()


def reset_db() -> None:
    """Drop and recreate all tables. USE WITH CAUTION — destroys all data."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        for (table_name,) in cursor.fetchall():
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
        init_db()
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {_db_path()}")

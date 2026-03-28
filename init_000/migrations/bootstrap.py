#!/usr/bin/env python3
"""
arifosmcp/init_000/migrations/bootstrap.py

Bootstrap script for init_000 SQLite database.

Usage:
    python -m arifosmcp.init_000.migrations.bootstrap [--reset]

Options:
    --reset   Drop all tables and recreate from scratch (DESTRUCTIVE)

Phase:
    Phase 1 — SQLite (this file)
    Phase 2 — migrate to Postgres (see MIGRATION_NOTES.md)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Ensure parent package is importable
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from arifosmcp.init_000.models import init_db, reset_db, _db_path
from arifosmcp.init_000.db import load_seeds_from_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap init_000 database")
    parser.add_argument("--reset", action="store_true", help="Drop and recreate all tables")
    args = parser.parse_args()

    seed_dir = Path(__file__).parent.parent / "seeds"

    if args.reset:
        print("WARNING: Dropping all init_000 tables...")
        reset_db()
        print("Tables dropped and recreated.")
    else:
        print("Initializing init_000 database...")
        init_db()
        print(f"Database ready at: {_db_path()}")

    print(f"\nLoading seeds from: {seed_dir}")
    if seed_dir.exists():
        load_seeds_from_dir(str(seed_dir))
        print("Seeds loaded.")
    else:
        print(f"Seed directory not found: {seed_dir}")

    print("\nDone. init_000 is ready.")


if __name__ == "__main__":
    main()

# MIGRATION_NOTES.md

## Phase 1 → Phase 2 → Phase 3

### Phase 1: SQLite (CURRENT)
- **Storage**: `arifosmcp/init_000/data/init_000.db`
- **Schema**: 4 tables defined in `models.py`
- **Seeds**: JSON files in `seeds/`
- **No external dependencies** — uses stdlib sqlite3

### Phase 2: SQLite → Postgres (planned)

When ready to migrate:

1. **Add dependency**: `asyncpg` (already in pyproject.toml)
2. **New connection**: Use `asyncpg` or `SQLAlchemy 2.x` async engine
3. **Connection string**: Store in env var `INIT_V1_DATABASE_URL`
4. **Migration approach**: Alembic for schema versioning

Key considerations for migration:

```
Postgres mapping:
- INTEGER PRIMARY KEY → SERIAL PRIMARY KEY (or BIGSERIAL)
- TEXT → VARCHAR(n) or TEXT
- JSON arrays stored as TEXT in SQLite → JSONB in Postgres
- BOOLEAN INTEGER → BOOLEAN
- timestamps → TIMESTAMPTZ
```

Table creation scripts will be moved to `migrations/001_initial.sql`.

### Phase 3: Multi-node Postgres (future)
- Connection pooling via PgBouncer
- Read replicas for get_* queries
- WAL-based backup

---

## Design Decisions Preserved for Migration

### 1. All table definitions are isolated in `models.py`
This makes it easy to extract as `CREATE TABLE` statements for Postgres.

### 2. All DB operations are in `db.py`
Switching from sqlite3 to asyncpg only requires rewriting `get_connection()` and query functions. The function signatures remain the same.

### 3. JSON fields are serialized as TEXT in SQLite
This is intentional. Postgres has native JSONB which is better, but for migration compatibility we store as TEXT everywhere.

### 4. No raw SQL strings embedded in application logic
All queries go through `db.py` functions. Migration to Postgres only requires updating `db.py`.

### 5. Session anchors are append-only
The `session_anchors` table is designed for inserts + occasional updates (end_session). No deletes. This maps well to Postgres audit tables.

---

## Migration Checklist (when ready)

- [ ] Export SQLite data to JSON
- [ ] Create Postgres schema from `models.py` SCHEMA_SQL
- [ ] Add `asyncpg` or `SQLAlchemy 2.x` to dependencies
- [ ] Rewrite `get_connection()` to use async connection pool
- [ ] Add `INIT_V1_DATABASE_URL` to `.env.example`
- [ ] Update `db.py` functions to use async/await
- [ ] Update `tools.py` to await db calls
- [ ] Import seed data into Postgres
- [ ] Run all tests against Postgres
- [ ] Update deployment to use Postgres connection string

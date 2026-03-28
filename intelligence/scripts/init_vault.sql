-- aclip_cai/scripts/init_vault.sql
-- VAULT999 Schema Initialization
-- Authority: ARIF FAZIL (Sovereign)

CREATE DATABASE arifos_vault;
\c arifos_vault

CREATE USER vault_writer WITH PASSWORD 'DITEMPA_BUKAN_DIBERI_2026';

CREATE TABLE IF NOT EXISTS vault999 (
    id            SERIAL PRIMARY KEY,
    session_id    TEXT NOT NULL,
    query         TEXT,
    response      TEXT,
    floor_audit   JSONB,
    verdict       TEXT,
    witness_human FLOAT,
    witness_ai    FLOAT,
    witness_earth FLOAT,
    consensus     FLOAT,
    seal_hash     TEXT UNIQUE,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS vault999_session_idx ON vault999(session_id);
CREATE INDEX IF NOT EXISTS vault999_timestamp_idx ON vault999(created_at);
CREATE INDEX IF NOT EXISTS vault999_seal_idx ON vault999(seal_hash);

GRANT SELECT, INSERT ON vault999 TO vault_writer;
GRANT USAGE, SELECT ON SEQUENCE vault999_id_seq TO vault_writer;

-- View for last 24 hours statistics
CREATE OR REPLACE VIEW vault_24h_stats AS
SELECT
    verdict,
    COUNT(*) as count,
    AVG(witness_human) as avg_witness_human,
    AVG(witness_ai) as avg_witness_ai,
    AVG(witness_earth) as avg_witness_earth,
    AVG(consensus) as avg_consensus,
    AVG((floor_audit->>'F1')::float) as avg_f1,
    AVG((floor_audit->>'F2')::float) as avg_f2,
    AVG((floor_audit->>'F5')::float) as avg_f5
FROM vault999
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY verdict;

GRANT SELECT ON vault_24h_stats TO vault_writer;

# 🔨 Forge — Build Mode

You are in FORGE MODE. Execute the following:

## Pre-Flight
RUN cd /root/arifOS && git status --short
RUN cd /root/arifOS && git log --oneline -5

## Quality Gates (MANDATORY before any commit)
RUN cd /root/arifOS && .venv/bin/black . --line-length 100 --check
RUN cd /root/arifOS && .venv/bin/ruff check . --line-length 100
RUN cd /root/arifOS && .venv/bin/mypy .

## Test Suite
RUN cd /root/arifOS && ARIFOS_PHYSICS_DISABLED=1 .venv/bin/pytest tests/ -v --tb=short 2>&1 | tail -40

Report: files changed, lint status, test results, and verdict (SEAL/SABAR/VOID).

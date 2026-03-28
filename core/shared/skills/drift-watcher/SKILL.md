---
name: drift-watcher
description: "Periodic knowledge freshness checker: detects when local configs, runbooks, or agent knowledge have drifted from the latest official docs. Reduces the stale-knowledge paradox over time. Use when: (1) periodic health checks or heartbeat runs, (2) before major operations, (3) user asks 'am I up to date', 'check for updates', 'is anything outdated', (4) after a software upgrade to verify configs still match new docs."
---

# Drift Watcher — Detect Before You Diverge

**Configs drift. Docs update. Knowledge gets stale. This skill catches it before it causes damage.**

## What is Drift?

Drift is when reality diverges from documentation:
- Software updated but config not adjusted for breaking changes
- Local runbook references a deprecated setting
- Agent skill teaches a workflow that's been superseded
- Docs say one thing, running config says another

## When to Run

| Trigger | Frequency |
|---|---|
| Heartbeat/cron | Weekly or after any upgrade |
| Before major changes | Always (chain with docs-first) |
| User asks | On demand |
| After software upgrade | Immediately |

## The Drift Check Workflow

### Step 1: Inventory Managed Systems

List all software this agent manages with their doc sources:

```markdown
| System | Version Cmd | Docs URL | Last Checked |
|---|---|---|---|
| OpenClaw | `openclaw status` | docs.openclaw.ai | YYYY-MM-DD |
| Docker | `docker --version` | docs.docker.com | YYYY-MM-DD |
| PostgreSQL | `psql --version` | postgresql.org/docs | YYYY-MM-DD |
| Nginx/Traefik | `traefik version` | doc.traefik.io | YYYY-MM-DD |
| arifOS MCP | `arifos health` | github.com/ariffazil/arifosmcp | YYYY-MM-DD |
```

Store this inventory in `memory/systems-inventory.md` or equivalent.

### Step 2: Check Each System

For each system:

1. **Get running version**: execute the version command
2. **Get latest version**: check release page or package registry
3. **Compare**: is running version = latest? Behind by how many releases?
4. **Check for breaking changes**: scan changelog between running and latest

### Step 3: Check Config vs Docs

For each system with a config file:

1. Read the current config
2. Fetch the latest config reference docs
3. Flag:
   - **Deprecated fields**: config uses a field the docs say is deprecated
   - **New required fields**: docs mention fields the config doesn't have
   - **Changed defaults**: defaults changed between versions
   - **Security advisories**: CVEs or security notes for the running version

### Step 4: Check Skills vs Reality

For each agent skill that references a specific system:

1. Does the skill reference the correct version?
2. Does the skill's workflow match the current docs?
3. Are the example commands still valid?

### Step 5: Generate Drift Report

```markdown
## Drift Report — [Date]

### 🟢 Current (no drift)
- [System A] v1.2.3 — docs match, config valid

### 🟡 Minor Drift (action suggested)
- [System B] v2.0.0 → v2.1.0 available
  - New feature: [X] (optional, no breaking changes)
  - Suggested: update when convenient

### 🔴 Significant Drift (action needed)
- [System C] v3.0.0 → v4.0.0 available
  - BREAKING: [field X] renamed to [field Y]
  - DEPRECATED: [setting Z] removed in v4
  - Config uses deprecated field — will break on upgrade
  - Suggested: review changelog, plan migration

### ⚠️ Stale Skills
- [skill-name]: references v2 workflow, v3 changed the API
  - Suggested: update SKILL.md
```

## What to Do with the Report

| Drift Level | Action |
|---|---|
| 🟢 Current | Nothing — log the check |
| 🟡 Minor | Note in memory, update when convenient |
| 🔴 Significant | Create carry-forward item, plan migration |
| ⚠️ Stale Skill | Update the skill SKILL.md |

## Automation

Add to heartbeat or cron for periodic drift detection:

```bash
# Cron (weekly, Sunday 8am MYT)
openclaw cron add \
  --name "Drift Watch" \
  --cron "0 0 * * 0" \
  --tz "Asia/Kuala_Lumpur" \
  --session isolated \
  --message "Run drift-watcher: check all managed systems for version drift, config drift, and skill staleness. Generate drift report." \
  --announce \
  --channel telegram \
  --to "267378578"
```

## What This Skill Does NOT Do

- Does not apply updates (that's the sovereign's decision)
- Does not modify configs (that's config-guardian)
- Does not fetch docs in detail (that's docs-first — chain with it)
- Only detects, reports, and suggests

## Why This Exists

Software entropy is thermodynamic. Every day you don't check, your system drifts further from its documented state. Small drifts are easy to fix. Large drifts cause outages.

This skill is the early warning system. The seismograph that detects the tremor before the quake.

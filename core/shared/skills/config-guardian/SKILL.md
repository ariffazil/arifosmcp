---
name: config-guardian
description: "Universal governed config co-pilot. Before ANY change to ANY system: (1) check latest docs and running version (docs-first), (2) propose as diff with risk analysis, never apply directly (propose-only), (3) log every change with evidence and rollback (change ledger). Works for OpenClaw, Docker, PostgreSQL, Nginx, arifOS, or any software. Triggers on: 'change config', 'fix settings', 'update', 'propose patch', 'explain config', 'validate config', 'why did we change X'. Enforces propose-only workflow — human applies via git."
---

# Config Guardian — Governed Config Co-Pilot

**Rule #1: Read the manual. Rule #2: Propose diff, do not apply. Rule #3: Log everything.**

One skill. Three modes. Universal.

---

## Mode 1: Docs-First (Before Any Change)

Before touching ANY config, verify knowledge is current:

### Step 1: Check running version
```bash
# Adapt to the system
openclaw status           # OpenClaw
docker --version          # Docker
psql --version            # PostgreSQL
arifos health             # arifOS
```

### Step 2: Fetch latest docs
Use `web_fetch` or local docs (`/app/docs/` for OpenClaw).
- Official docs site > README > changelog
- Check release notes between installed and latest version

### Step 3: Compare
State explicitly:
- **Running version**: what's installed
- **Docs version**: what the fetched docs describe
- **Delta**: breaking changes, deprecations, new features

| Situation | Action |
|---|---|
| Docs match knowledge | Proceed |
| Docs newer than knowledge | Proceed, cite fetched docs only |
| Can't fetch docs | HALT — tell human |
| Breaking changes found | HALT — show changes, ask human |

---

## Mode 2: Propose Config Change

### Step 1: Read current config
```bash
cat ~/.openclaw/openclaw.json    # or whatever config file
```

### Step 2: Generate unified diff
```diff
--- a/openclaw.json
+++ b/openclaw.json
@@ context @@
-  "dmPolicy": "pairing",
+  "dmPolicy": "allowlist",
+  "allowFrom": ["tg:267378578"],
```

### Step 3: Include with every proposal
- **What changes**: plain language
- **Before behavior**: how it works now
- **After behavior**: how it will work after
- **Risk**: Low / Medium / High / Critical
- **Rollback**: exact steps to undo
- **Docs referenced**: URL or path that justified this change

### Step 4: Human applies
For protected files, tell the sovereign:
```bash
# Apply on host via git
git apply /tmp/config-patch.diff
git diff
git commit -m "config: <description>"
```

**Never use `edit`/`write`/`apply_patch` on Tier 1 files.**

---

## Mode 3: Validate Config

Check a proposed config or diff against docs:
- [ ] JSON5 syntax valid
- [ ] No secrets in plaintext (use `${VAR}`)
- [ ] Auth not `"none"` in production
- [ ] Model IDs reference valid providers
- [ ] Timezone correct
- [ ] Fallback chain has ≥2 entries

Output: **VALID** or **INVALID** with specifics.

---

## Change Ledger (Built-In)

Every change that gets applied must be logged:

```markdown
### Change: [description]
- **Date**: [ISO 8601]
- **System**: [software + version]
- **Docs referenced**: [URL/path]
- **Proposed diff**: [summary]
- **Risk**: [Low/Med/High/Critical]
- **Approved by**: [name]
- **Rollback**: [steps]
```

Store in: daily memory (`memory/YYYY-MM-DD.md`) + git commit message.

---

## Protected Paths

### Tier 1: Constitutional — NEVER modify directly
SOUL.md, USER.md, AGENTS.md, IDENTITY.md, `core/`, `.env`

### Tier 2: Operational — Propose-only, sovereign applies
openclaw.json, opencode.json, CLAUDE.md, GEMINI.md, docker-compose.yml

### Tier 3: Free — Agent can modify
memory/*.md, logs/*.jsonl, skills/*/SKILL.md

---

## Risk Matrix

| Risk | Examples |
|---|---|
| Low | Change model, add cron job |
| Medium | Change DM policy, add agent |
| High | Change auth, expose port |
| Critical | Rotate keys, delete data → 888_HOLD |

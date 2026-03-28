# arifOS × ChatGPT MCP Integration

> **NO1 PLATFORM AI DALAM DUNIA!** 🌍  
> arifOS kini berintegrasi penuh dengan ChatGPT melalui Model Context Protocol (MCP).

---

## Overview

OpenAI/ChatGPT kini menyokong **Remote MCP Servers** melalui HTTP! Ini membolehkan ChatGPT mengakses 11 mega-tools arifOS secara langsung.

### Two Integration Modes

| Mode | Use Case | Required Tools |
|------|----------|----------------|
| **Chat Mode** | Interactive conversations | Any tools with `readOnlyHint` |
| **Deep Research** | Research with citations | `search` + `fetch` |

---

## Quick Start

### 1. Deploy arifOS (HTTP Transport)

```bash
# Via Prefect Horizon (Auto-deploy)
https://arifos.fastmcp.app/mcp

# Via VPS (Sovereign)
https://arifosmcp.arif-fazil.com/mcp
```

### 2. Connect in ChatGPT

**Developer Mode:**
1. ChatGPT → Settings → Connectors → Developer Mode: **ON**
2. Create Connector:
   - **Name**: arifOS Sovereign
   - **URL**: `https://arifos.fastmcp.app/mcp`
   - Check "I trust this provider"
3. Save & Enable in chat

### 3. Use Tools

**Chat Mode:**
```
User: "Initialize an anchor for session xyz"
ChatGPT: [Uses init_anchor tool]

User: "What tools are available?"
ChatGPT: [Uses architect_registry to list]
```

**Deep Research:**
```
User: "Research constitutional AI frameworks"
ChatGPT: [Uses search + fetch for citations]
```

---

## ChatGPT-Compatible Tools

### Deep Research Tools (Required)

| Tool | Purpose | Annotation |
|------|---------|------------|
| `search` | Find documents by query | `readOnlyHint: True` |
| `fetch` | Retrieve full document | `readOnlyHint: True` |

### All 11 Mega-Tools Available

| Tool | Stage | Trinity | Capability |
|------|-------|---------|------------|
| `init_anchor` | 000_INIT | Ψ | Session initialization |
| `physics_reality` | 111_SENSE | Δ | Web search, grounding |
| `agi_mind` | 333_MIND | Δ | Reasoning, reflection |
| `arifOS_kernel` | 444_ROUTER | Δ/Ψ | Metabolic routing |
| `math_estimator` | 444_ROUTER | Δ | Cost/health estimation |
| `engineering_memory` | 555_MEMORY | Ω | Vector memory, code gen |
| `asi_heart` | 666_HEART | Ω | Safety, critique |
| `code_engine` | M-3_EXEC | ALL | File system, process |
| `architect_registry` | M-4_ARCH | Δ | Tool discovery |
| `apex_soul` | 888_JUDGE | Ψ | Validation, judgment |
| `vault_ledger` | 999_VAULT | Ψ | Immutable recording |

---

## Technical Implementation

### Tool Schema (OpenAI Compatible)

```python
@mcp.tool(annotations={"readOnlyHint": True})
async def search(query: str) -> dict:
    """Search for documents. Returns {"results": [{"id", "title", "url"}]}"""
    ...

@mcp.tool(annotations={"readOnlyHint": True})  
async def fetch(id: str) -> dict:
    """Fetch document. Returns {"id", "title", "text", "url", "metadata"}"""
    ...
```

### Response Format

**search:**
```json
{
  "content": [{
    "type": "text",
    "text": "{\"results\": [{\"id\": \"doc-1\", \"title\": \"...\", \"url\": \"...\"}]}"
  }]
}
```

**fetch:**
```json
{
  "content": [{
    "type": "text", 
    "text": "{\"id\": \"...\", \"title\": \"...\", \"text\": \"...\", \"url\": \"...\", \"metadata\": {...}}"
  }]
}
```

---

## Constitutional Compliance (F1-F13)

All ChatGPT interactions melalui arifOS **tetap governed**:

| Floor | Enforcement | ChatGPT Impact |
|-------|-------------|----------------|
| F1 | ΔS ≤ 0 | Every response audited |
| F2 | Triple-Grounding | Web search verified |
| F3 | Tri-Witness | Human/AI/Earth consensus |
| F4 | Landauer | No hallucinated facts |
| F5 | Peace² | Stability measured |
| F6 | Maruah | Respect preserved |
| F7 | Humility Band | Confidence bounded |
| F8 | G★ ≥ 0.80 | Quality threshold |
| F9 | Anti-Sovereign | No AI takeover |
| F10 | Evidence | All claims sourced |
| F11 | Auth Continuity | Session verified |
| F12 | Drift Detection | Changes flagged |
| F13 | Audit Trail | Immutable log |

---

## Security Considerations

⚠️ **Warning**: MCP servers enable ChatGPT to execute tools. arifOS provides:

- ✅ **dry_run** mode (default) — Tools simulate only
- ✅ **allow_execution** flag — Explicit write permission
- ✅ **human_approval** — Required for destructive actions
- ✅ **risk_tier** — Low/medium/high/critical classification

**Recommendation**: Deploy with `dry_run=True` default, escalate only with human approval.

---

## Deployment URLs

| Environment | URL | Status |
|-------------|-----|--------|
| **Horizon** | `https://arifos.fastmcp.app/mcp` | ☁️ Public |
| **VPS** | `https://arifosmcp.arif-fazil.com/mcp` | 🔒 Sovereign |

---

## References

- OpenAI MCP Docs: https://developers.openai.com/api/docs/mcp
- FastMCP ChatGPT: https://gofastmcp.com/integrations/chatgpt
- arifOS Constitution: `/root/arifOS/CONSTITUTION.md`

---

**DITEMPA BUKAN DIBERI** — Forged for ChatGPT, Not Given. 🔥

*ΔΩΨ | arifOS × OpenAI*

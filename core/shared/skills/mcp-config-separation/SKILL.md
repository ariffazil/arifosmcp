# MCP Config Separation Pattern

**Purpose:** Clean architecture for managing MCP servers across global (generic) and project-specific (contextual) scopes.

**Version:** v1.0-SEAL  
**Authority:** Muhammad Arif bin Fazil (888 Judge)  
**Motto:** *Ditempa bukan diberi* — Forged, Not Given

---

## The Problem (High Entropy)

**Before:** 12 MCPs duplicated across 4 config files
```
Claude Desktop:  ~/.mcp.json          → 12 entries
Kimi CLI:        ~/.kimi/mcp.json     → 12 entries  (duplicate)
arifOS/Claude:   arifOS/.mcp.json     → 12 entries  (partially different)
arifOS/Kimi:     arifOS/.kimi/mcp.json → 12 entries (partially different)

Total: 48 entries to maintain
Entropy: HIGH — edit github? Update 4 files. Error-prone.
```

---

## The Solution (Low Entropy)

**After:** Separation of concerns

### Layer 1: Global Configs (Generic MCPs)
| MCP | `~/.mcp.json` (Claude) | `~/.kimi/mcp.json` (Kimi) |
|-----|------------------------|--------------------------|
| memory | ✅ | ✅ |
| sequential-thinking | ✅ | ✅ |
| fetch | ✅ (uvx) | ✅ (uvx) |
| time | ✅ (uvx) | ✅ (uvx) |
| brave-search | ✅ | ✅ |
| github | ✅ | ✅ |
| context7 | ✅ | ✅ |
| perplexity | ✅ | ✅ |
| puppeteer | ✅ | ✅ |
| playwright | ✅ | ✅ |
| python-repl | ✅ | - |

**Count:** 11 MCPs × 2 files = 22 entries  
**Scope:** Shared across ALL projects

### Layer 2: Project Configs (Context-Specific)
| MCP | `arifOS/.mcp.json` | `arifOS/.kimi/mcp.json` |
|-----|-------------------|------------------------|
| aaa-mcp | ✅ (needs cwd) | ✅ (needs cwd) |
| filesystem | ✅ (scoped path) | ✅ (scoped path) |
| git | ✅ (needs cwd) | ✅ (needs cwd) |
| memory | ✅ (custom path) | ✅ (custom path) |

**Count:** 4 MCPs × 2 files = 8 entries  
**Scope:** arifOS project only

---

## Constitutional Compliance

| Floor | How This Pattern Honors It |
|-------|---------------------------|
| **F1 Amanah** | Scoped paths contain filesystem access; reversible by design |
| **F2 Truth** | Single source of truth for each MCP; no drift between configs |
| **F4 Clarity** | ΔS ≤ 0: Reduced 48 entries → 30 entries (37% entropy reduction) |
| **F10 Ontology** | Clear type boundaries: generic vs contextual |
| **F11 Authority** | Project configs need cwd = explicit context declaration |

---

## Configuration Templates

### Global: `~/.mcp.json` (Claude Desktop)
```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    },
    "time": {
      "command": "uvx",
      "args": ["mcp-server-time"]
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-context7"]
    },
    "perplexity": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-perplexity"],
      "env": {
        "PERPLEXITY_API_KEY": "${PERPLEXITY_API_KEY}"
      }
    },
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@executeautomation/playwright-mcp-server"]
    },
    "python-repl": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-python-repl"]
    }
  }
}
```

### Global: `~/.kimi/mcp.json` (Kimi CLI)
```json
{
  "mcpServers": {
    "memory": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-memory"] },
    "sequential-thinking": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"] },
    "fetch": { "command": "uvx", "args": ["mcp-server-fetch"] },
    "time": { "command": "uvx", "args": ["mcp-server-time"] },
    "brave-search": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-brave-search"], "env": { "BRAVE_API_KEY": "${BRAVE_API_KEY}" } },
    "github": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"], "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}" } },
    "context7": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-context7"] },
    "perplexity": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-perplexity"], "env": { "PERPLEXITY_API_KEY": "${PERPLEXITY_API_KEY}" } },
    "puppeteer": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-puppeteer"] },
    "playwright": { "command": "npx", "args": ["-y", "@executeautomation/playwright-mcp-server"] }
  }
}
```

### Project: `arifOS/.mcp.json` (arifOS-specific, Claude)
```json
{
  "mcpServers": {
    "aaa-mcp": {
      "command": "python",
      "args": ["-m", "aaa_mcp", "stdio"],
      "cwd": "${workspaceFolder}"
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:/Users/User/arif-fazil-sites"]
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"],
      "cwd": "${workspaceFolder}"
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "C:/Users/User/arif-fazil-sites/.memory.json"
      }
    }
  }
}
```

### Project: `arifOS/.kimi/mcp.json` (arifOS-specific, Kimi)
```json
{
  "mcpServers": {
    "aaa-mcp": { "command": "python", "args": ["-m", "aaa_mcp", "stdio"], "cwd": "${workspaceFolder}" },
    "filesystem": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:/Users/User/arif-fazil-sites"] },
    "git": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-git"], "cwd": "${workspaceFolder}" },
    "memory": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-memory"], "env": { "MEMORY_FILE_PATH": "C:/Users/User/arif-fazil-sites/.memory.json" } }
  }
}
```

---

## Key Design Decisions

### 1. `cwd` Requirement
MCPs needing `cwd` (aaa-mcp, git) are **context-aware**. They behave differently based on project location.

### 2. Filesystem Scoping
```json
"args": ["-y", "@modelcontextprotocol/server-filesystem", "C:/Users/User/arif-fazil-sites"]
```
Filesystem is **bounded** to project path (F1 Amanah — reversible containment).

### 3. Memory Isolation
```json
"env": { "MEMORY_FILE_PATH": "C:/Users/User/arif-fazil-sites/.memory.json" }
```
Each project gets its own memory file. No cross-contamination.

### 4. UVX vs NPX
| Tool | Runtime | Why |
|------|---------|-----|
| fetch | uvx | Python-native, lightweight |
| time | uvx | Python-native, no Node bloat |
| Others | npx | Node ecosystem standard |

---

## Usage Flow

```
1. Start Claude Desktop / Kimi CLI
   ↓
2. Load GLOBAL configs (~/.mcp.json)
   → memory, fetch, time, github... available everywhere
   ↓
3. Open project folder (arifOS/)
   → Load PROJECT configs (.mcp.json)
   → aaa-mcp, filesystem (scoped), git (cwd-aware), memory (isolated)
   ↓
4. MCP union: GLOBAL ∪ PROJECT = 15 unique MCPs
```

---

## Migration Guide

### From Monolithic to Separated

**Step 1:** Backup existing configs
```bash
cp ~/.mcp.json ~/.mcp.json.backup
cp ~/.kimi/mcp.json ~/.kimi/mcp.json.backup
```

**Step 2:** Identify generic vs contextual MCPs
- Generic: Tools that work the same everywhere (memory, fetch, time, search)
- Contextual: Tools that need project context (filesystem, git, aaa-mcp)

**Step 3:** Move generic to global
```bash
# Edit ~/.mcp.json and ~/.kimi/mcp.json
# Keep only generic MCPs
```

**Step 4:** Create project-specific configs
```bash
# Create arifOS/.mcp.json
# Create arifOS/.kimi/mcp.json
# Add only contextual MCPs
```

**Step 5:** Verify union
```bash
# Count unique MCPs across both layers
# Should be: GLOBAL.count + PROJECT.count (no overlap)
```

---

## Verification Checklist

- [ ] Global configs load without errors
- [ ] Project configs load without errors
- [ ] No duplicate MCP names across layers
- [ ] Filesystem scoped to project path
- [ ] Memory isolated per project
- [ ] `cwd`-dependent MCPs have correct working directory
- [ ] Environment variables (BRAVE_API_KEY, GITHUB_TOKEN) configured

---

## Emergent Capabilities

With this separation, you unlock:

| Pattern | Capability |
|---------|-----------|
| Global + Project | **Contextual MCP Union** — Tools adapt to project |
| Scoped filesystem | **F1 Amanah Enforcement** — No escape from project bounds |
| Isolated memory | **Project-Specific Knowledge Graph** — Clean data separation |
| cwd-aware tools | **Implicit Context Loading** — Tools know where they are |

---

## References

- **arifOS Constitutional Framework:** https://apex.arif-fazil.com/llms.txt
- **Trinity Architecture:** https://github.com/ariffazil/arif-fazil-sites/blob/main/TRINITY_ARCHITECTURE.md
- **MCP Specification:** https://modelcontextprotocol.io

---

**SEALED BY:** 888_JUDGE  
**DATE:** 2026-02-06  
**VERSION:** v1.0  
**STATUS:** ARCHITECTURE_PATTERN

*Ditempa bukan diberi* 💎🔥🧠

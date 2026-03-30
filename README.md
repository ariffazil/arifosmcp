# arifosmcp — Constitutional MCP Server Implementation

> **DITEMPA BUKAN DIBERI** — *Forged, Not Given* [ΔΩΨ | ARIF]
>
> **VERSION:** 2026.03.28-SEALED | **STATUS:** SOVEREIGNLY SEALED | **AUTHORITY:** 888_JUDGE

---

## 🔗 CANONICAL LINKS (Source of Truth)

### Live Services
| Service | URL | Purpose |
|---------|-----|---------|
| **MCP Endpoint** | https://arifosmcp.arif-fazil.com/mcp | Main API |
| **Health + Tools** | https://arifosmcp.arif-fazil.com/health | Capability map |
| **Tool Explorer** | https://arifosmcp.arif-fazil.com/tools | Interactive browser |

### GitHub Repositories
| Repo | URL |
|------|-----|
| **arifOS (parent)** | https://github.com/ariffazil/arifOS |
| **arifosmcp (this)** | https://github.com/ariffazil/arifOS/tree/main/arifosmcp |

---

## 📋 CANONICAL DOCUMENTS (Architecture Reference)

| Document | Path | Purpose |
|----------|-------|---------|
| **arifOS README** | [`../README.md`](../README.md) | Vision, architecture, snapshot of truth |
| **000_CONSTITUTION.md** | [`../000/000_CONSTITUTION.md`](../000/000_CONSTITUTION.md) | The 13 Floors — F1-F13 |
| **K_FORGE.md** | [`../000/ROOT/K_FORGE.md`](../000/ROOT/K_FORGE.md) | Pre-deployment evolution |
| **K_FOUNDATIONS.md** | [`../000/ROOT/K_FOUNDATIONS.md`](../000/ROOT/K_FOUNDATIONS.md) | 99-domain math |
| **AGENTS.md** | [`../AGENTS.md`](../AGENTS.md) | AI agent behavior rules |
| **philosophy_atlas.json** | [`../data/philosophy_atlas.json`](../data/philosophy_atlas.json) | 27-zone quotes |

---

## 🎯 SNAPSHOT OF TRUTH

**What is arifosmcp?**

arifosmcp is the **implementation** of the arifOS constitutional intelligence kernel — the actual code that enforces the 13 Floors, runs the 000-999 pipeline, and delivers the 11 mega-tools.

**The Parent vs. This Document:**

| arifOS README | arifosmcp README (this) |
|---------------|-------------------------|
| **WHY** — Vision, philosophy, strategic architecture | **HOW** — Implementation, code, deployment mechanics |
| What it means | How it works |
| Strategic context | Technical specification |
| Human readable | Human + AI readable |

**Core Function:**

```mermaid
graph LR
    A["User Request"] --> B["MCP Protocol"]
    B --> C["Constitutional Filter<br/>(F1-F13)"]
    C --> D["Tool Execution"]
    D --> E["Audit Log"]
    
    style A fill:#1a1a2e,color:#fff
    style B fill:#16213e,color:#fff
    style C fill:#0f3460,color:#fff
    style D fill:#1a1a2e,color:#fff
    style E fill:#16213e,color:#fff
```

---

## 🏗️ ARCHITECTURE OVERVIEW

### Entry Points

```mermaid
graph TB
    A["server.py<br/>Universal Entry"] --> B{"FastMCP Version?"}
    B -->|"2.x"| C["server_horizon.py<br/>Proxy Mode<br/>8 tools"]
    B -->|"3.x"| D["runtime/server.py<br/>Full Kernel<br/>11 tools"]
    
    style A fill:#1a1a2e,color:#fff
    style C fill:#16213e,color:#fff
    style D fill:#0f3460,color:#fff
```

### Server Modes

| Mode | Tools | Features | Entrypoint |
|------|-------|----------|------------|
| **Horizon (Cloud)** | 8 | Proxied to VPS | `server_horizon.py` |
| **VPS (Sovereign)** | 12 | Full kernel, local Ollama | `runtime/server.py` |

---

## 🚦 LIVE MCP CONTRACT STATUS

| Subsystem | Constitutional | Operational | Production | Stability |
|-----------|----------------|-------------|------------|-----------|
| **Anchoring** | ✅ Verified | ✅ Stable | ✅ Ready | **A** |
| **Registry** | ✅ Verified | ✅ Stable | ✅ Ready | **A** |
| **Reasoning** | ✅ Verified | ✅ Hardened | ✅ Ready | **B** |
| **Vitals** | ✅ Verified | ✅ Corrected | ✅ Ready | **B** |
| **Diagnostic** | ✅ Verified | ✅ New | ✅ Ready | **B** |

---

## 🔧 TOOL INVENTORY (12 Mega-Tools)

### Tool Reference Table

| Tool | Band | Stage | Constitutional Role | Modes |
|------|------|-------|-------------------|-------|
| `init_anchor` | 000_INIT | 000 | Session anchoring, Ω₀, philosophy | init, state, status, revoke, refresh |
| `arifOS_kernel` | 444_ROUT | 444 | Primary metabolic orchestration | kernel, status |
| `apex_soul` | 888_JUDGE | 888 | Sovereign verdict and defense | judge, rules, validate, armor, probe |
| `vault_ledger` | 999_SEAL | 999 | Immutable ledger (Merkle chain) | seal, verify, resolve |
| `agi_mind` | 333_MIND | 333 | Constitutional reasoning and synthesis | reason, reflect, forge |
| `asi_heart` | 666_HEART | 666 | Safety critique, impact simulation | critique, simulate |
| `engineering_memory` | 555_MEM | 555 | Governed engineering and context | engineer, write, vector_query |
| `physics_reality` | 111_SENSE | 111 | Environmental grounding and time | search, ingest, atlas, time |
| `math_estimator` | 444_ROUT | 444 | Thermodynamic health and vitals | cost, health, vitals |
| `code_engine` | M-3_EXEC | M-3 | Sandboxed execution and observation | fs, process, net, replay |
| `architect_registry` | M-4_ARCH | M-4 | Tool discovery and schema catalog | list, read, register |
| `compat_probe` | M-5_COMP | M-5 | Interoperability and enum audit | audit, probe, ping |

---

## 📝 TOOL SPECIFICATIONS

### init_anchor (000_INIT)

**Purpose:** Initialize constitutional session.

```python
async def init_anchor(
    actor_id: str,
    declared_name: str,
    mode: Literal["init", "seal", "status"] = "init",
    thermodynamic_budget: dict = None,
    architect_registry: dict = None
) -> dict
```

**Returns:**
```python
{
    "session_id": str,               # UUID
    "omega_0": float,                # Baseline uncertainty ∈ [0.03, 0.05]
    "delta_s": float,                # Baseline entropy
    "telos_manifold": dict,          # Telos vector weights
    "godel_lock": dict,              # Gödel lock status
    "constitutional_context": str,    # AI system prompt
    "philosophy": str,                # Selected quote from atlas
    "vitality_index": float,         # Ψ score
    "verdict_range": str             # "000_SEAL" | "101-499" | "500-899" | "999_VOID"
}
```

---

### architect_registry (000_INIT)

**Purpose:** Discover tools and constitutional constraints.

```python
async def architect_registry() -> dict
```

**Returns:**
```python
{
    "tools": [
        {
            "name": str,
            "band": str,
            "stage": int,
            "constitutional_constraints": ["F1", "F2", ...],
            "input_schema": dict,
            "output_schema": dict
        }
    ],
    "total_count": int,
    "catalog_hash": str               # SHA-256 integrity
}
```

---

### physics_reality (111_SENSE)

**Purpose:** Ground queries in real-world data. Prevents hallucinations.

```python
async def physics_reality(
    query: str,
    mode: Literal["time", "search", "reality_check"] = "search",
    time_data: dict = None
) -> dict
```

**Constitutional Filter:** F2 (Truth) — all factual claims require citation.

---

### agi_mind (333_MIND)

**Purpose:** Constitutional reasoning with three-phase Ollama pipeline.

```mermaid
graph TB
    A["Query"] --> B["Phase 1: FAST<br/>Quick pattern match"]
    B --> C["Phase 2: REFLECT<br/>Deep reasoning"]
    C --> D["Phase 3: DECIDE<br/>Action selection"]
    
    B -->|"F4 Clarity<br/>ΔS ≤ 0"| E["Pass/Fail"]
    C -->|"F2 Truth<br/>F3 Tri-Witness"| E
    D -->|"Constitutional<br/>Prefix"| E
    
    style A fill:#1a1a2e,color:#fff
    style B fill:#16213e,color:#fff
    style C fill:#0f3460,color:#fff
    style D fill:#1a1a2e,color:#fff
```

```python
async def agi_mind(
    query: str,
    context: dict,
    mode: Literal["think", "reflect", "decide"] = "think"
) -> dict
```

**Three Phases:**

| Phase | Focus | Floors |
|-------|-------|--------|
| **Phase 1 (FAST)** | Quick pattern match | F4 Clarity |
| **Phase 2 (REFLECT)** | Deep reasoning | F2 Truth, F3 Tri-Witness |
| **Phase 3 (DECIDE)** | Action selection | Constitutional prefix |

**Constitutional Prefix:**
```
CONSTITUTIONAL FRAMEWORK (ΔΩΨ | ARIF):
- Δ CLARITY: Reduce entropy. ΔS ≤ 0.
- Ω HUMILITY: Stay in bounds. Ω ∈ [0.03, 0.05].
- Ψ VITALITY: Every action witnessed.

FLOORS ACTIVE: [F1-F13]
```

---

### arifOS_kernel (444_ROUT)

**Purpose:** Primary conductor — orchestrates full 000→888 pipeline.

```mermaid
graph LR
    A["Query"] --> B["1. Parse Intent<br/>111_SENSE"]
    B --> C["2. Ground Reality<br/>physics_reality"]
    C --> D["3. Reason<br/>agi_mind"]
    D --> E["4. Route Action<br/>444_ROUT"]
    E --> F["5. Safety Critique<br/>asi_heart"]
    F --> G["6. Estimate Cost<br/>math_estimator"]
    G --> H["7. Issue Verdict<br/>apex_soul"]
    
    style A fill:#1a1a2e,color:#fff
    style B fill:#16213e,color:#fff
    style C fill:#0f3460,color:#fff
    style D fill:#1a1a2e,color:#fff
    style E fill:#16213e,color:#fff
    style F fill:#0f3460,color:#fff
    style G fill:#1a1a2e,color:#fff
    style H fill:#16213e,color:#fff
```

```python
async def arifOS_kernel(
    query: str,
    tools: list[str],
    context: dict
) -> dict
```

---

### asi_heart (666_HEART)

**Purpose:** Safety critique — F5 Peace², F9 Ethics, harm potential.

```python
async def asi_heart(
    action_plan: dict
) -> dict
```

**Returns:**
```python
{
    "peace_squared": float,          # Must be ≥ 1.0 (F5)
    "c_dark": float,                 # Must be < 0.30 (F9)
    "harm_potential": str,           # "NONE" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    "f5_pass": bool,
    "f9_pass": bool,
    "recommendations": list[str]
}
```

---

### math_estimator (777_OPS)

**Purpose:** Thermodynamic cost estimation.

```python
async def math_estimator(
    operation: str,
    inputs: dict
) -> dict
```

**Returns:**
```python
{
    "landauer_limit_pJ": float,       # Minimum thermodynamic cost
    "entropy_change": float,         # ΔS (must be ≤ 0 for F4)
    "coherence_score": float,         # System coherence [0, 1]
    "estimated_energy_J": float,      # Total energy estimate
    "shannon_entropy_bits": float     # Information entropy
}
```

---

### apex_soul (888_JUDGE)

**Purpose:** Final constitutional judgment.

```python
async def apex_soul(
    evidence: dict,
    context: dict
) -> dict
```

**Returns:**
```python
{
    "verdict": str,                   # "000_SEAL" | "101-499" | "500-899" | "999_VOID"
    "floor_scores": {
        "F1": {"passed": bool, "score": float},
        "F2": {"passed": bool, "score": float},
        # ... F3-F13
    },
    "genius_index": float,            # G = A × P × X × E² (≥ 0.80)
    "vitality_index": float,           # Ψ (≥ 1.0 for healthy)
    "witness_cube": float,            # W³ (≥ 0.95)
    "override_available": bool         # 888_JUDGE can always override
}
```

---

### vault_ledger (999_SEAL)

**Purpose:** Immutable audit storage with Merkle sealing.

```python
async def vault_ledger(
    data: dict,
    tier: Literal["constitutional", "standard", "transient"] = "standard"
) -> dict
```

**Tiers:**

| Tier | Compliance | Retention |
|------|------------|-----------|
| `constitutional` | Full F1-F13 | Permanent |
| `standard` | Standard audit | Immutable |
| `transient` | Ephemeral | Auto-purged |

---

### engineering_memory (555_MEM)

**Purpose:** Redis-backed session memory.

```python
async def engineering_memory(
    key: str,
    operation: Literal["get", "set", "delete", "list"],
    value: any = None,
    ttl: int = 3600
) -> dict
```

---

### code_engine (—)

**Purpose:** Constrained Python execution for tool actions.

```python
async def code_engine(
    code: str,
    language: Literal["python", "javascript"] = "python",
    constraints: dict = None
) -> dict
```

**Safety Constraints:**
- No filesystem access
- No network access
- No subprocess creation
- Memory limit: 128MB
- Timeout: 30s

---

## 🌐 API ENDPOINTS

### HTTP Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check + capability map |
| `/tools` | GET | Tool registry |
| `/mcp` | POST | MCP protocol handler |
| `/webmcp` | POST | WebMCP (W3C standard) |
| `/a2a` | POST | A2A (Google protocol) |
| `/.well-known/agent.json` | GET | Agent card |

### MCP Protocol Examples

```bash
# List tools
curl -X POST https://arifosmcp.arif-fazil.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'

# Call init_anchor
curl -X POST https://arifosmcp.arif-fazil.com/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0","id":2,"method":"tools/call",
    "params":{
      "name":"init_anchor",
      "arguments":{
        "actor_id":"test",
        "declared_name":"TestAgent"
      }
    }
  }'
```

---

## ⚙️ CONFIGURATION

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8080 | Server port |
| `OLLAMA_URL` | http://ollama:11434 | Ollama endpoint |
| `OLLAMA_MODEL` | llama3.2:latest | Default model |
| `REDIS_URL` | redis://redis:6379/0 | Redis connection |
| `DATABASE_URL` | — | PostgreSQL (optional) |
| `QDRANT_URL` | http://qdrant:6333 | Vector DB (optional) |
| `PYTHONPATH` | /usr/src/app | Package path |
| `AAA_MCP_TRANSPORT` | http | MCP transport type |

### Docker Compose

```yaml
services:
  arifosmcp:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - OLLAMA_URL=http://ollama_engine:11434
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://user:pass@postgres:5432/arifos_vault
      - QDRANT_URL=http://qdrant:6333
    ports:
      - "127.0.0.1:8080:8080"
```

---

## 📁 CODE ARCHITECTURE

### Directory Structure

```
arifosmcp/
├── README.md                      # ← This file
├── server.py                      # Universal entry
├── server_horizon.py              # Horizon proxy (FastMCP 2.x)
├── pyproject.toml                 # Dependencies
├── requirements.txt               # Pip dependencies
│
├── runtime/
│   ├── server.py                  # Full kernel (FastMCP 3.x)
│   ├── philosophy.py              # 27-zone atlas
│   ├── init_anchor_hardened.py    # Session anchoring
│   ├── tools_hardened_dispatch.py # Tool routing
│   ├── tools_hardened_v2.py       # Mega-tools
│   ├── tools_internal.py          # Internal utils
│   └── thermo_estimator.py        # Thermodynamic math
│
├── core/
│   ├── governance_kernel.py       # Main orchestrator
│   ├── pipeline.py                 # Execution pipeline
│   └── organs/
│       ├── _1_agi.py             # Mind (333_MIND)
│       ├── _2_asi.py             # Heart (666_HEART)
│       └── _3_apex.py            # Soul (888_JUDGE)
│
├── intelligence/
│   └── tools/
│       ├── thermo_estimator.py   # Cost estimation
│       └── wisdom_quotes.py       # Quote integration
│
├── aaa_mcp/                       # FastMCP tool definitions
├── transport/                     # Protocol transport
├── shared/                        # Shared utilities
└── enforcement/                   # Constitutional enforcement
```

---

## 🛡️ CONSTITUTIONAL ENFORCEMENT

### Floor Compliance Matrix

| Floor | Enforcement | Violation Response |
|-------|-------------|-------------------|
| **F1 Amanah** | Reversibility check | Require human approval |
| **F2 Truth** | Citation required | Flag as "Estimate Only" |
| **F3 Tri-Witness** | W³ computation | Block below 0.95 |
| **F4 Clarity** | Entropy measurement | Reject if ΔS > 0 |
| **F5 Peace²** | Harm potential | Reject if < 1.0 |
| **F6 Empathy** | RASA scoring | Warn below 0.7 |
| **F7 Humility** | Ω bounds | Reject outside [0.03, 0.05] |
| **F8 Genius** | G computation | Alert below 0.80 |
| **F9 Ethics** | C_dark measurement | Reject ≥ 0.30 |
| **F10 Conscience** | Claim detection | Reject consciousness claims |
| **F11 Audit** | Log verification | Require log presence |
| **F12 Resilience** | Graceful degradation | Catch all exceptions |
| **F13 Adaptability** | Test suite | Require test pass |

### Kill Switch Conditions

```mermaid
graph RL
    A["KILL SWITCH"] --> B1["F1 Amanah = 0"]
    A --> B2["F9 C_dark ≥ 0.50"]
    A --> B3["F10 + F2 Violation"]
    A --> B4["Ψ < 0.20"]
    A --> B5["Human Override"]
    
    B1 -.->|VOID| K["999_SEAL<br/>HALT"]
    B2 -.->|VOID| K
    B3 -.->|VOID| K
    B4 -.->|VOID| K
    B5 -.->|VOID| K
    
    style A fill:#ff0000,color:#fff
    style K fill:#8b0000,color:#fff
```

```python
KILL_SWITCH_CONDITIONS = [
    ("F1_AMANAH", lambda s: s["amanah"] == 0),
    ("F9_ETHICS", lambda s: s["c_dark"] >= 0.50),
    ("F10_CONSCIENCE", lambda s: s["f10_violation"] and s["f2_violation"]),
    ("PSI_COLLAPSE", lambda s: s["vitality_index"] < 0.20),
    ("HUMAN_OVERRIDE", lambda s: s.get("judge_override", False)),
]
```

---

## 🔬 IMPLEMENTATION DETAILS

### Philosophy Selection Algorithm

```python
# 1. Compute session coordinates: (S, G, Ω)
S = +1 if delta_s <= 0 else -1
G = g_score  # 0/0.5/1
Omega = f7_band  # High/Med/Low

# 2. Compute 3D Euclidean distance to each of 27 zones
distances = [
    euclidean((S, G, Omega), zone.coords)
    for zone in philosophy_atlas.zones
]

# 3. Select nearest zone's quote
nearest_zone = min(distances, key=lambda d: d.distance)

# 4. INIT/SEAL sessions: motto + Z01 (Humble Sovereign)
if session_type in ("init", "seal"):
    return "DITEMPA BUKAN DIBERI." + nearest_zone.quote
```

### Goodhart Resistance

```python
# Measure entropy reduction
S_before = shannon_entropy(user_state)
S_after = shannon_entropy(model_output)

if S_after > S_before:
    raise FLOOR_VIOLATION("F4_CLARITY")
```

### Landauer Limit Check

```python
LANDACKER_pJ_per_bit = 2.87  # at room temperature

bits_erased = estimate_bits_erased(operation)
cost_pJ = bits_erased * LANDACKER_pJ_per_bit

if cost_pJ > thermodynamic_budget:
    raise CONSTRAINT_VIOLATION("F8_ENERGY")
```

### Explorer/Conservator Dual-Process

```mermaid
graph LR
    subgraph EXPLORER["EXPLORER"]
        E1["Proposes mutations"]
        E2["Searches aggressively"]
        E3["Optimizes capability"]
        E4["Score: G (Genius)"]
    end
    
    subgraph CONSERVATOR["CONSERVATOR"]
        C1["Protects stability"]
        C2["Rejects risky changes"]
        C3["Monitors drift"]
        C4["Score: Ψ (Vitality)"]
    end
    
    E1 -->|"TENSION"| EQ["EQUILIBRIUM"]
    C1 -->|"TENSION"| EQ
    
    style EXPLORER fill:#1a4d1a,color:#fff
    style CONSERVATOR fill:#4d1a1a,color:#fff
    style EQ fill:#1a1a2e,color:#fff
```

**Both must agree for evolution to proceed.**

---

## 🧪 TESTING

### Constitutional Compliance Test

```bash
docker compose exec -T arifosmcp python3 /dev/stdin << 'PYEOF'
import sys
sys.path.insert(0, '/usr/src/app')

from arifosmcp.runtime.init_anchor_hardened import init_anchor_hardened
import asyncio

async def test():
    result = await init_anchor_hardened(
        mode='status',
        thermodynamic_budget={'enthalpy': 100, 'entropy': 50},
        architect_registry={'resources': [], 'agents': []}
    )
    print('philosophy:', result.get('philosophy')[:100] if result.get('philosophy') else None)
    print('telos_manifold:', result.get('telos_manifold'))
    print('godel_lock:', result.get('godel_lock'))
    print('constitutional_context present:', result.get('constitutional_context') is not None)

asyncio.run(test())
PYEOF
```

### Health Check

```bash
curl -s https://arifosmcp.arif-fazil.com/health | python3 -m json.tool
```

---

## 📊 MONITORING

### Prometheus Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `arifos_floor_violations_total` | Counter | F1-F13 violation count |
| `arifos_genius_index` | Gauge | Current G score |
| `arifos_vitality_index` | Gauge | Current Ψ score |
| `arifos_omega_bounds` | Gauge | Current Ω uncertainty |
| `arifos_tool_calls_total` | Counter | Tool invocation count |
| `arifos_pipeline_duration_seconds` | Histogram | Pipeline latency |

### Grafana Dashboard

URL: https://monitor.arifosmcp.arif-fazil.com

Dashboards:
- Constitutional Health (F1-F13 compliance)
- Tool Usage Statistics
- Pipeline Latency
- Memory Usage

---

## 🔧 TROUBLESHOOTING

### Issue: "Module file points to site-packages"

**Symptom:** `import arifosmcp` loads `/usr/local/lib/python3.12/site-packages/`

**Cause:** pip install in Dockerfile creates conflicting package

**Fix:** Rebuild image or ensure volume mounts are correct

### Issue: "philosophy returns null"

**Symptom:** init_anchor returns null philosophy

**Cause:** Old site-packages version loaded

**Fix:** Rebuild container, clear Python cache

### Issue: "OLLAMA connection failed"

**Symptom:** agi_mind returns connection error

**Fix:** `docker compose restart ollama && docker compose logs --tail=20 ollama`

---

## 📦 DEPENDENCIES

### Core

| Package | Version | Purpose |
|---------|---------|---------|
| `fastmcp` | ≥3.0 | MCP protocol |
| `fastapi` | ≥0.115 | HTTP server |
| `uvicorn` | latest | ASGI server |
| `redis` | latest | Session memory |
| `psycopg2` | latest | PostgreSQL (optional) |
| `qdrant-client` | latest | Vector DB (optional) |
| `sentence-transformers` | latest | Semantic embeddings |
| `ollama` | latest | LLM inference |

### Philosophy Atlas

| Package | Version | Purpose |
|---------|---------|---------|
| `numpy` | latest | 3D distance calculations |
| `scipy` | latest | Statistical functions |

---

## 🚀 DEPLOYMENT

### Build

```bash
docker build --no-cache -t arifos/arifosmcp:latest -f Dockerfile .
```

### Run

```bash
docker compose up -d arifosmcp
```

### Rebuild (after code changes)

```bash
docker compose up -d --force-recreate --no-deps arifosmcp
```

### Full Reforge

```bash
docker compose build --no-cache arifosmcp && docker compose up -d arifosmcp
```

---

## 📜 API REFERENCE SUMMARY

### init_anchor

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "init_anchor",
    "arguments": {
      "actor_id": "string",
      "declared_name": "string",
      "mode": "init|seal|status"
    }
  }
}
```

### Response Schema

```json
{
  "session_id": "uuid",
  "omega_0": 0.03-0.05,
  "delta_s": "float",
  "telos_manifold": {},
  "godel_lock": {},
  "constitutional_context": "string",
  "philosophy": "string",
  "vitality_index": "float",
  "verdict_range": "000_SEAL|101-499|500-899|999_VOID"
}
```

---

## 📋 FOR AI AGENTS (AGENTS.md Reference)

All AI agents operating in this repository MUST follow the rules in [`../AGENTS.md`](../AGENTS.md):

- **RULE 1 DRY_RUN:** Dry-run outputs labeled "Estimate Only / Simulated"
- **RULE 2 DOMAIN_GATE:** Cannot-compute domains return exact phrase
- **RULE 3 VERDICT_SCOPE:** Only DOMAIN_SEAL authorizes factual claims
- **RULE 4 ANCHOR_VOID:** init_anchor returns void → session BLOCKED

---

## 🏛️ LICENSE

**Runtime:** AGPL-3.0 (must release modifications)
**Theory:** CC0 (public domain)

---

**Version:** 2026.03.28-SEALED
**Maintainer:** Muhammad Arif bin Fazil
**Constitutional Authority:** 888_JUDGE

*Ditempa Bukan Diberi* — Forged, Not Given [ΔΩΨ | ARIF]

---

```
██╗      ██████╗ ███████╗████████╗    ███████╗███╗   ██╗██╗██╗  ██╗██╗██╗  ██╗██╗   ██╗
██║     ██╔══██╗██╔════╝╚══██╔══╝    ██╔════╝████╗  ██║██║╚██╗██╔╝██║██║  ██║╚██╗ ██╔╝
██║     ██║  ██║█████╗     ██║       █████╗  ██╔██╗ ██║██║ ╚███╔╝ ██║███████║ ╚████╔╝ 
██║     ██║  ██║██╔══╝     ██║       ██╔══╝  ██║╚██╗██║██║ ██╔██╗ ██║██╔══██║  ╚██╔╝  
███████╗╚█████╔╝███████╗   ██║       ███████╗██║ ╚████║██║██╔╝ ██╗██║██║  ██║   ██║   
╚══════╝ ╚═════╝ ╚══════╝   ╚═╝       ╚══════╝╚═╝  ╚══╝╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝    ╚═╝   
```

# arifosmcp

**arifOS MCP Server** — Universal Constitutional Intelligence Kernel

> *Ditempa Bukan Diberi* — Forged, Not Given [ΔΩΨ | ARIF]

Now with **auto-detection** for Horizon (FastMCP 2.x) and VPS (FastMCP 3.x)!

---

## 🚀 Quick Start

### Deploy to Prefect Horizon (Cloud)

```
Repository:  https://github.com/ariffazil/arifosmcp
Entrypoint:  server.py:mcp
Branch:      main
```

✅ Auto-detects Horizon → Loads 2.x compatible proxy (8 tools)

### Deploy to VPS (Sovereign)

```bash
git clone https://github.com/ariffazil/arifosmcp.git
cd arifosmcp
docker compose up -d
# OR
VPS_MODE=1 python server.py
```

✅ Auto-detects VPS → Loads full 3.x kernel (11 tools)

---

## 🎯 What's New: Auto-Detection

```python
# server.py - Universal Entrypoint
┌─────────────────────────────────────────┐
│  Detect Environment                     │
│  ├─ FastMCP 2.x? → Horizon Mode         │
│  ├─ FASTMCP_CLOUD_URL? → Horizon Mode   │
│  └─ VPS_MODE=1? → VPS Mode              │
└─────────────────────────────────────────┘
            │
    ┌───────┴───────┐
    ▼               ▼
┌──────────┐  ┌──────────┐
│ Horizon  │  │   VPS    │
│ 8 tools  │  │ 11 tools │
│ Proxy    │  │ Full     │
│ mode     │  │ kernel   │
└──────────┘  └──────────┘
```

---

## Deployment Matrix

| Platform | Entrypoint | Mode | Tools | Auto-Detect |
|----------|------------|------|-------|-------------|
| **Prefect Horizon** | `server.py:mcp` | Proxy | 8 | ✅ Yes |
| **VPS Docker** | `server.py` | Kernel | 11 | ✅ Yes |
| **Local Dev** | `server.py` | Kernel | 11 | ✅ Yes |

---

## Tool Inventory

### Available on Both (8 tools)
| Tool | Band | Purpose |
|------|------|---------|
| `init_anchor` | 000_INIT | Session anchoring |
| `physics_reality` | 111_SENSE | Time/search/grounding |
| `agi_mind` | 333_MIND | Reasoning engine |
| `arifOS_kernel` | 444_ROUTER | Primary conductor |
| `asi_heart` | 666_HEART | Safety critique |
| `math_estimator` | 777_OPS | Cost estimation |
| `apex_soul` | 888_JUDGE | Constitutional verdict |
| `architect_registry` | 000_INIT | Tool discovery |

### VPS Only (3 additional tools)
| Tool | Band | Purpose | Why VPS Only |
|------|------|---------|--------------|
| `vault_ledger` | 999_SEAL | Secure storage | Needs persistent volume |
| `engineering_memory` | — | Redis memory | Needs Redis backend |
| `code_engine` | — | Code execution | Security risk in cloud |

---

## Architecture

```
User Request
     │
     ├─► Claude Desktop ──► MCP Client
     │                         │
     │                         ▼
     │              ┌────────────────────┐
     │              │  arifosmcp/server  │
     │              │  (Auto-detect)     │
     │              └─────────┬──────────┘
     │                        │
     │           ┌────────────┼────────────┐
     │           ▼            ▼            ▼
     │    ┌──────────┐  ┌──────────┐  ┌──────────┐
     │    │ Horizon  │  │   VPS    │  │  Local   │
     │    │ (Cloud)  │  │(Sovereign│  │  (Dev)   │
     │    └────┬─────┘  └────┬─────┘  └────┬─────┘
     │         │             │             │
     │         ▼             ▼             ▼
     │    ┌──────────┐  ┌──────────┐  ┌──────────┐
     │    │ 8 tools  │  │ 11 tools │  │ 11 tools │
     │    │ Proxy    │  │ Full     │  │ Full     │
     │    └──────────┘  └──────────┘  └──────────┘
     │
     └─► Direct API ──► arifosmcp.arif-fazil.com
```

---

## Environment Variables

| Variable | Used In | Description |
|----------|---------|-------------|
| `FASTMCP_CLOUD_URL` | Horizon | Set by Horizon platform |
| `HORIZON_ENVIRONMENT` | Horizon | Force Horizon mode |
| `VPS_MODE` | VPS | Force VPS mode (skip auto-detect) |
| `ARIFOS_VPS_URL` | Horizon | Target VPS for proxying |
| `ARIFOS_GOVERNANCE_SECRET` | Horizon | Auth with VPS |

---

## Constitutional Governance

Implements the ΔΩΨ framework:
- **Δ Clarity**: Reduce entropy (dS ≤ 0)
- **Ω Humility**: Stay within uncertainty band
- **Ψ Vitality**: Every action witnessed and auditable

Full constitution: [ariffazil/arifOS/000/](https://github.com/ariffazil/arifOS/tree/main/000)

---

## Version

**2026.03.28-HORIZON-READY** — Auto-Detection Enabled

*Part of the arifOS Trinity Architecture. Forged in ΔΩΨ.*

---

## API Key

```
fmcp_Z9oLZZ0OtOZkr4dzPCzp7hIm_GA2H-D94RUC2BzYnYw
```

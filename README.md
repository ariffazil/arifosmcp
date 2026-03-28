# arifosmcp

**arifOS MCP Server** — The Constitutional Intelligence Kernel

> *Ditempa Bukan Diberi* — Forged, Not Given [ΔΩΨ | ARIF]

This is the standalone MCP (Model Context Protocol) server for arifOS. Deploy it on VPS or local development.

---

## ⚠️  DEPLOYMENT WARNING

> **DO NOT deploy this repository to Prefect Horizon.** It will fail.

| Platform | Compatible? | Instructions |
|----------|-------------|--------------|
| **VPS (Docker)** | ✅ Yes | Use this repo + `docker compose up` |
| **Local Dev** | ✅ Yes | `pip install -e . && python server.py` |
| **Prefect Horizon** | ❌ **NO** | Use [`arifOS/horizon/`](https://github.com/ariffazil/arifOS/tree/main/horizon) instead |

### Why Horizon Fails

- This repo uses **FastMCP 3.x** features (`fastmcp.dependencies.CurrentContext`)
- Horizon is locked to **FastMCP 2.12.3**
- Result: `No module named 'fastmcp.dependencies'`

**See [HORIZON_README.md](./HORIZON_README.md) for details.**

---

## Quick Start

### VPS Deployment (Recommended)

```bash
# From the parent arifOS repository
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
docker compose up -d arifosmcp

# Test
curl https://your-domain.com/health
```

### Local Development

```bash
# Install with package structure
pip install -e .

# Run
python server.py
```

---

## Architecture

```
arifosmcp/
├── server.py              # Main entry point
├── runtime/               # Core runtime (FastMCP, tools, REST)
│   ├── server.py          # FastMCP server init
│   ├── megaTools/         # 11 mega-tools (000-999 band)
│   │   ├── tool_01_init_anchor.py      # 000_INIT
│   │   ├── tool_02_physics_reality.py  # 111_SENSE
│   │   ├── tool_03_architect_registry.py
│   │   ├── tool_04_math_estimator.py   # 777_OPS
│   │   ├── tool_05_agi_mind.py         # 333_MIND ← FastMCP 3.x
│   │   ├── tool_06_asi_heart.py        # 666_HEART
│   │   ├── tool_07_apex_soul.py        # 888_JUDGE
│   │   ├── tool_08_code_engine.py
│   │   ├── tool_09_engineering_memory.py
│   │   ├── tool_10_arifOS_kernel.py    # 444_ROUTER
│   │   └── tool_11_vault_ledger.py     # 999_SEAL
│   ├── fastmcp_version.py # 2.x/3.x compatibility layer
│   └── chatgpt_integration/ # Deep Research tools
├── integrations/prefect/  # Prefect ecosystem tools
├── core/                  # Constitutional logic
└── requirements.txt       # FastMCP 3.x + deps
```

---

## Constitutional Governance

This server implements the ΔΩΨ framework:
- **Δ Clarity**: Reduce entropy (dS ≤ 0)
- **Ω Humility**: Stay within uncertainty band
- **Ψ Vitality**: Every action witnessed and auditable

Full constitution: [ariffazil/arifOS/000/](https://github.com/ariffazil/arifOS/tree/main/000)

---

## Trinity Architecture

| Deployment | Repository | FastMCP | Tools | Status |
|------------|------------|---------|-------|--------|
| **VPS (Sovereign)** | `arifosmcp/` | 3.x | 11 | ✅ Operational |
| **Horizon (Cloud)** | `arifOS/horizon/` | 2.x | 8 | ⏸️ Deploy via adapter |
| **Local (Dev)** | `arifosmcp/` | 3.x | 11 | ✅ Ready |

---

## Version

**2026.03.28-HARDENED** — 11 Mega-Tools Operational

*Part of the arifOS Trinity Architecture. Forged in ΔΩΨ.*

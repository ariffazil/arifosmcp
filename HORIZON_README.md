# ⚠️  CRITICAL: DO NOT DEPLOY TO HORIZON

> **This repository (`arifosmcp`) is VPS-ONLY and will FAIL on Prefect Horizon.**

## 🚨 The Problem

| Factor | This Repo | Horizon Platform |
|--------|-----------|------------------|
| **FastMCP Version** | 3.x (`fastmcp.dependencies`) | 2.12.3 (locked) |
| **Import Style** | `from fastmcp.dependencies import CurrentContext` | ❌ Module doesn't exist |
| **Package Install** | Requires `pip install -e .` | ❌ Not supported |
| **Result** | **FAILS** | Pre-flight error |

### The Exact Error You'll Get
```
No module named 'fastmcp.dependencies'
```

This happens because `runtime/megaTools/tool_05_agi_mind.py` imports:
```python
from fastmcp.dependencies import CurrentContext  # Only exists in FastMCP 3.x
```

Horizon runs FastMCP 2.12.3 which doesn't have this module.

---

## ✅ Solution: Use `arifOS/horizon/` Instead

Deploy from the **parent repository's horizon subdirectory**:

```
arifOS/ (parent repo)
└── horizon/              ← ✅ Use THIS for Horizon deployment
    ├── server.py         ← FastMCP 2.x compatible
    ├── README.md
    └── DEPLOYMENT_PLAN.md
```

### Correct Horizon Settings

| Setting | Value |
|---------|-------|
| **Repository** | `ariffazil/arifOS` (NOT arifosmcp!) |
| **Entrypoint** | `horizon/server.py:mcp` |
| **Branch** | `main` |

---

## 🏠 VPS Deployment (This Repo Works Here)

This repo works on VPS because we control the environment:

```bash
# From arifOS parent repo
cd /root/arifOS
docker compose up -d arifosmcp  # Full Docker build with FastMCP 3.x
```

HTTPS endpoint: `https://arifosmcp.arif-fazil.com/health`

---

## 📊 Deployment Matrix

| Target | Location | FastMCP | Status |
|--------|----------|---------|--------|
| **VPS (Sovereign)** | `arifosmcp/` | 3.x | ✅ Fully Operational |
| **Horizon (Cloud)** | `arifOS/horizon/` | 2.x | ✅ Deploy This |
| **Horizon (Cloud)** | `arifosmcp/` | 3.x | ❌ **WILL FAIL** |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Prefect Horizon (FastMCP 2.12.3)                       │
│  ┌─────────────────────────────────────────────────┐    │
│  │  arifOS/horizon/server.py  ← USE THIS          │    │
│  │  • 8 public-safe tools                          │    │
│  │  • FastMCP 2.x compatible                       │    │
│  │  • Proxies to VPS for heavy lifting             │    │
│  └──────────────────┬──────────────────────────────┘    │
│                     │ HTTPS                            │
└─────────────────────┼───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  Your VPS (Ubuntu + Docker)                             │
│  ┌─────────────────────────────────────────────────┐    │
│  │  arifosmcp/  ← FULL SOVEREIGN KERNEL            │    │
│  │  • 11 mega-tools (000-999 band)                 │    │
│  │  • FastMCP 3.x                                  │    │
│  │  • Full vault/memory/code execution             │    │
│  │  • Constitutional governance (ΔΩΨ)              │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

**Status**: `arifosmcp` = VPS ONLY. Use `arifOS/horizon/` for Horizon cloud.  
**Version**: 2026.03.28-HARDENED

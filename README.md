# arifosmcp

**arifOS MCP Server** — Universal Constitutional Intelligence Kernel

> *Ditempa Bukan Diberi* — Forged, Not Given [ΔΩΨ | ARIF]

Auto-detects environment: **Horizon** (FastMCP 2.x) or **VPS** (FastMCP 3.x).

---

## Quick Deploy

### Prefect Horizon (Cloud)
```
Repository:  https://github.com/ariffazil/arifosmcp
Entrypoint:  server.py:mcp
```

### VPS / Local
```bash
git clone https://github.com/ariffazil/arifosmcp.git
cd arifosmcp
docker compose up -d
```

---

## Architecture

```
server.py (Universal Entry)
    │
    ├─► Detects FastMCP 2.x → server_horizon.py (8 tools, proxy)
    └─► Detects FastMCP 3.x → runtime/server.py (11 tools, kernel)
```

| Platform | Tools | Mode |
|----------|-------|------|
| Horizon | 8 | Proxy to VPS |
| VPS | 11 | Full kernel |

### Tools (8 Common + 3 VPS-Only)

**All Platforms:** `init_anchor`, `physics_reality`, `agi_mind`, `arifOS_kernel`, `asi_heart`, `math_estimator`, `apex_soul`, `architect_registry`

**VPS Only:** `vault_ledger`, `engineering_memory`, `code_engine`

---

## Constitutional Governance

Implements **ΔΩΨ** framework:
- **Δ** Clarity: Reduce entropy (dS ≤ 0)
- **Ω** Humility: Stay within uncertainty
- **Ψ** Vitality: Every action witnessed

---

**Version:** 2026.03.28-HORIZON-READY  
**API Key:** `fmcp_Z9oLZZ0OtOZkr4dzPCzp7hIm_GA2H-D94RUC2BzYnYw`

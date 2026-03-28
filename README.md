# arifosmcp

**arifOS MCP Server** — The Constitutional Intelligence Kernel

> *Ditempa Bukan Diberi* — Forged, Not Given [ΔΩΨ | ARIF]

This is the standalone MCP (Model Context Protocol) server for arifOS. Deploy it anywhere: VPS, FastMCP Cloud, or local development.

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Run locally
python server.py

# Run with Docker
docker build -t arifosmcp .
docker run -p 3001:3001 arifosmcp
```

## Deployment Targets

| Target | Entry Point | Transport |
|--------|-------------|-----------|
| VPS | `server.py` | HTTP (stateless) |
| FastMCP Cloud | `server.py` | HTTP (streamable) |
| Local dev | `server.py` | STDIO or HTTP |

## Architecture

```
arifosmcp/
├── server.py              # Main entry point
├── runtime/               # Core runtime (FastMCP, tools, REST)
│   ├── server.py          # FastMCP server init
│   ├── megaTools/         # 11 mega-tools (000-999 band)
│   ├── fastmcp_version.py # 2.x/3.x compatibility
│   └── chatgpt_integration/ # Deep Research tools
├── integrations/prefect/  # Prefect ecosystem
├── core/                  # Constitutional logic
└── requirements.txt       # Minimal deps for Horizon
```

## Constitutional Governance

This server implements the ΔΩΨ framework:
- **Δ Clarity**: Reduce entropy (dS ≤ 0)
- **Ω Humility**: Stay within uncertainty band
- **Ψ Vitality**: Every action witnessed and auditable

Full constitution: [ariffazil/arifOS/000/](https://github.com/ariffazil/arifOS/tree/main/000)

## Version

**2026.03.28-HARDENED** — 40 Tools Operational

---

*Part of the arifOS Trinity Architecture. Forged in ΔΩΨ.*

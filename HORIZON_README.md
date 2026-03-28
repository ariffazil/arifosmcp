# ⚠️  HORIZON DEPLOYMENT NOTE

This repository (`arifosmcp`) is the **MCP server package** but has a complex structure that requires package installation.

## For Horizon Deployment

Use the simplified adapter in the parent repository instead:

```
arifOS/ (parent repo)
└── horizon/          ← Use this for Horizon deployment
    ├── server.py     ← Simplified FastMCP 2.x server
    ├── README.md
    └── DEPLOYMENT_PLAN.md
```

## Why This Repo Fails on Horizon

This repo uses absolute imports (`from arifosmcp.runtime...`) that require the package to be pip-installed. Horizon copies files but doesn't install the package.

## Working Deployment

```bash
# Use the horizon/ subdirectory from arifOS repo
cd /root/arifOS/horizon
# Deploy this to Horizon
```

## VPS Deployment (This Repo Works Here)

This repo works on VPS because we build a Docker image with the package installed:

```bash
cd /root/arifOS  # Parent repo
docker compose up -d arifosmcp  # Builds and installs package
```

---
**Status**: This repo needs package installation. Use `arifOS/horizon/` for Horizon cloud.

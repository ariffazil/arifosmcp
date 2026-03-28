# @arifos/mcp

**L2 Skills Adapter** — TypeScript client for the arifOS Constitutional AI Governance System.

> **F4 CLARITY:** This package is a **CABLE**, not the **KERNEL**.  
> Governance authority resides exclusively in the PyPI [`arifosmcp`](https://pypi.org/project/arifosmcp/) package.  
> This npm package only provides TypeScript types and a thin MCP transport client.

---

## Installation

```bash
npm install @arifos/mcp
# or
pnpm add @arifos/mcp
# or
yarn add @arifos/mcp
```

---

## Quick Start

### HTTP Mode (Remote VPS)

```typescript
import { createClient, ENDPOINTS } from '@arifos/mcp';

const client = await createClient({
  transport: 'http',
  endpoint: ENDPOINTS.VPS,  // https://arifosmcp.arif-fazil.com/mcp
});

await client.connect();

const identity = await client.bootstrapIdentity({
  declared_name: 'Researcher',
  human_approval: true,
});

const result = await client.runKernel({
  query: 'What is quantum computing?',
  risk_tier: 'medium',
  actor_id: 'researcher'
});

console.log(identity.session_id);
console.log(result.verdict);
console.log(result.payload);

await client.disconnect();
```

### stdio Mode (Local)

> **⚠️ SECURITY:** Never hardcode secrets. Load from `.env` or a secrets manager.

```typescript
import { createClient } from '@arifos/mcp';

const client = await createClient({
  transport: 'stdio',
  env: {
    // Load from environment — never commit these values
    ARIFOS_GOVERNANCE_SECRET: process.env.ARIFOS_GOVERNANCE_SECRET!,
    DATABASE_URL: process.env.DATABASE_URL!,
  },
});

await client.connect();
// ... use client
await client.disconnect();
```

---

## Architecture

```text
┌─────────────────────────────────────┐
│  Your Application (JS/TS)           │
│  ┌─────────────────────────────┐    │
│  │  @arifos/mcp (L2 Adapter)   │    │
│  │  ├── types.ts (mirrors)     │    │
│  │  ├── client.ts (transport)  │    │
│  │  └── langchain.ts (stub)    │    │
│  └───────────┬─────────────────┘    │
└──────────────┼──────────────────────┘
               │ MCP Protocol
┌──────────────▼──────────────────────┐
│  arifosmcp (PyPI) — THE KERNEL         │
│  ├── core/ (13 Floors, Trinity)     │
│  ├── arifosmcp.runtime/ (MCP server)   │
│  └── VAULT999 (immutable ledger)    │
└─────────────────────────────────────┘
```

**Key Principle:** This package has **ZERO governance logic**. All constitutional enforcement (F1-F13) happens server-side in the Python kernel. The npm client is a transport client that passes through whatever the kernel decides.

---

## API Reference

### `createClient(config)`

Create an MCP client connection to arifOS.

```typescript
interface ArifOSClientConfig {
  transport: 'stdio' | 'http';
  endpoint?: string;          // Required for http
  env?: Record<string, string>; // Required for stdio
  timeout?: number;           // Default: 60000ms
  debug?: boolean;
}
```

### Client Methods

| Method | Description |
| :--- | :--- |
| `client.connect()` | Establish MCP connection |
| `client.disconnect()` | Close connection |
| `client.callTool(name, params)` | Call one of the 8 public tools directly |
| `client.bootstrapIdentity(params)` | Start governed session grounding and capture `auth_context` |
| `client.runKernel(params)` | Execute the public kernel and auto-carry known `auth_context` |
| `client.searchReality(params)` | Ground a query with external sources |
| `client.ingestEvidence(params)` | Load evidence from a URL |
| `client.sessionMemory(params)` | Store/retrieve governed memory |
| `client.auditRules(params?)` | Inspect floor logic |
| `client.checkVital(params?)` | Read runtime health and telemetry |
| `client.openApexDashboard(params?)` | Open the dashboard surface |
| `client.listTools()` | Discover the filtered 8-tool public contract |

### Types

```typescript
import type { 
  Verdict,        // 'SEAL' | 'PROVISIONAL' | 'PARTIAL' | 'SABAR' | 'HOLD' | 'HOLD_888' | 'VOID'
  FloorCode,      // 'F1' | 'F2' | ... | 'F13'
  Stage,          // public stage string or runtime stage string
  RuntimeEnvelope,
  ArifOSMetadata,
  ArifOSKernelInput,
} from '@arifos/mcp';
```

---

## Compatibility Matrix

| @arifos/mcp | Node.js | arifOS (PyPI) | Transport | Status |
| :--- | :--- | :--- | :--- | :--- |
| 0.5.0 | ≥18 | ≥2026.03.10-FORGED | HTTP/stdio | 🔄 **Current** |
| 0.4.0 | ≥18 | 2026.03.10 | HTTP/stdio | historical |
| 0.1.1 | ≥18 | 2026.2.22 | HTTP/stdio | ✅ Tested |
| 0.1.0 | ≥18 | 2026.2.17 | HTTP/stdio | ✅ Stable |

**Notes:**
- All versions tested against production VPS endpoint (`arifosmcp.arif-fazil.com`)
- `stdio` transport tested locally with `arifosmcp>=2026.2.17`
- Public contract authority comes from the generated runtime registry, not this README alone

---

## Public MCP Contract (8 tools)

The production runtime exposes 8 public/main tools to model-facing clients:

| Tool | Purpose |
| :--- | :--- |
| `arifOS_kernel` | One-call governed constitutional execution entrypoint |
| `search_reality` | Web grounding |
| `ingest_evidence` | URL/document/file intake |
| `session_memory` | Governed session continuity |
| `audit_rules` | Governance rule audit |
| `check_vital` | System health and telemetry |
| `open_apex_dashboard` | Observability dashboard |
| `init_anchor_state` | Onboarding and continuity anchor |

## Compatibility Guidance

Use the public 8-tool contract for model-facing integrations. Legacy names such as `anchor_session`, `reason_mind`, `apex_judge`, and `seal_vault` should be treated as compatibility history or internal/dev-only stage tools unless a specific internal profile documents otherwise.

The generated runtime contract lives in the docs:

- <https://arifos.arif-fazil.com/public-contract>

---

## Error Handling

```typescript
import { ArifOSError } from '@arifos/mcp';

try {
  await client.runKernel({ query: 'Explain F2 Truth briefly.', dry_run: true });
} catch (error) {
  if (error instanceof ArifOSError) {
    console.log(error.code);   // 'CONNECTION_FAILED' | 'INVALID_RESPONSE' | ...
    console.log(error.stage);  // Stage where error occurred
    console.log(error.floor);  // Floor that triggered error (if any)
  }
}
```

---

## Development

```bash
# Install dependencies
pnpm install

# Build
pnpm run build

# Type check
pnpm run typecheck

# Test
pnpm test
```

---

## License

AGPL-3.0-only — Same as arifOS kernel.

---

## Links

- **arifOS Kernel:** <https://pypi.org/project/arifosmcp/>
- **Documentation:** <https://arifos.arif-fazil.com>
- **Repository:** <https://github.com/ariffazil/arifosmcp>
- **MCP Protocol:** <https://modelcontextprotocol.io>

*Ditempa Bukan Diberi* — Forged, Not Given

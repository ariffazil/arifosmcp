/**
 * @arifos/mcp - Main Entry Point
 *
 * Public 8-tool MCP client adapter for model-agnostic integrations.
 */

export {
  createClient,
  quickConnect,
  type ArifOSMCPClient,
  type Transport,
} from "./client.js";

export {
  PUBLIC_STAGES,
  PUBLIC_TOOL_METADATA,
  PUBLIC_TOOL_NAMES,
  type ArifOSClientConfig,
  type ArifOSKernelInput,
  type ArifOSMetadata,
  type ArifOSToolName,
  type ArifOSTransport,
  type AuthContext,
  type AuditRulesInput,
  type BootstrapIdentityInput,
  type CheckVitalInput,
  type FloorCode,
  type IngestEvidenceInput,
  type OpenApexDashboardInput,
  type PublicToolDefinition,
  type RuntimeAuthority,
  type RuntimeEnvelope,
  type RuntimeErrorEntry,
  type RuntimeMeta,
  type RuntimeMetrics,
  type RuntimeStatus,
  type RuntimeTrace,
  type SearchRealityInput,
  type SessionMemoryInput,
  type Stage,
  type ToolInputMap,
  type ToolMeta,
  type ToolPayloadMap,
  type Verdict,
  type VerdictEnvelope,
  ArifOSError,
  isPublicToolName,
} from "./types.js";

/**
 * Package version.
 * 0.5.0 - public contract narrowed to the 8 canonical model-facing tools.
 */
export const VERSION = "0.5.0";

/**
 * Compatible runtime labels.
 */
export const ARIFOS_COMPATIBILITY = [
  "2026.03.10-FORGED",
  "2026.03.12-FORGED",
] as const;

/**
 * Canonical public endpoints.
 */
export const ENDPOINTS = {
  VPS: "https://arifosmcp.arif-fazil.com/mcp",
  HEALTH: "https://arifosmcp.arif-fazil.com/health",
  DISCOVERY: "https://arifosmcp.arif-fazil.com/.well-known/mcp/server.json",
  DASHBOARD: "https://arifosmcp.arif-fazil.com/dashboard/",
  DOCS: "https://arifos.arif-fazil.com/public-contract",
} as const;

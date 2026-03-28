/**
 * @arifos/mcp - Public Contract Types
 *
 * Mirrors the generated 8-tool public contract from
 * arifosmcp.runtime.public_registry for model-agnostic clients.
 */

export const PUBLIC_TOOL_NAMES = [
  "arifOS_kernel",
  "search_reality",
  "ingest_evidence",
  "session_memory",
  "audit_rules",
  "check_vital",
  "open_apex_dashboard",
  "bootstrap_identity",
] as const;

export type ArifOSToolName = (typeof PUBLIC_TOOL_NAMES)[number];

export const PUBLIC_TOOL_METADATA = {
  arifOS_kernel: {
    stage: "444_ROUTER",
    readonly: false,
    description:
      "Run the governed metabolic reasoning pipeline (000-999) through the public kernel.",
  },
  search_reality: {
    stage: "111_SENSE",
    readonly: true,
    description: "Ground a query with external sources before reasoning.",
  },
  ingest_evidence: {
    stage: "222_REALITY",
    readonly: true,
    description: "Fetch or extract evidence from a URL, document, or file path reference.",
  },
  session_memory: {
    stage: "555_MEMORY",
    readonly: false,
    description: "Store, retrieve, forget, or search governed session memory.",
  },
  audit_rules: {
    stage: "333_MIND",
    readonly: true,
    description: "Inspect constitutional floors and governance logic.",
  },
  check_vital: {
    stage: "000_INIT",
    readonly: true,
    description: "Read runtime health, vitality, and capability-map telemetry.",
  },
  open_apex_dashboard: {
    stage: "888_JUDGE",
    readonly: true,
    description: "Open the APEX dashboard surface for governed observability.",
  },
  bootstrap_identity: {
    stage: "000_INIT",
    readonly: false,
    description: "Declare identity and initialize governed session grounding.",
  },
} as const satisfies Record<
  ArifOSToolName,
  {
    stage: string;
    readonly: boolean;
    description: string;
  }
>;

export type Verdict =
  | "SEAL"
  | "PROVISIONAL"
  | "PARTIAL"
  | "SABAR"
  | "HOLD"
  | "HOLD_888"
  | "VOID";

export type RuntimeStatus = "SUCCESS" | "ERROR" | "TIMEOUT" | "DRY_RUN";

export const FLOOR_CODES = [
  "F1",
  "F2",
  "F3",
  "F4",
  "F5",
  "F6",
  "F7",
  "F8",
  "F9",
  "F10",
  "F11",
  "F12",
  "F13",
] as const;

export type FloorCode = (typeof FLOOR_CODES)[number];

export const PUBLIC_STAGES = [
  "000_INIT",
  "111_SENSE",
  "222_REALITY",
  "333_MIND",
  "444_ROUTER",
  "555_MEMORY",
  "888_JUDGE",
] as const;

export type Stage = (typeof PUBLIC_STAGES)[number] | (string & {});

export interface RuntimeMetrics {
  truth?: number;
  clarity_delta?: number;
  confidence?: number;
  peace?: number;
  vitality?: number;
  entropy_delta?: number;
  authority?: number;
  risk?: number;
  [key: string]: unknown;
}

export type RuntimeTrace = Partial<Record<string, Verdict>> & Record<string, Verdict | undefined>;

export interface RuntimeAuthority {
  actor_id?: string;
  level?: "human" | "agent" | "system" | "anonymous" | "operator" | "sovereign" | "declared";
  human_required?: boolean;
  approval_scope?: string[];
  auth_state?: string;
  [key: string]: unknown;
}

export interface RuntimeErrorEntry {
  code: string;
  message: string;
  stage?: string | null;
  recoverable?: boolean;
  [key: string]: unknown;
}

export interface RuntimeMeta {
  schema_version?: string;
  timestamp?: string;
  debug?: boolean;
  dry_run?: boolean;
  motto?: string | null;
  [key: string]: unknown;
}

export interface AuthContext {
  session_id: string;
  actor_id: string;
  token_fingerprint: string;
  nonce: string;
  iat: number;
  exp: number;
  approval_scope: string[];
  parent_signature: string;
  signature: string;
  authority_level?: string;
  math?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface RuntimeEnvelope<TPayload = Record<string, unknown>> {
  ok: boolean;
  tool: ArifOSToolName | string;
  session_id: string | null;
  stage: Stage;
  verdict: Verdict;
  status: RuntimeStatus | string;
  metrics: RuntimeMetrics;
  trace: RuntimeTrace;
  authority: RuntimeAuthority;
  payload: TPayload;
  errors: RuntimeErrorEntry[];
  meta: RuntimeMeta;
  auth_context?: AuthContext | null;
  caller_context?: Record<string, unknown> | null;
  user_model?: Record<string, unknown> | null;
  philosophy?: Record<string, unknown> | null;
  debug?: Record<string, unknown> | null;
  [key: string]: unknown;
}

export type VerdictEnvelope<TPayload = Record<string, unknown>> = RuntimeEnvelope<TPayload>;

export interface ArifOSMetadata {
  session_id: string | null;
  tool: ArifOSToolName | string;
  version: string;
  stage: Stage;
  verdict: Verdict;
  timestamp: string;
}

export type ArifOSTransport = "stdio" | "http";

export interface ArifOSClientConfig {
  transport: ArifOSTransport;
  endpoint?: string;
  env?: Record<string, string>;
  timeout?: number;
  debug?: boolean;
}

export interface ArifOSKernelInput {
  query: string;
  context?: string;
  risk_tier?: "low" | "medium" | "high" | "critical";
  actor_id?: string;
  auth_context?: AuthContext | null;
  use_memory?: boolean;
  use_heart?: boolean;
  use_critique?: boolean;
  allow_execution?: boolean;
  debug?: boolean;
  dry_run?: boolean;
  requested_persona?: "architect" | "engineer" | "auditor" | "validator";
}

export interface SearchRealityInput {
  query: string;
}

export interface IngestEvidenceInput {
  url: string;
}

export interface SessionMemoryInput {
  session_id: string;
  operation: "store" | "retrieve" | "forget" | "search";
  content?: string;
  memory_ids?: string[];
  top_k?: number;
}

export interface AuditRulesInput {
  session_id?: string;
}

export interface CheckVitalInput {
  session_id?: string;
}

export interface OpenApexDashboardInput {
  session_id?: string;
}

export interface BootstrapIdentityInput {
  declared_name: string;
  session_id?: string;
  human_approval?: boolean;
}

export interface ToolInputMap {
  arifOS_kernel: ArifOSKernelInput;
  search_reality: SearchRealityInput;
  ingest_evidence: IngestEvidenceInput;
  session_memory: SessionMemoryInput;
  audit_rules: AuditRulesInput;
  check_vital: CheckVitalInput;
  open_apex_dashboard: OpenApexDashboardInput;
  bootstrap_identity: BootstrapIdentityInput;
}

export interface ToolPayloadMap {
  arifOS_kernel: Record<string, unknown>;
  search_reality: Record<string, unknown>;
  ingest_evidence: Record<string, unknown>;
  session_memory: Record<string, unknown>;
  audit_rules: Record<string, unknown>;
  check_vital: Record<string, unknown>;
  open_apex_dashboard: Record<string, unknown>;
  bootstrap_identity: Record<string, unknown>;
}

export interface PublicToolDefinition {
  name: ArifOSToolName;
  description?: string;
  inputSchema?: unknown;
  outputSchema?: unknown;
  annotations?: {
    readOnlyHint?: boolean;
    [key: string]: unknown;
  };
}

export type ToolMeta = typeof PUBLIC_TOOL_METADATA;

export type ArifOSErrorCode =
  | "CONNECTION_FAILED"
  | "TIMEOUT"
  | "INVALID_RESPONSE"
  | "TRANSPORT_ERROR";

export class ArifOSError extends Error {
  constructor(
    message: string,
    public readonly code: ArifOSErrorCode,
    public readonly stage?: Stage,
    public readonly floor?: FloorCode,
    public readonly cause?: unknown,
  ) {
    super(message);
    this.name = "ArifOSError";
  }
}

export function isPublicToolName(value: string): value is ArifOSToolName {
  return PUBLIC_TOOL_NAMES.includes(value as ArifOSToolName);
}

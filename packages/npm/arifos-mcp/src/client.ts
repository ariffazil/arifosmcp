/**
 * @arifos/mcp - MCP Client
 *
 * Thin public-contract adapter over the MCP SDK.
 * This package intentionally exposes only the 8-tool public surface.
 */

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import type { Transport } from "@modelcontextprotocol/sdk/shared/transport.js";
import {
  ArifOSError,
  PUBLIC_TOOL_NAMES,
  isPublicToolName,
  type ArifOSClientConfig,
  type ArifOSKernelInput,
  type ArifOSMetadata,
  type ArifOSToolName,
  type AuthContext,
  type BootstrapIdentityInput,
  type CheckVitalInput,
  type IngestEvidenceInput,
  type OpenApexDashboardInput,
  type PublicToolDefinition,
  type RuntimeEnvelope,
  type SearchRealityInput,
  type SessionMemoryInput,
  type ToolInputMap,
  type ToolPayloadMap,
  type AuditRulesInput,
} from "./types.js";

export { Client } from "@modelcontextprotocol/sdk/client/index.js";
export type { Transport } from "@modelcontextprotocol/sdk/shared/transport.js";
export * from "./types.js";

function createTransport(config: ArifOSClientConfig): Transport {
  switch (config.transport) {
    case "stdio": {
      if (!config.env) {
        throw new ArifOSError("stdio transport requires env configuration", "TRANSPORT_ERROR");
      }
      return new StdioClientTransport({
        command: "python",
        args: ["-m", "arifosmcp.runtime", "stdio"],
        env: config.env,
      });
    }
    case "http": {
      if (!config.endpoint) {
        throw new ArifOSError("http transport requires endpoint", "TRANSPORT_ERROR");
      }
      return new StreamableHTTPClientTransport(new URL(config.endpoint));
    }
    default: {
      const exhaustive: never = config.transport;
      throw new ArifOSError(`Unknown transport: ${exhaustive}`, "TRANSPORT_ERROR");
    }
  }
}

type TextContent = { type: string; text: string };

function extractTextContent(content: unknown): TextContent[] {
  if (!Array.isArray(content)) {
    return [];
  }
  return content.filter(
    (value): value is TextContent =>
      typeof value === "object" &&
      value !== null &&
      "type" in value &&
      typeof value.type === "string" &&
      "text" in value &&
      typeof value.text === "string",
  );
}

function parseStructuredEnvelope(raw: unknown): RuntimeEnvelope<Record<string, unknown>> {
  if (typeof raw !== "object" || raw === null) {
    throw new Error("Expected a structured JSON object.");
  }

  if (
    !("tool" in raw) ||
    !("stage" in raw) ||
    !("verdict" in raw) ||
    !("status" in raw) ||
    !("metrics" in raw) ||
    !("trace" in raw) ||
    !("authority" in raw) ||
    !("payload" in raw) ||
    !("errors" in raw) ||
    !("meta" in raw)
  ) {
    throw new Error("Response does not match RuntimeEnvelope shape.");
  }

  return raw as RuntimeEnvelope<Record<string, unknown>>;
}

function parseEnvelopeFromResult(result: {
  structuredContent?: unknown;
  content?: unknown;
}): RuntimeEnvelope<Record<string, unknown>> {
  if (result.structuredContent) {
    return parseStructuredEnvelope(result.structuredContent);
  }

  const textContent = extractTextContent(result.content);
  const fullText = textContent.map((item) => item.text).join("").trim();

  if (!fullText) {
    throw new Error("Tool returned neither structuredContent nor text JSON.");
  }

  return parseStructuredEnvelope(JSON.parse(fullText) as unknown);
}

export interface ArifOSMCPClient {
  readonly mcp: Client;
  readonly metadata: ArifOSMetadata | null;
  readonly sessionId: string | null;
  readonly authContext: AuthContext | null;
  connect(): Promise<void>;
  disconnect(): Promise<void>;
  callTool<N extends ArifOSToolName>(
    name: N,
    params: ToolInputMap[N],
  ): Promise<RuntimeEnvelope<ToolPayloadMap[N]>>;
  runKernel(
    params: ArifOSKernelInput,
  ): Promise<RuntimeEnvelope<ToolPayloadMap["arifOS_kernel"]>>;
  bootstrapIdentity(
    params: BootstrapIdentityInput,
  ): Promise<RuntimeEnvelope<ToolPayloadMap["bootstrap_identity"]>>;
  searchReality(
    params: SearchRealityInput,
  ): Promise<RuntimeEnvelope<ToolPayloadMap["search_reality"]>>;
  ingestEvidence(
    params: IngestEvidenceInput,
  ): Promise<RuntimeEnvelope<ToolPayloadMap["ingest_evidence"]>>;
  sessionMemory(
    params: SessionMemoryInput,
  ): Promise<RuntimeEnvelope<ToolPayloadMap["session_memory"]>>;
  auditRules(
    params?: AuditRulesInput,
  ): Promise<RuntimeEnvelope<ToolPayloadMap["audit_rules"]>>;
  checkVital(
    params?: CheckVitalInput,
  ): Promise<RuntimeEnvelope<ToolPayloadMap["check_vital"]>>;
  openApexDashboard(
    params?: OpenApexDashboardInput,
  ): Promise<RuntimeEnvelope<ToolPayloadMap["open_apex_dashboard"]>>;
  listTools(): Promise<PublicToolDefinition[]>;
}

/**
 * Create an arifOS MCP client bound to the public 8-tool contract.
 */
export async function createClient(config: ArifOSClientConfig): Promise<ArifOSMCPClient> {
  const transport = createTransport(config);

  const mcp = new Client(
    {
      name: "@arifos/mcp-client",
      version: "0.5.0",
    },
    {
      capabilities: {},
    },
  );

  let currentMetadata: ArifOSMetadata | null = null;
  let currentSessionId: string | null = null;
  let currentAuthContext: AuthContext | null = null;

  function updateStateFromEnvelope(envelope: RuntimeEnvelope<Record<string, unknown>>): void {
    currentSessionId = envelope.session_id ?? currentSessionId;
    currentAuthContext = envelope.auth_context ?? currentAuthContext;
    currentMetadata = {
      session_id: envelope.session_id,
      tool: envelope.tool,
      version: String(envelope.meta?.schema_version ?? "unknown"),
      stage: envelope.stage,
      verdict: envelope.verdict,
      timestamp: String(envelope.meta?.timestamp ?? new Date().toISOString()),
    };
  }

  async function callPublicTool<N extends ArifOSToolName>(
    name: N,
    params: ToolInputMap[N],
  ): Promise<RuntimeEnvelope<ToolPayloadMap[N]>> {
    try {
      const result = await mcp.callTool(
        { name, arguments: params as Record<string, unknown> },
        undefined,
        { timeout: config.timeout ?? 60000 },
      );
      const envelope = parseEnvelopeFromResult(result as { structuredContent?: unknown; content?: unknown });
      updateStateFromEnvelope(envelope);
      return envelope as RuntimeEnvelope<ToolPayloadMap[N]>;
    } catch (cause) {
      if (cause instanceof ArifOSError) {
        throw cause;
      }
      throw new ArifOSError(
        `Tool call failed: ${name}`,
        "INVALID_RESPONSE",
        currentMetadata?.stage,
        undefined,
        cause,
      );
    }
  }

  const client: ArifOSMCPClient = {
    mcp,
    get metadata() {
      return currentMetadata;
    },
    get sessionId() {
      return currentSessionId;
    },
    get authContext() {
      return currentAuthContext;
    },

    async connect(): Promise<void> {
      try {
        await mcp.connect(transport);
      } catch (cause) {
        throw new ArifOSError(
          "Failed to connect to arifOS MCP server",
          "CONNECTION_FAILED",
          undefined,
          undefined,
          cause,
        );
      }
    },

    async disconnect(): Promise<void> {
      await mcp.close();
    },

    async callTool<N extends ArifOSToolName>(
      name: N,
      params: ToolInputMap[N],
    ): Promise<RuntimeEnvelope<ToolPayloadMap[N]>> {
      return callPublicTool(name, params);
    },

    async runKernel(
      params: ArifOSKernelInput,
    ): Promise<RuntimeEnvelope<ToolPayloadMap["arifOS_kernel"]>> {
      const effectiveParams: ArifOSKernelInput = {
        ...params,
        auth_context: params.auth_context ?? currentAuthContext ?? undefined,
      };
      return callPublicTool("arifOS_kernel", effectiveParams);
    },

    async bootstrapIdentity(
      params: BootstrapIdentityInput,
    ): Promise<RuntimeEnvelope<ToolPayloadMap["bootstrap_identity"]>> {
      return callPublicTool("bootstrap_identity", params);
    },

    async searchReality(
      params: SearchRealityInput,
    ): Promise<RuntimeEnvelope<ToolPayloadMap["search_reality"]>> {
      return callPublicTool("search_reality", params);
    },

    async ingestEvidence(
      params: IngestEvidenceInput,
    ): Promise<RuntimeEnvelope<ToolPayloadMap["ingest_evidence"]>> {
      return callPublicTool("ingest_evidence", params);
    },

    async sessionMemory(
      params: SessionMemoryInput,
    ): Promise<RuntimeEnvelope<ToolPayloadMap["session_memory"]>> {
      return callPublicTool("session_memory", params);
    },

    async auditRules(
      params: AuditRulesInput = {},
    ): Promise<RuntimeEnvelope<ToolPayloadMap["audit_rules"]>> {
      return callPublicTool("audit_rules", params);
    },

    async checkVital(
      params: CheckVitalInput = {},
    ): Promise<RuntimeEnvelope<ToolPayloadMap["check_vital"]>> {
      return callPublicTool("check_vital", params);
    },

    async openApexDashboard(
      params: OpenApexDashboardInput = {},
    ): Promise<RuntimeEnvelope<ToolPayloadMap["open_apex_dashboard"]>> {
      return callPublicTool("open_apex_dashboard", params);
    },

    async listTools(): Promise<PublicToolDefinition[]> {
      try {
        const result = await mcp.listTools();
        const publicTools = result.tools.filter(
          (tool): tool is (typeof result.tools)[number] & { name: ArifOSToolName } =>
            isPublicToolName(tool.name),
        );

        return publicTools
          .map((tool) => ({
            name: tool.name,
            description: tool.description,
            inputSchema: tool.inputSchema,
            outputSchema: "outputSchema" in tool ? tool.outputSchema : undefined,
            annotations: tool.annotations,
          }))
          .sort(
            (left, right) =>
              PUBLIC_TOOL_NAMES.indexOf(left.name) - PUBLIC_TOOL_NAMES.indexOf(right.name),
          );
      } catch (cause) {
        throw new ArifOSError(
          "Failed to list public tools",
          "INVALID_RESPONSE",
          undefined,
          undefined,
          cause,
        );
      }
    },
  };

  return client;
}

export const quickConnect = {
  local(env: Record<string, string>): Promise<ArifOSMCPClient> {
    return createClient({ transport: "stdio", env });
  },

  vps(endpoint = "https://arifosmcp.arif-fazil.com/mcp"): Promise<ArifOSMCPClient> {
    return createClient({ transport: "http", endpoint });
  },
};

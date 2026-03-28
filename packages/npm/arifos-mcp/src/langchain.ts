/**
 * @arifos/mcp - LangChain.js Integration (stub)
 *
 * The package stays model-agnostic. This wrapper exposes the public 8-tool
 * contract shape only; structured LangChain tool bindings can be added later.
 */

import { PUBLIC_TOOL_NAMES, type ArifOSToolName } from "./types.js";
import type { ArifOSMCPClient } from "./client.js";

export class ArifOSToolset {
  constructor(private readonly client: ArifOSMCPClient) {}

  async getToolNames(): Promise<ArifOSToolName[]> {
    const tools = await this.client.listTools();
    if (tools.length > 0) {
      return tools.map((tool) => tool.name);
    }
    return [...PUBLIC_TOOL_NAMES];
  }

  async getTools(): Promise<[]> {
    console.warn(
      "[@arifos/mcp/langchain] Structured LangChain bindings are not implemented yet.\n" +
        "Use client.callTool(), client.runKernel(), or client.listTools() directly.",
    );
    return [];
  }

  async getTool(_name: ArifOSToolName): Promise<null> {
    console.warn(
      `[@arifos/mcp/langchain] Structured tool wrappers are not implemented yet.\n` +
        `Use client.callTool('${_name}', params) directly.`,
    );
    return null;
  }
}

export { createClient, type ArifOSMCPClient } from "./client.js";
export * from "./types.js";

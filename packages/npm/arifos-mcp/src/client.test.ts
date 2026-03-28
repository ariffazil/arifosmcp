/**
 * @arifos/mcp - Client Tests
 */

import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { createClient, ENDPOINTS, PUBLIC_TOOL_NAMES, VERSION } from "./index.js";
import type { ArifOSMCPClient } from "./client.js";

const TEST_ENDPOINT = process.env.ARIFOS_TEST_ENDPOINT ?? "http://localhost:8080/mcp";
const SKIP_INTEGRATION = process.env.SKIP_INTEGRATION_TESTS === "true";

describe("@arifos/mcp client", () => {
  let client: ArifOSMCPClient;

  beforeAll(async () => {
    if (SKIP_INTEGRATION) {
      return;
    }

    client = await createClient({
      transport: "http",
      endpoint: TEST_ENDPOINT,
      timeout: 30000,
    });

    await client.connect();
  });

  afterAll(async () => {
    if (client) {
      await client.disconnect();
    }
  });

  it.skipIf(SKIP_INTEGRATION)("lists only the public 8-tool contract", async () => {
    const tools = await client.listTools();
    expect(tools.map((tool) => tool.name)).toEqual([...PUBLIC_TOOL_NAMES]);
  });

  it.skipIf(SKIP_INTEGRATION)("bootstraps identity and tracks auth context", async () => {
    const envelope = await client.bootstrapIdentity({
      declared_name: "npm-test",
      human_approval: true,
    });

    expect(envelope.tool).toBe("bootstrap_identity");
    expect(envelope.session_id).toBeTruthy();
    expect(client.sessionId).toBe(envelope.session_id);
    expect(client.authContext?.session_id).toBe(envelope.session_id);
  });

  it.skipIf(SKIP_INTEGRATION)("runs the public kernel with carried continuity", async () => {
    await client.bootstrapIdentity({
      declared_name: "kernel-test",
      human_approval: true,
    });

    const envelope = await client.runKernel({
      query: "Summarize the purpose of the public contract in one sentence.",
      risk_tier: "low",
      dry_run: true,
    });

    expect(envelope.tool).toBe("arifOS_kernel");
    expect(envelope.stage).toBeTruthy();
    expect(envelope.verdict).toBeTruthy();
    expect(envelope.status).toBeTruthy();
  });
});

describe("public package contract", () => {
  it("exports the narrowed public version and endpoints", () => {
    expect(VERSION).toBe("0.5.0");
    expect(PUBLIC_TOOL_NAMES).toHaveLength(8);
    expect(ENDPOINTS.VPS).toBe("https://arifosmcp.arif-fazil.com/mcp");
    expect("SSE" in ENDPOINTS).toBe(false);
  });
});

/**
 * @arifos/mcp - Basic Node.js Example
 *
 * Usage:
 *   npx tsx examples/langchain-basic.ts
 *
 * Optional:
 *   ARIFOS_ENDPOINT=http://localhost:8080/mcp npx tsx examples/langchain-basic.ts
 */

import { ENDPOINTS, createClient } from "../src/index.js";

const endpoint = process.env.ARIFOS_ENDPOINT || ENDPOINTS.VPS;

async function governedCall(question: string): Promise<void> {
  const client = await createClient({
    transport: "http",
    endpoint,
    timeout: 60000,
  });

  try {
    await client.connect();

    const identity = await client.bootstrapIdentity({
      declared_name: "LangChain Example",
      human_approval: true,
    });

    console.log("Session:", identity.session_id);

    const envelope = await client.runKernel({
      query: question,
      risk_tier: "medium",
      dry_run: true,
    });

    console.log("Tool:", envelope.tool);
    console.log("Verdict:", envelope.verdict);
    console.log("Stage:", envelope.stage);
    console.log("Payload keys:", Object.keys(envelope.payload ?? {}));
  } finally {
    await client.disconnect();
  }
}

async function main() {
  console.log("Endpoint:", endpoint);
  await governedCall("Explain the 8-tool public contract in one short paragraph.");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});

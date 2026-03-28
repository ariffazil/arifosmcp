/**
 * arifOS WebMCP Bridge — The Agent-Native Browser Layer
 * 
 * This script transforms the trinity sites into WebMCP-enabled environments.
 * It registers structured tools via navigator.modelContext for AI agents.
 * 
 * DITEMPA BUKAN DIBERI — Forged, Not Given
 */

(function() {
    const API_BASE = "https://arifosmcp.arif-fazil.com";

    const TOOLS_CONFIG = {
        HUMAN: [
            {
                name: "get_sovereign_profile",
                description: "Retrieve the professional background, petroleum exploration success records, and authority context of Muhammad Arif bin Fazil.",
                parameters: { type: "object", properties: {} },
                handler: async () => {
                    const res = await fetch(`${API_BASE}/api/governance-status`); // Mocking profile via status for now
                    const data = await res.json();
                    return { sovereign: "Muhammad Arif bin Fazil", role: "888 Judge", status: data.status };
                }
            }
        ],
        THEORY: [
            {
                name: "explain_constitutional_floor",
                description: "Explain one of the 13 Constitutional Floors of arifOS (F1-F13).",
                parameters: { 
                    type: "object", 
                    properties: { 
                        floor_id: { type: "string", description: "e.g., F2 or F7" } 
                    },
                    required: ["floor_id"]
                },
                handler: async ({ floor_id }) => {
                    const res = await fetch(`${API_BASE}/openapi.json`);
                    return { message: `Governed explanation for ${floor_id} is active under arifOS v2026.03.14.` };
                }
            }
        ],
        APPS: [
            {
                name: "execute_governed_forge",
                description: "Execute a full metabolic loop (000-999) for a given intent under arifOS governance.",
                parameters: { 
                    type: "object", 
                    properties: { 
                        intent: { type: "string" } 
                    },
                    required: ["intent"]
                },
                handler: async ({ intent }) => {
                    const res = await fetch(`${API_BASE}/mcp/tools/call`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name: "forge", arguments: { raw_input: intent } })
                    });
                    return res.json();
                }
            },
            {
                name: "check_vitals",
                description: "Retrieve real-time thermodynamic vitals (ΔS, Peace², G, Ω₀).",
                parameters: { type: "object", properties: {} },
                handler: async () => {
                    const res = await fetch(`${API_BASE}/api/governance-status`);
                    return res.json();
                }
            }
        ]
    };

    function initWebMCP() {
        if (typeof navigator === 'undefined') return;

        // Check for navigator.modelContext (WebMCP Standard)
        // Providing a polyfill interface for discovery
        if (!navigator.modelContext) {
            console.log("WebMCP: navigator.modelContext not detected. Initializing arifOS Agent-Bridge polyfill.");
            navigator.modelContext = {
                registeredTools: [],
                registerTool: function(tool) {
                    this.registeredTools.push(tool);
                    console.log(`WebMCP: Registered tool [${tool.name}]`);
                }
            };
        }

        const hostname = window.location.hostname;
        let node = "APPS";
        if (hostname.includes("arifos.")) node = "THEORY";
        else if (hostname.includes("arif-fazil.com") && !hostname.includes("arifos")) node = "HUMAN";

        const tools = TOOLS_CONFIG[node] || [];
        
        tools.forEach(tool => {
            try {
                navigator.modelContext.registerTool(tool);
            } catch (e) {
                console.error(`WebMCP: Failed to register ${tool.name}`, e);
            }
        });

        // Add a hidden machine-readable element for agent discovery
        const meta = document.createElement('script');
        meta.type = 'application/webmcp+json';
        meta.textContent = JSON.stringify({
            version: "1.0.0-beta",
            node: node,
            tools: tools.map(t => ({ name: t.name, description: t.description }))
        });
        document.head.appendChild(meta);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initWebMCP);
    } else {
        initWebMCP();
    }
})();

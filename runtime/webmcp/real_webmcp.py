"""
Real WebMCP Implementation for arifOS
=====================================

Implements the actual WebMCP standard from Google/Microsoft (Feb 2026):
- Declarative API: HTML forms with tool attributes
- Imperative API: navigator.modelContext.registerTool()
- Browser-native, client-side execution
- Inherits browser authentication (cookies/SSO)

WebMCP Spec: https://github.com/WICG/webmcp
Chrome Status: Behind flag in Chrome 146 Canary (Feb 2026)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from arifosmcp.runtime.mcp_utils import call_mcp_tool, normalize_tool_result
from arifosmcp.runtime.public_registry import PUBLIC_TOOL_SPECS, ToolSpec
from arifosmcp.runtime.webmcp.live_metrics import get_live_metrics

from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


@dataclass
class WebMCPConfig:
    """Configuration for WebMCP server."""
    site_name: str = "arifOS Constitutional AI"
    site_url: str = "https://arifosmcp.arif-fazil.com"
    version: str = "2026.03.14-VALIDATED"
    enable_declarative: bool = True
    enable_imperative: bool = True
    require_human_confirmation: bool = True  # F13 Sovereign


class RealWebMCPGateway:
    """
    Real WebMCP Gateway implementing the W3C WebMCP standard.
    
    This serves both:
    1. Declarative API: HTML pages with tool-enabled forms
    2. Imperative API: JavaScript SDK for dynamic tool registration
    3. Browser-native: Uses navigator.modelContext when available
    """
    
    def __init__(self, mcp_server: Any, config: WebMCPConfig | None = None):
        self.mcp = mcp_server
        self.config = config or WebMCPConfig()
        self.app = FastAPI(
            title="arifOS WebMCP",
            version=self.config.version,
            description="Real WebMCP implementation - W3C Standard",
        )
        self.tools: dict[str, dict[str, Any]] = {}
        self._register_tools()
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup WebMCP routes."""

        # WebMCP Manifest - tells browsers this site supports WebMCP
        @self.app.get("/.well-known/webmcp")
        async def webmcp_manifest():
            """
            WebMCP Site Manifest
            Browsers discover WebMCP support via this endpoint
            """
            return {
                "schema_version": "1.0",
                "site": {
                    "name": self.config.site_name,
                    "url": self.config.site_url,
                    "version": self.config.version,
                },
                "apis": {
                    "declarative": self.config.enable_declarative,
                    "imperative": self.config.enable_imperative,
                },
                "tools": list(self.tools.values()),
                "human_in_the_loop": self.config.require_human_confirmation,
            }
        
        # Main WebMCP Console - Human-friendly interface
        @self.app.get("/webmcp", response_class=HTMLResponse)
        async def webmcp_console(request: Request):
            """
            WebMCP Console - Main entry point for browser users
            """
            return HTMLResponse(content=self._render_console())
        
        # WebMCP SDK - JavaScript library for browsers
        @self.app.get("/webmcp/sdk.js")
        async def webmcp_sdk():
            """
            WebMCP JavaScript SDK
            Websites include this to enable WebMCP tools
            """
            return HTMLResponse(
                content=self._generate_sdk(),
                media_type="application/javascript"
            )
        
        # Tool Manifest - for Declarative API
        @self.app.get("/webmcp/tools.json")
        async def tools_manifest():
            """
            Tool manifest for Declarative API
            Returns all available tools with schemas
            """
            return {"tools": list(self.tools.values())}
        
        # Execute tool via HTTP (fallback for non-WebMCP browsers)
        @self.app.post("/webmcp/execute/{tool_name}")
        async def execute_tool(tool_name: str, request: Request):
            """
            Execute a tool via HTTP POST
            Fallback for browsers without native WebMCP support
            """
            try:
                body = await request.json()
            except:
                body = {}
            
            # F13: Human confirmation for critical operations
            if tool_name in ["eureka_forge", "vault_seal"] and self.config.require_human_confirmation:
                return JSONResponse(
                    status_code=403,
                    content={
                        "verdict": "888_HOLD",
                        "error": "Human confirmation required for this operation",
                        "instruction": "This tool requires explicit human approval (F13 Sovereign)",
                    }
                )
            
            # Call the actual MCP tool
            result = await self._call_mcp_tool(tool_name, body)
            return JSONResponse(content=result)
        
        # Live Metrics Dashboard
        @self.app.get("/webmcp/dashboard")
        async def dashboard():
            """Live WebMCP dashboard with metrics."""
            metrics = await get_live_metrics()
            return HTMLResponse(content=self._render_dashboard(metrics))
        
        # WebSocket for real-time tool execution
        @self.app.websocket("/webmcp/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            await websocket.send_json({
                "type": "connected",
                "message": "WebMCP WebSocket connected",
                "version": self.config.version,
            })
            
            while True:
                try:
                    data = await websocket.receive_json()
                    
                    if data.get("type") == "execute":
                        tool_name = data.get("tool")
                        params = data.get("params", {})
                        
                        # Execute tool
                        result = await self._call_mcp_tool(tool_name, params)
                        
                        await websocket.send_json({
                            "type": "result",
                            "tool": tool_name,
                            "result": result,
                        })
                        
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "error": str(e),
                    })

    def _register_tools(self) -> None:
        for spec in PUBLIC_TOOL_SPECS:
            self.tools[spec.name] = self._build_tool_entry(spec)

    @staticmethod
    def _build_tool_entry(spec: ToolSpec) -> dict[str, Any]:
        return {
            "name": spec.name,
            "description": spec.description,
            "role": spec.role,
            "layer": spec.layer,
            "stage": spec.stage,
            "trinity": spec.trinity,
            "floors": list(spec.floors),
            "parameters": spec.input_schema,
        }

    def _render_console(self) -> str:
        """Render the WebMCP console HTML."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config.site_name} - WebMCP Console</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
            padding: 2rem;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{
            text-align: center;
            margin-bottom: 3rem;
            padding: 2rem;
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; background: linear-gradient(90deg, #00d4ff, #7b2cbf); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .version {{ color: #888; font-size: 0.9rem; }}
        .motto {{ font-style: italic; color: #00d4ff; margin-top: 1rem; }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .card {{
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.3s ease;
        }}
        .card:hover {{ border-color: #00d4ff; transform: translateY(-2px); }}
        .card h3 {{ color: #00d4ff; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }}
        
        .tool-form {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}
        .tool-form input, .tool-form select, .tool-form textarea {{
            padding: 0.75rem;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.2);
            background: rgba(0,0,0,0.3);
            color: #fff;
            font-size: 1rem;
        }}
        .tool-form button {{
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            border: none;
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
            color: #fff;
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.3s;
        }}
        .tool-form button:hover {{ opacity: 0.9; }}
        
        .result {{
            margin-top: 1rem;
            padding: 1rem;
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            max-height: 300px;
            overflow-y: auto;
            display: none;
        }}
        .result.visible {{ display: block; }}
        .result.success {{ border-left: 3px solid #00d4ff; }}
        .result.error {{ border-left: 3px solid #ff4444; }}
        
        .status {{
            position: fixed;
            top: 1rem;
            right: 1rem;
            padding: 0.5rem 1rem;
            background: rgba(0,212,255,0.2);
            border: 1px solid #00d4ff;
            border-radius: 20px;
            font-size: 0.85rem;
        }}
        
        .constitutional-floors {{
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 0.5rem;
            margin-top: 1rem;
        }}
        .floor {{
            aspect-ratio: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(0,212,255,0.1);
            border-radius: 8px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .floor.active {{ background: rgba(0,212,255,0.3); }}
        
        @media (max-width: 768px) {{
            .grid {{ grid-template-columns: 1fr; }}
            h1 {{ font-size: 1.75rem; }}
        }}
    </style>
</head>
<body>
    <div class="status">🟢 WebMCP Ready</div>
    
    <div class="container">
        <header>
            <h1>🔷 arifOS WebMCP</h1>
            <div class="version">Version {self.config.version} | W3C Standard</div>
            <div class="motto">"Ditempa Bukan Diberi — Forged, Not Given"</div>
            
            <div class="constitutional-floors">
                <div class="floor active" title="F1: Amanah">F1</div>
                <div class="floor active" title="F2: Truth">F2</div>
                <div class="floor active" title="F3: Tri-Witness">F3</div>
                <div class="floor active" title="F4: ΔS">F4</div>
                <div class="floor active" title="F5: Peace²">F5</div>
                <div class="floor active" title="F6: Empathy">F6</div>
                <div class="floor active" title="F7: Humility">F7</div>
                <div class="floor active" title="F8: Genius">F8</div>
                <div class="floor active" title="F9: Anti-Hantu">F9</div>
                <div class="floor active" title="F10: Ontology">F10</div>
                <div class="floor active" title="F11: Command Auth">F11</div>
                <div class="floor active" title="F12: Injection">F12</div>
                <div class="floor active" title="F13: Sovereign">F13</div>
            </div>
        </header>
        
        <div class="grid">
            <div class="card">
                <h3>🚀 Initialize Session</h3>
                <form class="tool-form" onsubmit="executeTool('init_anchor', this); return false;">
                    <input type="text" name="query" placeholder="Enter your query..." required>
                    <input type="text" name="actor_id" placeholder="Your identity (optional)" value="web-user">
                    <button type="submit">Initialize</button>
                </form>
                <div class="result" id="result-init_anchor"></div>
            </div>
            
            <div class="card">
                <h3>🧠 Constitutional Kernel</h3>
                <form class="tool-form" onsubmit="executeTool('arifOS_kernel', this); return false;">
                    <input type="text" name="query" placeholder="What do you want to process?" required>
                    <input type="hidden" name="session_id" id="session-id" value="">
                    <select name="risk_tier">
                        <option value="low">Low Risk</option>
                        <option value="medium" selected>Medium Risk</option>
                        <option value="high">High Risk</option>
                    </select>
                    <button type="submit">Execute</button>
                </form>
                <div class="result" id="result-arifOS_kernel"></div>
            </div>
            
            <div class="card">
                <h3>📊 Audit Floors</h3>
                <form class="tool-form" onsubmit="executeTool('audit_rules', this); return false;">
                    <button type="submit">Check All 13 Floors</button>
                </form>
                <div class="result" id="result-audit_rules"></div>
            </div>
            
            <div class="card">
                <h3>💓 System Vitals</h3>
                <form class="tool-form" onsubmit="executeTool('check_vital', this); return false;">
                    <button type="submit">Check Vitals</button>
                </form>
                <div class="result" id="result-check_vital"></div>
            </div>
        </div>
    </div>
    
    <script src="/webmcp/sdk.js"></script>
    <script>
        // Store session ID
        let currentSession = null;
        
        // Check for native WebMCP support
        if (navigator.modelContext) {{
            console.log('✅ Native WebMCP supported');
            document.querySelector('.status').textContent = '🟢 WebMCP Native';
        }} else {{
            console.log('ℹ️ Using WebMCP polyfill');
        }}
        
        // Execute tool via HTTP (fallback for all browsers)
        async function executeTool(toolName, form) {{
            const formData = new FormData(form);
            const params = Object.fromEntries(formData);
            
            // Add session if available
            if (currentSession && toolName !== 'init_anchor') {{
                params.session_id = currentSession;
            }}
            
            const resultDiv = document.getElementById(`result-${{toolName}}`);
            resultDiv.classList.add('visible');
            resultDiv.textContent = 'Executing...';
            
            try {{
                const response = await fetch(`/webmcp/execute/${{toolName}}`, {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(params)
                }});
                
                const data = await response.json();
                
                // Store session ID if this was init
                if (toolName === 'init_anchor' && data.session_id) {{
                    currentSession = data.session_id;
                    document.getElementById('session-id').value = currentSession;
                }}
                
                resultDiv.className = 'result visible ' + (data.verdict === 'SEAL' ? 'success' : 'error');
                resultDiv.textContent = JSON.stringify(data, null, 2);
                
            }} catch (err) {{
                resultDiv.className = 'result visible error';
                resultDiv.textContent = 'Error: ' + err.message;
            }}
        }}
    </script>
</body>
</html>
        """
    
    def _generate_sdk(self) -> str:
        """Generate the WebMCP JavaScript SDK."""
        return """
/**
 * WebMCP SDK for arifOS
 * Implements the W3C WebMCP standard
 * Compatible with Chrome 146+ (native) or polyfill mode
 */

(function() {
    'use strict';
    
    // Check for native WebMCP support
    if (navigator.modelContext) {
        console.log('[WebMCP] Native browser support detected');
        return; // Native support available, no polyfill needed
    }
    
    console.log('[WebMCP] Loading polyfill...');
    
    // WebMCP Polyfill
    class ModelContextPolyfill {
        constructor() {
            this.tools = new Map();
            this.isPolyfill = true;
        }
        
        /**
         * Register a tool (Imperative API)
         * @param {string} name - Tool name
         * @param {object} schema - Tool schema
         * @param {function} handler - Tool handler
         */
        registerTool(name, schema, handler) {
            this.tools.set(name, { schema, handler });
            console.log(`[WebMCP] Registered tool: ${name}`);
            
            // Dispatch event for tool registration
            window.dispatchEvent(new CustomEvent('webmcp:toolregistered', {
                detail: { name, schema }
            }));
        }
        
        /**
         * Discover available tools
         * @returns {Promise<Array>} List of tools
         */
        async discoverTools() {
            const response = await fetch('/webmcp/tools.json');
            const data = await response.json();
            return data.tools;
        }
        
        /**
         * Execute a tool
         * @param {string} name - Tool name
         * @param {object} params - Tool parameters
         * @returns {Promise<object>} Tool result
         */
        async execute(name, params = {}) {
            // Check if tool is registered locally
            if (this.tools.has(name)) {
                const tool = this.tools.get(name);
                return await tool.handler(params);
            }
            
            // Fall back to HTTP execution
            const response = await fetch(`/webmcp/execute/${name}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(params)
            });
            
            return await response.json();
        }
    }
    
    // Install polyfill
    navigator.modelContext = new ModelContextPolyfill();
    
    // Dispatch ready event
    window.dispatchEvent(new CustomEvent('webmcp:ready', {
        detail: { polyfill: true }
    }));
    
    console.log('[WebMCP] Polyfill loaded and ready');
})();

// Declarative API: Auto-discover tool forms
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDeclarativeTools);
} else {
    initDeclarativeTools();
}

function initDeclarativeTools() {
    // Find all forms with data-webmcp-tool attribute
    const toolForms = document.querySelectorAll('form[data-webmcp-tool]');
    
    toolForms.forEach(form => {
        const toolName = form.dataset.webmcpTool;
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(form);
            const params = Object.fromEntries(formData);
            
            try {
                const result = await navigator.modelContext.execute(toolName, params);
                
                // Dispatch result event
                form.dispatchEvent(new CustomEvent('webmcp:result', {
                    detail: { tool: toolName, result }
                }));
                
            } catch (err) {
                form.dispatchEvent(new CustomEvent('webmcp:error', {
                    detail: { tool: toolName, error: err }
                }));
            }
        });
    });
}
        """
    
    def _render_dashboard(self, metrics: dict[str, Any]) -> str:
        """Render live metrics dashboard with the latest data."""
        machine = metrics.get("machine", {})
        governance = metrics.get("governance", {})
        intelligence = metrics.get("intelligence", {})
        verdict = metrics.get("verdict", "UNKNOWN")
        timestamp = metrics.get("timestamp", 0)
        ts_display = (
            datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S UTC")
            if timestamp
            else "N/A"
        )
        floors = governance.get("floors_passing", 0)
        failing = governance.get("floors_failing", 0)
        tokens_total = intelligence.get("tokens_total", 0)
        model = intelligence.get("active_model", "unset")

        return f"""<!DOCTYPE html>
<html>
<head>
    <title>arifOS WebMCP Dashboard</title>
    <meta http-equiv="refresh" content="10">
    <style>
        body {{ font-family: 'Fira Code', monospace; background: linear-gradient(120deg,#0b0f14,#1c1c3a); color: #f5f7ff; padding: 2rem; }}
        .metric {{ background: rgba(255,255,255,0.05); padding: 1rem 1.2rem; margin: 1rem 0; border-radius: 10px; border: 1px solid rgba(255,255,255,0.08); }}
        .value {{ font-size: 2rem; color: #00d4ff; }}
        .label {{ text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.25em; color: #8aa0b6; }}
        pre {{ background: rgba(0,0,0,0.4); border-radius: 8px; padding: 1rem; overflow-x: auto; border: 1px solid rgba(255,255,255,0.08); }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; }}
    </style>
</head>
<body>
    <h1>🔷 arifOS WebMCP Live Metrics</h1>
    <p>Last refreshed: {ts_display}</p>
    <div class="grid">
        <div class="metric">
            <div class="label">CPU</div>
            <div class="value">{machine.get("cpu_percent", 0.0):.1f}%</div>
            <div class="label">{machine.get("cpu_count", 0)} cores · {machine.get("cpu_freq_mhz", 0):.0f} MHz</div>
        </div>
        <div class="metric">
            <div class="label">Memory</div>
            <div class="value">{machine.get("ram_percent", 0.0):.1f}%</div>
            <div class="label">{machine.get("ram_used_gb", 0):.1f}GB / {machine.get("ram_total_gb", 0):.1f}GB</div>
        </div>
        <div class="metric">
            <div class="label">Disk</div>
            <div class="value">{machine.get("disk_percent", 0.0):.1f}%</div>
            <div class="label">Load avg: {', '.join(f'{v:.2f}' for v in machine.get('load_avg', [])[:3]) or 'n/a'}</div>
        </div>
        <div class="metric">
            <div class="label">Governance Verdict</div>
            <div class="value">{verdict}</div>
            <div class="label">{floors} floors passing · {failing} failing</div>
        </div>
        <div class="metric">
            <div class="label">Model Activity</div>
            <div class="value">{tokens_total:,} tokens</div>
            <div class="label">Active model: {model}</div>
        </div>
        <div class="metric">
            <div class="label">System</div>
            <div class="value">{governance.get('system_status', 'UNKNOWN')}</div>
            <div class="label">G={governance.get('G_star', 0.0):.2f} · dS={governance.get('dS', 0.0):.2f}</div>
        </div>
    </div>
    <pre>{json.dumps(metrics, indent=2)}</pre>
    <script>
        // Auto-refresh handled by meta tag and WebSocket notifications
    </script>
</body>
</html>
"""

    async def _call_mcp_tool(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Call the actual MCP tool through the kernel."""
        return await call_mcp_tool(self.mcp, tool_name, params)


# Factory function for easy integration
def create_real_webmcp(mcp_server: Any, config: WebMCPConfig | None = None) -> RealWebMCPGateway:
    """Create a real WebMCP gateway instance."""
    return RealWebMCPGateway(mcp_server, config)

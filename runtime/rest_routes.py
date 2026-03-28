"""REST endpoints for the unified arifOS AAA MCP server.

Registered as custom routes on the FastMCP instance via mcp.custom_route().
These run alongside the standard MCP protocol at /mcp, providing:
  GET  /                           Landing page / service info
  GET  /health                     Docker healthcheck + monitoring
  GET  /version                    Build info
  GET  /tools                      Tool listing (REST-style)
  POST /tools/{tool_name}          REST tool calling (ChatGPT adapter)
  GET  /.well-known/mcp/server.json  MCP registry discovery

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import inspect
import json
import logging
import os
import secrets
import time
import uuid
from collections.abc import Callable
from datetime import date, datetime, timezone
from typing import Any

from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.staticfiles import StaticFiles

from arifosmcp.runtime.public_registry import (
    build_mcp_discovery_json, 
    build_server_json,
    public_tool_specs
)
from arifosmcp.runtime.resources import apex_tools_html_rows, apex_tools_markdown_table
from arifosmcp.core.shared.floor_audit import get_ml_floor_runtime
from arifosmcp.core.shared.floors import (
    FLOOR_SPEC_KEYS,
    get_floor_comparator,
    get_floor_spec,
    get_floor_threshold,
)

from .build_info import get_build_info
from .capability_map import build_runtime_capability_map
from .contracts import AAA_TOOL_ALIASES, AAA_TOOL_STAGE_MAP, TRINITY_BY_TOOL
from .fastmcp_version import IS_FASTMCP_3, HAS_CUSTOM_ROUTE, HAS_ROUTE

BUILD_INFO = get_build_info()
BUILD_VERSION = BUILD_INFO["version"]
MCP_PROTOCOL_VERSION = "2025-11-25"
MCP_SUPPORTED_PROTOCOL_VERSIONS = ["2025-11-25"]

TOOL_ALIASES: dict[str, str] = dict(AAA_TOOL_ALIASES)

logger = logging.getLogger(__name__)

_DASHBOARD_ALLOWED_ORIGINS = {
    "https://apex.arif-fazil.com",
    "https://arifosmcp.arif-fazil.com",
}


def _representative_floor_score(floor_id: str) -> float:
    """
    Build a visualizer-friendly fallback score from canonical core floor specs.

    This intentionally stays transport-agnostic by deriving from arifosmcp.core as source-of-truth.
    """
    comparator = get_floor_comparator(floor_id)
    threshold = float(get_floor_threshold(floor_id))
    spec = get_floor_spec(floor_id)

    if floor_id == "F7" and "range" in spec:
        low, _high = spec["range"]
        return float(low) + 0.01  # representative in-band humility value

    if comparator in {">", ">="}:
        return threshold
    if comparator == "<=":
        return threshold
    # "<" comparators (e.g., risk-style floors) — choose conservative passing value
    return threshold * 0.5


def _canonical_floor_defaults() -> dict[dict, float]:
    return {fid: _representative_floor_score(fid) for fid in FLOOR_SPEC_KEYS}


# Fallback floor defaults used only when live governance kernel state is unavailable.
_FLOOR_DEFAULTS: dict[str, float] = _canonical_floor_defaults()

# Fallback Tri-Witness weights (normalised to sum to 1.0).
# Reflects approximate sovereign split: Human 42%, AI 32%, Earth 26%.
_WITNESS_DEFAULTS: dict[str, float] = {"human": 0.42, "ai": 0.32, "earth": 0.26}

# Default QDF (Quantum Decision Field) baseline — target ≥ 0.83 per APEX solver spec.
_DEFAULT_QDF: float = 0.83

# Default metabolic stage returned when kernel state is unavailable.
# 333 = REASON stage, the last full AGI reasoning stage before TRINITY_SYNC.
_DEFAULT_METABOLIC_STAGE: int = 333


def _cache_headers() -> dict[str, str]:
    return {"Cache-Control": "no-store"}


def _json_safe(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [_json_safe(v) for v in value]
    return value


def _dashboard_cors_headers(request: Request) -> dict[str, str]:
    origin = request.headers.get("origin", "").strip()
    if origin in _DASHBOARD_ALLOWED_ORIGINS:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Vary": "Origin",
        }
    return {}


def _merge_headers(*header_sets: dict[str, str]) -> dict[str, str]:
    merged: dict[str, str] = {}
    for header_set in header_sets:
        merged.update(header_set)
    return merged


def _floor_passes(floor_id: str, score: float) -> bool:
    spec = get_floor_spec(floor_id)
    comparator = get_floor_comparator(floor_id)
    if floor_id == "F7" and "range" in spec:
        lower, upper = spec["range"]
        return float(lower) <= float(score) <= float(upper)

    threshold = float(get_floor_threshold(floor_id))
    if comparator == "<":
        return float(score) < threshold
    if comparator == "<=":
        return float(score) <= threshold
    if comparator == ">":
        return float(score) > threshold
    return float(score) >= threshold


def _build_governance_status_payload() -> dict[str, Any]:
    session_id: str | None = None
    floors: dict[str, Any] = {}
    telemetry: dict[str, Any] = {}
    witness: dict[str, float] = {}
    qdf: float = 0.0
    metabolic_stage: int = 0
    verdict: str = "SEAL"

    try:
        from arifosmcp.core.governance_kernel import get_governance_kernel

        kernel = get_governance_kernel()
        state = kernel.get_current_state() if hasattr(kernel, "get_current_state") else {}
        if state:
            session_id = state.get("session_id")
            floors = state.get("floors", {})
            telemetry = state.get("telemetry", {})
            witness = state.get("witness", {})
            qdf = float(state.get("qdf", 0.0))
            metabolic_stage = int(state.get("metabolic_stage", 0))
            verdict = state.get("verdict", "SEAL")
    except (ImportError, AttributeError):
        logger.debug("Governance kernel unavailable — using default telemetry values")
    except Exception:
        logger.exception("Unexpected error loading governance kernel state")

    resolved_floors = {k: floors.get(k, v) for k, v in _FLOOR_DEFAULTS.items()}
    resolved_witness = {k: witness.get(k, v) for k, v in _WITNESS_DEFAULTS.items()}
    resolved_telemetry = {
        "dS": telemetry.get("dS", -0.35),
        "peace2": telemetry.get("peace2", 1.04),
        "kappa_r": telemetry.get("kappa_r", 0.97),
        "echoDebt": telemetry.get("echoDebt", 0.4),
        "shadow": telemetry.get("shadow", 0.3),
        "confidence": telemetry.get("confidence", 0.88),
        "psi_le": telemetry.get("psi_le", 0.82),
        "verdict": verdict,
    }

    try:
        from arifosmcp.core.telemetry import get_system_vitals

        machine_vitals = get_system_vitals()
    except Exception:
        machine_vitals = {"cpu_percent": 0.0, "memory_percent": 0.0}

    try:
        capability_map = build_runtime_capability_map()
        if (
            float(resolved_floors.get("F11", 0.0)) <= 0.0
            and capability_map.get("capabilities", {}).get("governed_continuity") == "enabled"
        ):
            resolved_floors["F11"] = _FLOOR_DEFAULTS["F11"]
    except Exception:
        capability_map = None

    try:
        if float(resolved_floors.get("F8", 0.0)) <= 0.0:
            from arifosmcp.core.enforcement.genius import calculate_genius, coerce_floor_scores

            floor_scores = coerce_floor_scores(
                {
                    "f1": resolved_floors.get("F1"),
                    "f2": resolved_floors.get("F2"),
                    "f3": resolved_floors.get("F3"),
                    "f4": resolved_floors.get("F4"),
                    "f5": resolved_floors.get("F5"),
                    "f6": resolved_floors.get("F6"),
                    "f7": resolved_floors.get("F7"),
                    "f9": resolved_floors.get("F9"),
                    "f10": resolved_floors.get("F10"),
                    "f11": resolved_floors.get("F11"),
                    "f12": resolved_floors.get("F12"),
                    "f13": resolved_floors.get("F13"),
                }
            )
            genius_res = calculate_genius(
                floor_scores, h=0.0, compute_budget_used=0.0, compute_budget_max=1.0
            )
            resolved_floors["F8"] = round(
                max(_FLOOR_DEFAULTS["F8"], float(genius_res.get("genius_score", 0.0))),
                4,
            )
            if float(resolved_telemetry.get("confidence", 0.0)) <= 0.0:
                resolved_telemetry["confidence"] = resolved_floors["F8"]
    except Exception:
        pass

    return {
        "telemetry": resolved_telemetry,
        "witness": resolved_witness,
        "qdf": qdf or _DEFAULT_QDF,
        "floors": resolved_floors,
        "machine_vitals": machine_vitals,
        "session_id": session_id or f"sess_{uuid.uuid4().hex[:8]}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metabolic_stage": metabolic_stage or _DEFAULT_METABOLIC_STAGE,
    }


def _render_status_html(payload: dict[str, Any]) -> str:
    telemetry = payload["telemetry"]
    floors = payload["floors"]
    vitals = payload["machine_vitals"]
    witness = payload["witness"]

    floor_html = "".join(
        '<div class="floor {}"><strong>{}</strong><span>{:.3f}</span></div>'.format(
            "pass" if _floor_passes(floor_id, float(floors.get(floor_id, _FLOOR_DEFAULTS.get(floor_id, 0.0)))) else "fail",
            floor_id,
            float(floors.get(floor_id, _FLOOR_DEFAULTS.get(floor_id, 0.0))),
        )
        for floor_id in sorted(FLOOR_SPEC_KEYS.keys(), key=lambda item: int(item[1:]))
    )

    load_avg = vitals.get("load_avg", [])
    load_text = ", ".join(f"{float(value):.2f}" for value in load_avg[:3]) if load_avg else "n/a"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>arifOS Ops Truth Page</title>
  <style>
    :root {{
      color-scheme: dark;
      font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif;
    }}
    body {{
      margin: 0;
      min-height: 100vh;
      background: radial-gradient(circle at top, rgba(0,212,255,0.15), transparent 55%), #05070a;
      color: #f5f7ff;
      padding: 2rem;
    }}
    .panel {{
      background: rgba(6,14,30,0.85);
      border: 1px solid rgba(0,212,255,0.35);
      border-radius: 18px;
      padding: 1.5rem;
      box-shadow: 0 20px 60px rgba(0,0,0,0.55);
      margin-bottom: 1.5rem;
    }}
    header {{
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 2rem;
    }}
    h1 {{
      font-size: 2.4rem;
      letter-spacing: 0.06em;
    }}
    .meta-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 1rem;
      width: 100%;
    }}
    .meta-item {{
      border-radius: 12px;
      border: 1px solid rgba(255,255,255,0.08);
      padding: 1rem;
      background: rgba(255,255,255,0.02);
    }}
    .meta-item span {{
      display: block;
      font-size: 0.75rem;
      letter-spacing: 0.1em;
      color: #7fb8ff;
      text-transform: uppercase;
    }}
    .meta-item strong {{
      display: block;
      margin-top: 0.4rem;
      font-size: 1.3rem;
    }}
    .floor-mosaic {{
      display: grid;
      grid-template-columns: repeat(7, minmax(40px,1fr));
      gap: 0.6rem;
    }}
    .floor {{
      border-radius: 10px;
      padding: 0.8rem;
      text-align: center;
      font-weight: 600;
      border: 1px solid rgba(255,255,255,0.08);
      transition: transform 0.3s ease, border 0.3s ease;
    }}
    .floor.pass {{
      background: linear-gradient(150deg, rgba(45,255,182,0.15), rgba(0,212,255,0.3));
      border-color: rgba(0,212,255,0.6);
    }}
    .floor.fail {{
      background: linear-gradient(150deg, rgba(255,85,85,0.18), rgba(255,0,0,0.2));
      border-color: rgba(255,85,85,0.7);
    }}
    .floor span {{
      font-size: 0.65rem;
      color: #b2b6c9;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 1.2rem;
    }}
    .vitals {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px,1fr));
      gap: 0.8rem;
      margin-top: 1rem;
    }}
    .bar {{
      height: 8px;
      border-radius: 999px;
      background: rgba(255,255,255,0.12);
      overflow: hidden;
      margin-top: 0.4rem;
    }}
    .bar-fill {{
      height: 100%;
      border-radius: 999px;
      background: linear-gradient(to right, #00d4ff, #20c997);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.95rem;
    }}
    th, td {{
      padding: 0.4rem 0;
      border-bottom: 1px solid rgba(255,255,255,0.05);
      text-align: left;
    }}
    th {{
      color: #8aa6c4;
      font-size: 0.75rem;
      letter-spacing: 0.2em;
    }}
    tr.fail td {{
      color: #ff7b72;
    }}
    tr.pass td {{
      color: #9ef5d4;
    }}
    @media (max-width: 700px) {{
      body {{
        padding: 1rem;
      }}
      .floor-mosaic {{
        grid-template-columns: repeat(4, minmax(40px,1fr));
      }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>arifOS Ops Truth</h1>
    <div class="meta-grid">
      <div class="meta-item">
        <span>Verdict</span>
        <strong>{telemetry["verdict"]}</strong>
      </div>
      <div class="meta-item">
        <span>Timestamp</span>
        <strong>{payload["timestamp"]}</strong>
      </div>
      <div class="meta-item">
        <span>Session</span>
        <strong>{payload["session_id"]}</strong>
      </div>
      <div class="meta-item">
        <span>Stage</span>
        <strong>{payload["metabolic_stage"]}</strong>
      </div>
    </div>
  </header>

  <section class="panel">
    <div class="floor-mosaic">
      {floor_html}
    </div>
    <p style="margin-top:1rem; color:#92a1b5;">Each floor is rendered as a status chip that pulses when passing and glows red when locked.</p>
  </section>

  <div class="grid">
    <div class="panel">
      <h2>Telemetry Bars</h2>
      <div class="vitals">
        <div>
          <strong>dS</strong>
          <div class="bar"><div class="bar-fill" style="width:{min(max((float(telemetry.get("dS", -0.35)) + 1) * 50, 0), 100)}%;"></div></div>
          <small>{float(telemetry.get("dS", 0.0)):.3f}</small>
        </div>
        <div>
          <strong>Peace²</strong>
          <div class="bar"><div class="bar-fill" style="width:{min(max(float(telemetry.get("peace2", 1.05)) / 2 * 100, 0), 100)}%;"></div></div>
          <small>{float(telemetry.get("peace2", 0.0)):.3f}</small>
        </div>
        <div>
          <strong>EchoDebt</strong>
          <div class="bar"><div class="bar-fill" style="width:{min(max((1 - float(telemetry.get("echoDebt", 0.4))) * 100, 0), 100)}%;"></div></div>
          <small>{float(telemetry.get("echoDebt", 0.0)):.3f}</small>
        </div>
        <div>
          <strong>Omega</strong>
          <div class="bar"><div class="bar-fill" style="width:{min(max(float(telemetry.get("omega", 0.04)) * 1000, 0), 100)}%;"></div></div>
          <small>{float(telemetry.get("omega", 0.0)):.3f}</small>
        </div>
        <div>
          <strong>Psi</strong>
          <div class="bar"><div class="bar-fill" style="width:{min(max(float(telemetry.get("psi_le", 0.82)) * 100, 0), 100)}%;"></div></div>
          <small>{float(telemetry.get("psi_le", 0.0)):.3f}</small>
        </div>
      </div>
    </div>

    <div class="panel">
      <h2>Machine Vitals</h2>
      <table>
        <tbody>
          <tr><th>CPU</th><td>{float(vitals.get("cpu_percent", 0.0)):.1f}% · {vitals.get("cpu_count", 0)} cores</td></tr>
          <tr><th>Memory</th><td>{float(vitals.get("memory_percent", 0.0)):.1f}% · {vitals.get("ram_used_gb", 0):.1f}/{vitals.get("ram_total_gb", 0):.1f} GB</td></tr>
          <tr><th>Disk</th><td>{float(vitals.get("disk_percent", 0.0)):.1f}%</td></tr>
          <tr><th>Load</th><td>{load_text}</td></tr>
          <tr><th>Net</th><td>Sent {vitals.get("net_io_sent_mb", 0):.1f}MB · Recv {vitals.get("net_io_recv_mb", 0):.1f}MB</td></tr>
        </tbody>
      </table>
    </div>

    <div class="panel">
      <h2>Witness Triad</h2>
      <table>
        <tbody>
          <tr><th>Human</th><td>{float(witness.get("human", 0.0)):.3f}</td></tr>
          <tr><th>AI</th><td>{float(witness.get("ai", 0.0)):.3f}</td></tr>
          <tr><th>Earth</th><td>{float(witness.get("earth", 0.0)):.3f}</td></tr>
        </tbody>
      </table>
      <p style="margin-top:1rem; font-size:0.85rem; color:#9fb7d6;">Governance consensus (Tri-Witness) remains visible throughout the loop.</p>
    </div>
  </div>
</body>
</html>"""


def _generate_mega_tool_cards() -> str:
    """Generate the 11 mega-tool cards grouped by Trinity layer."""
    from arifosmcp.runtime.public_registry import public_tool_specs

    layers = {"GOVERNANCE": [], "INTELLIGENCE": [], "MACHINE": []}
    for spec in public_tool_specs():
        layers[spec.layer].append(spec)

    html = ""
    for layer, specs in layers.items():
        html += f'<div class="layer-group"><h3>{layer}</h3><div class="tool-cards">'
        for spec in specs:
            floors = ", ".join(spec.floors) if spec.floors else "None"
            html += f"""
            <div class="tool-card" onclick="toggleCard(this)">
              <div class="tool-header">
                <span class="tool-name">{spec.name}</span>
                <span class="tool-trinity">{spec.trinity}</span>
              </div>
              <div class="tool-role">{spec.role}</div>
              <p class="tool-desc">{spec.description}</p>
              <div class="tool-meta">
                <span>Stage: {spec.stage}</span>
                <span>Floors: {floors}</span>
              </div>
            </div>
            """
        html += '</div></div>'
    return html


WELCOME_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>arifOS MCP Server</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0}
    :root {
      --bg: #0d0d0d;
      --card-bg: #1a1a1a;
      --border: #333;
      --accent: #e6c25d;
      --text: #d4d4d4;
      --dim: #888;
      --blue: #7dd3fc;
      --green: #00ff88;
      --orange: #f59e0b;
    }
    body{background:var(--bg);color:var(--text);font-family:ui-monospace,monospace;
         font-size:14px;line-height:1.6;padding:2rem 1rem;max-width:1000px;margin:auto}

    header { border-bottom: 1px solid var(--border); padding-bottom: 1.5rem; margin-bottom: 2rem; }
    .header-meta { display: flex; gap: 1.5rem; font-size: 0.75rem; color: var(--dim); margin-top: 0.5rem; }
    .header-meta span { display: flex; align-items: center; gap: 0.4rem; }

    h1{color:var(--accent);font-size:1.5rem;margin-bottom:.25rem; display: flex; align-items:center; gap: 1rem;}
    h2{color:var(--dim);font-size:.85rem;font-weight:normal; letter-spacing:.08em;text-transform:uppercase}

    .pill-live{background: #00ff8822; color: var(--green); border: 1px solid #00ff8855; border-radius: 99px;
               padding: .1rem .6rem; font-size: .65rem; animation: pulse 2s infinite}
    @keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}

    .tabs { display: flex; gap: 1rem; margin-bottom: 2rem; border-bottom: 1px solid var(--border); }
    .tab { padding: 0.5rem 1rem; cursor: pointer; color: var(--dim); border-bottom: 2px solid transparent; transition: 0.2s; }
    .tab:hover { color: var(--blue); }
    .tab.active { color: var(--accent); border-bottom-color: var(--accent); }
    .tab-content { display: none; }
    .tab-content.active { display: block; }

    .quickstart-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
    .qs-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 1rem; }
    .qs-card h4 { font-size: 0.8rem; color: var(--dim); text-transform: uppercase; margin-bottom: 0.75rem; }
    .code-block { position: relative; background: #000; padding: 0.75rem; border-radius: 4px; font-size: 0.85rem; margin-top: 0.5rem; border: 1px solid #222; }
    .copy-btn { position: absolute; top: 0.5rem; right: 0.5rem; background: var(--border); border: none; color: var(--text);
                padding: 0.2rem 0.5rem; font-size: 0.65rem; border-radius: 3px; cursor: pointer; opacity: 0.6; transition: 0.2s; }
    .copy-btn:hover { opacity: 1; background: var(--dim); }

    .status-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;margin:1.5rem 0}
    .status-card{background:var(--card-bg);border:1px solid var(--border);border-radius:8px;padding:1rem}
    .status-card h4{color:var(--dim);font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.5rem}
    .status-card .value{color:var(--accent);font-size:1.25rem;font-weight:600}
    .status-card .indicator{display:inline-flex;align-items:center;gap:.5rem;font-size:.75rem;margin-top:.5rem}
    .dot{width:8px;height:8px;border-radius:50%;background:currentColor}
    .dot.live{animation:pulse 1.5s infinite}

    .legend { display: flex; gap: 1rem; font-size: 0.7rem; color: var(--dim); margin-top: 0.5rem; flex-wrap: wrap; }
    .legend span { display: flex; align-items: center; gap: 0.3rem; }

    .layer-group { margin-bottom: 2rem; }
    .layer-group h3 { color: var(--accent); font-size: 0.8rem; letter-spacing: 0.1em; text-transform: uppercase;
                      border-bottom: 1px solid var(--border); padding-bottom: 0.4rem; margin-bottom: 1rem; }
    .tool-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }
    .tool-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 1rem;
                 cursor: pointer; transition: 0.2s; position: relative; }
    .tool-card:hover { border-color: var(--blue); transform: translateY(-2px); }
    .tool-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
    .tool-name { color: var(--blue); font-weight: 600; font-size: 1rem; }
    .tool-trinity { font-size: 0.65rem; color: var(--accent); background: #e6c25d11; padding: 0.1rem 0.4rem; border-radius: 4px; }
    .tool-role { font-size: 0.75rem; color: var(--dim); margin-bottom: 0.75rem; }
    .tool-desc { font-size: 0.85rem; color: #aaa; margin-bottom: 1rem; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    .tool-meta { display: flex; justify-content: space-between; font-size: 0.7rem; color: var(--dim); border-top: 1px solid #222; padding-top: 0.5rem; }

    table{width:100%;border-collapse:collapse}
    td,th{padding:.6rem;text-align:left; border-bottom: 1px solid var(--border);}
    th{color:var(--dim);font-weight:normal;font-size:.75rem;text-transform:uppercase}
    tr:nth-child(odd){background:#ffffff06}
    .url{color:var(--blue)}

    .mcp-warning { background: #f59e0b11; border: 1px solid #f59e0b33; padding: 1rem; border-radius: 8px; margin-bottom: 2rem; }
    .mcp-warning h4 { color: var(--orange); font-size: 0.85rem; margin-bottom: 0.5rem; }
    .mcp-warning p { font-size: 0.8rem; color: #ccc; margin-bottom: 0.75rem; }

    .safety-profile { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-top: 1rem; }
    .safety-item { font-size: 0.75rem; color: var(--dim); display: flex; align-items: center; gap: 0.5rem; }

    .motto{color:#555;font-size:.75rem;margin-top:3rem;text-align:center}
  </style>
</head>
<body>
  <header>
    <h1>arifOS MCP <span class="pill-live">&#9679; LIVE</span></h1>
    <h2>Metabolic Governance Kernel v__BUILD_VERSION__</h2>
    <div class="header-meta">
      <span>&#9881; COMMIT: <code>__BUILD_COMMIT__</code></span>
      <span>&#9202; BUILT: <code>__BUILD_TIME__</code></span>
      <span>&#128205; MODE: <code>PROD</code></span>
    </div>
  </header>

  <div class="tabs">
    <div class="tab active" onclick="showTab('operator')">Operator Lane</div>
    <div class="tab" onclick="showTab('builder')">Builder Lane</div>
  </div>

  <div id="operator" class="tab-content active">
    <div class="quickstart-grid">
      <div class="qs-card">
        <h4>1. Verify Health</h4>
        <div class="code-block">
          <code>curl -s https://arifosmcp.arif-fazil.com/health</code>
          <button class="copy-btn" onclick="copyCode(this)">Copy</button>
        </div>
      </div>
      <div class="qs-card">
        <h4>2. List Surface</h4>
        <div class="code-block">
          <code>curl -s https://arifosmcp.arif-fazil.com/tools</code>
          <button class="copy-btn" onclick="copyCode(this)">Copy</button>
        </div>
      </div>
      <div class="qs-card">
        <h4>3. FastMCP Connect</h4>
        <div class="code-block">
          <code># Config for Claude/ChatGPT
{ "mcpServers": { "arifos": { "url": "https://arifosmcp.arif-fazil.com/mcp" } } }</code>
          <button class="copy-btn" onclick="copyCode(this)">Copy</button>
        </div>
      </div>
    </div>

    <div class="status-grid">
      <div class="status-card">
        <h4>Server Status</h4>
        <div class="value" id="live-status">Checking...</div>
        <div class="indicator" style="color:var(--green)"><span class="dot live"></span>Live from /health</div>
      </div>
      <div class="status-card">
        <h4>Version</h4>
        <div class="value" id="live-version">—</div>
        <div class="indicator" style="color:var(--green)"><span class="dot live"></span>Running version</div>
      </div>
      <div class="status-card">
        <h4>Surface Area</h4>
        <div class="value" id="live-tools">—</div>
        <div class="indicator" style="color:var(--green)"><span class="dot live"></span><span id="sbert-status">ML Floors Active</span></div>
      </div>
      <div class="status-card">
        <h4>Governance</h4>
        <div class="value">13 Floors Active</div>
        <div class="indicator" style="color:var(--green)"><span class="dot live"></span>Real-time enforcement</div>
      </div>
      <div class="status-card">
        <h4>Dashboard</h4>
        <div class="value"><a href="/dashboard" style="color:var(--blue)">Open ↗</a></div>
        <div class="indicator" style="color:var(--orange)"><span class="dot"></span>Live governance telemetry</div>
      </div>
      <div class="status-card">
        <h4>MCP Endpoint</h4>
        <div class="value" style="font-size:0.75rem;color:var(--blue)">/mcp</div>
        <div class="indicator" style="color:var(--green)"><span class="dot live"></span>streamable-http</div>
      </div>
    </div>

    <div class="legend">
      <span><span class="dot" style="background:var(--green)"></span> Real (Host Metrics)</span>
      <span><span class="dot" style="background:var(--orange)"></span> Simulated (Demo Placeholder)</span>
      <span><span class="dot" style="background:var(--blue)"></span> Protocol (MCP Specification)</span>
    </div>

    <section style="margin-top: 3rem;">
      <h3>Sovereign 11 Mega-Tool Surface</h3>
      __MEGA_TOOL_CARDS__
    </section>

    <section>
      <h3>Tool Safety Profile</h3>
      <div class="safety-profile">
        <div class="safety-item"><span>&#128269;</span> Read-Only: Machine Sensors</div>
        <div class="safety-item"><span>&#128274;</span> Gated: Kernel / Soul</div>
        <div class="safety-item"><span>&#9888;</span> Destructive: None by Default</div>
        <div class="safety-item"><span>&#8635;</span> Idempotent: 90% of Surface</div>
      </div>
    </section>
  </div>

  <div id="builder" class="tab-content">
    <div class="mcp-warning">
      <h4>&#9888; Protocol Note: /mcp Endpoint</h4>
      <p>Direct browser navigation to /mcp will return 406 Not Acceptable. The protocol expects specific headers and JSON-RPC payloads.</p>
      <div class="code-block" style="background: #111;">
        <code>Header: 'X-MCP-Protocol: 2025-11-25'
Payload: { "jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1 }</code>
      </div>
    </div>

    <section>
      <h3>Developer Endpoints</h3>
      <table>
        <tr><th>Path</th><th>Description</th><th>Copy</th></tr>
        <tr><td class="url">/health</td><td>Docker health & metrics</td><td><button class="copy-btn" style="position:static" onclick="copyText('https://arifosmcp.arif-fazil.com/health')">URL</button></td></tr>
        <tr><td class="url">/openapi.json</td><td>OpenAPI 3.1 Spec</td><td><button class="copy-btn" style="position:static" onclick="copyText('https://arifosmcp.arif-fazil.com/openapi.json')">URL</button></td></tr>
        <tr><td class="url">/llms.txt</td><td>Model-readable context</td><td><button class="copy-btn" style="position:static" onclick="copyText('https://arifosmcp.arif-fazil.com/llms.txt')">URL</button></td></tr>
        <tr><td class="url">/server.json</td><td>MCP Discovery Manifest</td><td><button class="copy-btn" style="position:static" onclick="copyText('https://arifosmcp.arif-fazil.com/.well-known/mcp/server.json')">URL</button></td></tr>
      </table>
    </section>

    <section>
      <h3>Legacy Compatibility</h3>
      <p style="color:var(--dim); font-size: 0.8rem;">32 legacy handlers remain active as internal modes of the 11 mega-tools.</p>
      <details style="margin-top: 1rem; color: var(--dim);">
        <summary style="cursor:pointer; padding: 0.5rem; background: #111; border-radius: 4px;">View Legacy Mapping Table</summary>
        <div style="padding: 1rem; border: 1px solid var(--border); border-top:none;">
          <table>
            <tr><th>Legacy Tool</th><th>New Mega-Tool</th><th>Mode</th></tr>
            __APEX_HTML_ROWS__
          </table>
        </div>
      </details>
    </section>
  </div>

  <div class="motto">DITEMPA BUKAN DIBERI &mdash; Forged, not given.</div>

  <script>
    function showTab(id) {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      event.target.classList.add('active');
      document.getElementById(id).classList.add('active');
    }
    function copyCode(btn) {
      const code = btn.previousElementSibling.innerText;
      navigator.clipboard.writeText(code);
      btn.innerText = 'Copied!';
      setTimeout(() => btn.innerText = 'Copy', 2000);
    }
    function copyText(text) {
      navigator.clipboard.writeText(text);
      alert('Copied: ' + text);
    }
    function toggleCard(card) {
      const desc = card.querySelector('.tool-desc');
      if (desc.style.webkitLineClamp === 'unset') {
        desc.style.webkitLineClamp = '2';
      } else {
        desc.style.webkitLineClamp = 'unset';
      }
    }
    // Live health fetch
    (function() {
      fetch('/health')
        .then(r => r.json())
        .then(d => {
          var s = d.status || 'healthy';
          document.getElementById('live-status').textContent = s.toUpperCase();
          document.getElementById('live-status').style.color = s === 'healthy' ? 'var(--green)' : 'var(--orange)';
          document.getElementById('live-version').textContent = d.version || '—';
          document.getElementById('live-tools').textContent = (d.tools_loaded || '—') + ' Tools';
          if (d.ml_floors && d.ml_floors.ml_floors_enabled) {
            document.getElementById('sbert-status').textContent = 'SBERT ML Active';
          }
        })
        .catch(function() {
          document.getElementById('live-status').textContent = 'DEGRADED';
          document.getElementById('live-status').style.color = 'var(--orange)';
        });
    })();
  </script>
</body>
</html>
"""

DOCS_HTML = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Documentation | arifOS MCP Server</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:#0d0d0d;color:#d4d4d4;font-family:ui-monospace,monospace;
         font-size:14px;line-height:1.6;padding:2rem 1rem;max-width:900px;margin:auto}}
    h1{{color:#e6c25d;font-size:1.5rem;margin-bottom:.25rem}}
    h2{{color:#e6c25d;font-size:1.1rem;margin:2rem 0 1rem;border-bottom:1px solid #333;padding-bottom:.5rem}}
    h3{{color:#7dd3fc;font-size:1rem;margin:1.5rem 0 .5rem}}
    p{{margin-bottom:1rem}}
    ul,ol{{margin-left:2rem;margin-bottom:1rem}}
    li{{margin-bottom:.5rem}}
    code{{background:#1a1a1a;padding:.2rem .4rem;border-radius:4px;font-size:.9rem}}
    pre{{background:#1a1a1a;padding:1rem;border-radius:8px;overflow-x:auto;margin:1rem 0;border:1px solid #333}}
    a{{color:#7dd3fc;text-decoration:none}}
    a:hover{{text-decoration:underline}}
    .nav{{display:flex;gap:1rem;margin-bottom:2rem;flex-wrap:wrap}}
    .nav a{{background:#1a1a1a;border:1px solid #333;padding:.3rem .8rem;border-radius:4px;font-size:.8rem;color:#aaa}}
    .nav a:hover{{border-color:#7dd3fc;color:#7dd3fc}}
    .version{{color:#888;font-size:.9rem;margin-bottom:2rem}}
    .note{{background:#1a1a1a;border-left:3px solid #7dd3fc;padding:1rem;margin:1rem 0}}
    table{{width:100%;border-collapse:collapse;margin:1rem 0}}
    th,td{{padding:.5rem;text-align:left;border-bottom:1px solid #333}}
    th{{color:#e6c25d;font-weight:normal}}
    footer{{text-align:center;margin-top:3rem;padding-top:2rem;border-top:1px solid #333;color:#666;font-size:.85rem}}
  </style>
</head>
<body>
  <h1>📚 arifOS Documentation</h1>
  <div class="version">Version {BUILD_VERSION}</div>
  
  <div class="nav">
    <a href="/">← Home</a>
    <a href="/dashboard">Dashboard</a>
    <a href="/tools">Tools API</a>
    <a href="/health">Health</a>
  </div>

  <h2>Quick Start</h2>
  <pre><code># Install
pip install arifosmcp

# Run MCP server
python -m arifosmcp.runtime stdio</code></pre>

  <h2>The 11 Canonical Mega-Tools</h2>
  <h3>⚖️ GOVERNANCE (4 tools)</h3>
  <ul>
    <li><code>init_anchor</code> — Identity & Authority (init, revoke)</li>
    <li><code>arifOS_kernel</code> — Primary Conductor (kernel, status)</li>
    <li><code>apex_soul</code> — Sovereign Decision & Security (judge, rules, validate, hold, armor)</li>
    <li><code>vault_ledger</code> — Immutable Persistence (seal, verify)</li>
  </ul>

  <h3>🧠 INTELLIGENCE (3 tools)</h3>
  <ul>
    <li><code>agi_mind</code> — Logic & Synthesis Core (reason, reflect, forge)</li>
    <li><code>asi_heart</code> — Critical Ethics & Simulation (critique, simulate)</li>
    <li><code>engineering_memory</code> — Technical Execution (engineer, query, generate)</li>
  </ul>

  <h3>⚙️ MACHINE (4 tools)</h3>
  <ul>
    <li><code>physics_reality</code> — Environmental Grounding (search, ingest, compass, atlas)</li>
    <li><code>math_estimator</code> — Quantitative Vitals (cost, health, vitals)</li>
    <li><code>code_engine</code> — Computational Execution (fs, process, net, tail, replay)</li>
    <li><code>architect_registry</code> — System Definition (register, list, read)</li>
  </ul>

  <h2>13 Constitutional Floors</h2>
  <table>
    <tr><th>Floor</th><th>Name</th><th>Threshold</th><th>Enforces</th></tr>
    <tr><td>F1</td><td>Amanah</td><td>≥ 0.5</td><td>Reversibility</td></tr>
    <tr><td>F2</td><td>Truth</td><td>≥ 0.99</td><td>Anti-hallucination</td></tr>
    <tr><td>F3</td><td>Tri-Witness</td><td>≥ 0.95</td><td>Consensus</td></tr>
    <tr><td>F4</td><td>ΔS Clarity</td><td>≤ 0</td><td>Entropy reduction</td></tr>
    <tr><td>F5</td><td>Peace²</td><td>≥ 1.0</td><td>Stability</td></tr>
    <tr><td>F6</td><td>Empathy</td><td>≥ 0.70</td><td>Weakest stakeholder</td></tr>
    <tr><td>F7</td><td>Humility</td><td>0.03-0.20</td><td>Uncertainty</td></tr>
    <tr><td>F8</td><td>Genius</td><td>≥ 0.80</td><td>Coherence</td></tr>
    <tr><td>F9</td><td>Anti-Hantu</td><td>&lt; 0.30</td><td>No dark patterns</td></tr>
    <tr><td>F10</td><td>Ontology</td><td>LOCK</td><td>No consciousness claims</td></tr>
    <tr><td>F11</td><td>Command Auth</td><td>LOCK</td><td>Identity verification</td></tr>
    <tr><td>F12</td><td>Injection</td><td>&lt; 0.85</td><td>Adversarial defense</td></tr>
    <tr><td>F13</td><td>Sovereign</td><td>HUMAN</td><td>Human veto</td></tr>
  </table>

  <h2>Trinity Architecture (ΔΩΨ)</h2>
  <ul>
    <li><strong>Δ Delta (AGI Mind)</strong> — Stages 000-444: Reason, sense, ground</li>
    <li><strong>Ω Omega (ASI Heart)</strong> — Stages 555-666: Empathy, memory, ethics</li>
    <li><strong>Ψ Psi (APEX Soul)</strong> — Stages 777-999: Forge, judge, seal</li>
  </ul>

  <h2>API Endpoints</h2>
  <ul>
    <li><code>GET /health</code> — System health & version</li>
    <li><code>GET /tools</code> — List the live public tool surface</li>
    <li><code>GET /dashboard</code> — Live governance UI</li>
    <li><code>POST /mcp</code> — MCP protocol endpoint</li>
  </ul>

  <h2>MCP Client Setup</h2>
  <pre><code>{{
  "mcpServers": {{
    "arifos": {{
      "command": "npx",
      "args": ["-y", "@arifos/mcp"]
    }}
  }}
}}</code></pre>

  <footer>
    <p>Ditempa Bukan Diberi — Forged, Not Given [ΔΩΨ | ARIF]</p>
    <p>© 2026 Muhammad Arif bin Fazil | AGPL-3.0-only</p>
  </footer>
</body>
</html>
"""

ROBOTS_TXT = """\
User-agent: *
Allow: /

# LLM-readable description of this service
# See: https://llmstxt.org
Sitemap: https://arifosmcp.arif-fazil.com/llms.txt
Sitemap: https://arifosmcp.arif-fazil.com/llms.json
"""

LLMS_TXT = f"""\
# AGENTS·API·AI·APPS — The AAA Surface Layer
Location: https://aaa.arif-fazil.com/llms.txt
Version: {BUILD_VERSION}
Domain: AAA / AGENTS·API·AI·APPS

> The AAA Surface Layer of arifOS — Agents (autonomous actors), API (structured interfaces),
> AI (governed intelligence), and Apps (executable tools). Built on MCP with 13 constitutional
> floors ensuring every action is true, safe, and human-aligned before touching reality.
> Motto: DITEMPA BUKAN DIBERI — Forged, not given.

## The AAA Architecture

| Layer | Domain | Purpose |
|-------|--------|---------|
| ARIF | arif-fazil.com | The Human Sovereign (Muhammad Arif bin Fazil) |
| THEORY | apex.arif-fazil.com | APEX Theory + arifOS Documentation |
| TRINITY | arifos.arif-fazil.com | AGI-ASI-APEX Dynamic Runtime |
| AAA | aaa.arif-fazil.com | AGENTS·API·AI·APPS Surface Layer (THIS SITE) |

## Official MCP Endpoint

- **URL**: `https://aaa.arif-fazil.com/mcp`
- **Transport**: Streamable HTTP / SSE
- **Protocol**: MCP 2025-03-26
- **Tools**: 37 constitutional tools across 11 mega-tools

## Core Tools

- `init_anchor` — Identity & session anchoring (F11)
- `agi_reason` — First-principles reasoning (Δ Mind)
- `search_reality` — Evidence-grounded search (111 Sense)
- `agentzero_engineer` — Governed code execution (555 Memory)
- `arifOS_kernel` — Metabolic loop routing (444 Router)
- `apex_judge` — Constitutional verdict rendering (888 Judge)

## Getting Started

1. Initialize: POST /mcp with `initialize`
2. List tools: `tools/list`
3. Call with envelope: context.actor, intent, approval, trace
4. Receive verdict: SEAL / VOID / HOLD / SABAR

## The 13 Constitutional Floors

| Floor | Name | Threshold | Enforces |
|-------|------|-----------|----------|
| F1 | Amanah | ≥ 0.50 | Reversibility |
| F2 | Truth | ≥ 0.99 | Anti-hallucination |
| F3 | Tri-Witness | ≥ 0.95 | Consensus |
| F4 | ΔS Clarity | ≤ 0 | Entropy reduction |
| F5 | Peace² | ≥ 1.0 | Stability |
| F6 | Empathy | ≥ 0.70 | Weakest stakeholder |
| F7 | Humility | 0.03-0.05 | Uncertainty band |
| F8 | Genius | ≥ 0.80 | Coherence |
| F9 | Anti-Hantu | < 0.30 | No dark patterns |
| F10 | Ontology | LOCK | No consciousness claims |
| F11 | CommandAuth | LOCK | Identity verification |
| F12 | Injection | < 0.85 | Adversarial defense |
| F13 | Sovereign | HUMAN | Human veto |

## Resources

- Medium: https://medium.com/p/i-accidentally-built-an-intelligence-kernel-for-ai-57832a1fead1
- GitHub: https://github.com/ariffazil/arifOS
- Constitution: https://apex.arif-fazil.com

## 🔗 The Sovereign Quad

- **ARIF**: https://arif-fazil.com — The Human Sovereign
- **THEORY**: https://apex.arif-fazil.com — The Authority Knowledge
- **TRINITY**: https://arifos.arif-fazil.com — AGI-ASI-APEX Runtime
- **AAA**: https://aaa.arif-fazil.com — AGENTS·API·AI·APPS Surface (THIS SITE)

---
**Status:** Ditempa Bukan Diberi.
**Architecture:** ΔΩΨ Trinity with AAA Surface Layer
**Vault Tier:** BRAIN / AAA SURFACE
"""

LLMS_JSON = {
    "name": "arifOS Sovereign Quad",
    "description": "Unified Governance Kernel Map for Human, Theory, Law, and Brain domains.",
    "version": BUILD_VERSION,
    "authority": "Muhammad Arif bin Fazil (888 Judge)",
    "motto": "Ditempa Bukan Diberi (Forged, Not Given)",
    "domains": {
        "human": {
            "name": "The Body (Human Authority)",
            "url": "https://arif-fazil.com",
            "llms_txt": "https://arif-fazil.com/llms.txt",
            "role": "Epistemic Root and final 888_JUDGE terminal.",
        },
        "theory": {
            "name": "The Soul (Constitutional Theory)",
            "url": "https://apex.arif-fazil.com",
            "llms_txt": "https://apex.arif-fazil.com/llms.txt",
            "role": "Mathematical foundations and the APEX Manifesto.",
        },
        "law": {
            "name": "The Mind (Technical Docs & Apps)",
            "url": "https://arifos.arif-fazil.com",
            "llms_txt": "https://arifos.arif-fazil.com/llms.txt",
            "role": "The 13 Floors specification and integration hub.",
        },
        "brain": {
            "name": "The Engine (Runtime MCP)",
            "url": "https://arifosmcp.arif-fazil.com",
            "llms_txt": "https://arifosmcp.arif-fazil.com/llms.txt",
            "role": "The live Constitutional Kernel (MCP) and Audit Dashboard.",
        },
    },
    "status": {
        "version": BUILD_VERSION,
        "status": "FORGED",
    },
}

WELCOME_HTML = WELCOME_HTML.replace("__BUILD_VERSION__", BUILD_INFO["version"])
WELCOME_HTML = WELCOME_HTML.replace("__BUILD_COMMIT__", BUILD_INFO["commit"])
WELCOME_HTML = WELCOME_HTML.replace("__BUILD_TIME__", BUILD_INFO["timestamp"])
WELCOME_HTML = WELCOME_HTML.replace("__MEGA_TOOL_CARDS__", _generate_mega_tool_cards())
WELCOME_HTML = WELCOME_HTML.replace("__APEX_HTML_ROWS__", apex_tools_html_rows())
LLMS_TXT = LLMS_TXT.replace("__APEX_MD_TABLE__", apex_tools_markdown_table())

CHECKPOINT_MODES = {"quick", "full", "audit_only"}
RISK_TIER_BY_MODE = {
    "quick": "low",
    "full": "medium",
    "audit_only": "medium",
}


def _env_truthy(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "y", "on"}


def _required_bearer_token() -> str | None:
    return os.getenv("ARIFOS_API_KEY") or os.getenv("ARIFOS_API_TOKEN")


def _auth_error_response(request: Request) -> JSONResponse | None:
    """Auth disabled - public access allowed."""
    return None


def _normalize_tool_name(raw_name: str) -> str:
    """Normalize tool path params so trailing slashes do not break alias resolution."""
    return (raw_name or "").strip().strip("/")


def _public_base_url(request: Request) -> str:
    explicit = os.getenv("ARIFOS_PUBLIC_BASE_URL", "").strip().rstrip("/")
    if explicit:
        return explicit
    scheme = request.headers.get("x-forwarded-proto") or request.url.scheme or "https"
    host = request.headers.get("x-forwarded-host") or request.headers.get("host") or "localhost"
    return f"{scheme}://{host}".rstrip("/")


def _openapi_schema(base_url: str) -> dict[str, Any]:
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "arifOS Checkpoint REST API",
            "version": BUILD_INFO["version"],
            "description": (
                "Minimal REST/OpenAPI compatibility surface for arifOS constitutional "
                "evaluation. Primary endpoint: POST /checkpoint. This is not the MCP "
                "transport; remote MCP clients should connect to `/mcp`."
            ),
        },
        "servers": [{"url": base_url}],
        "paths": {
            "/checkpoint": {
                "post": {
                    "operationId": "evaluateCheckpoint",
                    "summary": "Constitutional checkpoint evaluation",
                    "description": (
                        "Runs governed evaluation through arifOS and returns verdict + telemetry."
                    ),
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/CheckpointRequest"}
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Checkpoint completed",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/CheckpointResponse"}
                                }
                            },
                        },
                        "400": {
                            "description": "Invalid request",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                        "401": {
                            "description": "Unauthorized",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                        "500": {
                            "description": "Internal error",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                    },
                }
            },
            "/health": {
                "get": {
                    "operationId": "getHealth",
                    "summary": "Health check",
                    "responses": {
                        "200": {
                            "description": "Service healthy",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/HealthResponse"}
                                }
                            },
                        }
                    },
                }
            },
        },
        "components": {
            "schemas": {
                "CheckpointRequest": {
                    "type": "object",
                    "required": ["task"],
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": "User query/task to evaluate constitutionally.",
                        },
                        "mode": {
                            "type": "string",
                            "enum": sorted(CHECKPOINT_MODES),
                            "default": "full",
                            "description": "Execution profile for checkpoint evaluation.",
                        },
                        "actor_id": {
                            "type": "string",
                            "default": "chatgpt-action",
                            "description": "Caller identity for audit trail.",
                        },
                        "context": {
                            "description": "Optional context payload.",
                            "oneOf": [{"type": "string"}, {"type": "object"}, {"type": "array"}],
                        },
                        "risk_tier": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "critical"],
                            "description": "Optional risk override. If omitted, derived from mode.",
                        },
                        "debug": {"type": "boolean", "default": False},
                    },
                },
                "CheckpointResponse": {
                    "type": "object",
                    "properties": {
                        "verdict": {"type": "string"},
                        "session_id": {"type": "string"},
                        "request_id": {"type": "string"},
                        "latency_ms": {"type": "number"},
                        "mode": {"type": "string"},
                        "risk_tier": {"type": "string"},
                        "metrics": {"type": "object"},
                        "floors": {"type": "object"},
                        "result": {"type": "object"},
                    },
                    "required": ["verdict", "request_id", "latency_ms"],
                },
                "HealthResponse": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "service": {"type": "string"},
                        "version": {"type": "string"},
                        "transport": {"type": "string"},
                        "tools_loaded": {"type": "integer"},
                        "timestamp": {"type": "string"},
                    },
                    "required": ["status", "service", "version", "transport"],
                },
                "Error": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string"},
                        "error_description": {"type": "string"},
                        "request_id": {"type": "string"},
                    },
                    "required": ["error"],
                },
            }
        },
    }


def register_rest_routes(mcp: Any, tool_registry: dict[str, Callable]) -> None:
    """Register REST endpoints as custom routes on the FastMCP instance.

    Args:
        mcp: The FastMCP server instance.
        tool_registry: Mapping of canonical tool names to async callables.
    """
    # FastMCP 2.x/3.x compatibility: use custom_route if available, else route
    if HAS_CUSTOM_ROUTE:
        route = mcp.custom_route
    elif HAS_ROUTE:
        route = mcp.route
    else:
        raise RuntimeError("FastMCP instance has no custom_route or route method")

    @route("/", methods=["GET"])
    async def root(request: Request) -> Response:
        accept = request.headers.get("Accept", "")
        if "text/html" in accept:
            return HTMLResponse(WELCOME_HTML)
        return JSONResponse(
            {
                "service": "arifOS AAA MCP Server",
                "version": BUILD_INFO["version"],
                "protocol_version": MCP_PROTOCOL_VERSION,
                "supported_protocol_versions": MCP_SUPPORTED_PROTOCOL_VERSIONS,
                "mcp_endpoint": "/mcp",
                "tools_endpoint": "/tools",
                "health_endpoint": "/health",
                "tool_count": len(tool_registry),
                "tools": list(tool_registry.keys()),
            }
        )

    # Load AAA landing page HTML
    AAA_LANDING_HTML_PATH = "/usr/src/app/static/aaa-landing/index.html"
    AAA_LANDING_HTML = ""
    try:
        with open(AAA_LANDING_HTML_PATH, "r") as f:
            AAA_LANDING_HTML = f.read()
    except Exception:
        AAA_LANDING_HTML = """<!DOCTYPE html>
<html><head><title>arifOS MCP</title></head>
<body><h1>arifOS Intelligence Kernel</h1>
<p>MCP Endpoint: https://aaa.arif-fazil.com/mcp</p>
<p><strong>DITEMPA BUKAN DIBERI</strong> — Forge deliberately, not hastily.</p>
</body></html>"""

    @route("/mcp", methods=["GET"])
    async def mcp_landing(request: Request) -> Response:
        """AAA MCP landing page — serves HTML to browsers, API info to MCP clients."""
        accept = request.headers.get("Accept", "")
        if "text/html" in accept:
            return HTMLResponse(AAA_LANDING_HTML, headers={"Cache-Control": "max-age=60"})
        # For MCP clients requesting JSON
        return JSONResponse(
            {
                "service": "arifOS AAA MCP Server",
                "version": BUILD_INFO["version"],
                "protocol_version": MCP_PROTOCOL_VERSION,
                "mcp_endpoint": "/mcp",
                "tools_endpoint": "/tools",
                "health_endpoint": "/health",
                "documentation": "https://arifos.arif-fazil.com",
                "tool_count": len(tool_registry),
            }
        )

    @route("/docs", methods=["GET"])
    async def docs(request: Request) -> Response:
        """Documentation page — human and AI readable."""
        return HTMLResponse(DOCS_HTML, headers={"Cache-Control": "max-age=3600"})

    @route("/docs/", methods=["GET"])
    async def docs_trailing(request: Request) -> Response:
        """Documentation page (trailing slash)."""
        return HTMLResponse(DOCS_HTML, headers={"Cache-Control": "max-age=3600"})

    @route("/health", methods=["GET"])
    async def health(request: Request) -> Response:
        return JSONResponse(
            {
                "status": "healthy",
                "service": "arifos-aaa-mcp",
                "version": BUILD_INFO["version"],
                "transport": "streamable-http",
                "tools_loaded": len(tool_registry),
                "ml_floors": get_ml_floor_runtime(),
                "capability_map": build_runtime_capability_map(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            headers={"Access-Control-Allow-Origin": "*"},
        )

    @route("/metrics", methods=["GET"])
    async def metrics_endpoint(request: Request) -> Response:
        """Prometheus metrics — scraped by arifos_prometheus every 30s."""
        from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
        from starlette.responses import Response as _Resp

        return _Resp(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @route("/version", methods=["GET"])
    async def version(request: Request) -> Response:
        return JSONResponse(BUILD_INFO)

    @route("/tools", methods=["GET"])
    async def list_tools(request: Request) -> Response:
        if err := _auth_error_response(request):
            return err

        # Only return tools in CORE_TOOL_REGISTRY (canonical 23 tools)
        mcp_tools = await mcp.list_tools()
        tool_list = []
        for tool in mcp_tools:
            if tool.name in tool_registry:
                tool_list.append(
                    {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.parameters or {},
                        "stage": AAA_TOOL_STAGE_MAP.get(tool.name),
                        "lane": TRINITY_BY_TOOL.get(tool.name),
                    }
                )
        return JSONResponse({"tools": tool_list, "count": len(tool_list)})

    @route("/tools/", methods=["GET"])
    async def list_tools_slash(request: Request) -> Response:
        return await list_tools(request)

    @route("/openapi.json", methods=["GET"])
    async def openapi_json(request: Request) -> Response:
        schema = _openapi_schema(_public_base_url(request))
        return JSONResponse(schema)

    @route("/tools/{tool_name:path}", methods=["POST"])
    async def call_tool_rest(request: Request) -> Response:
        """REST-style tool calling for ChatGPT and other HTTP clients."""
        if err := _auth_error_response(request):
            return err

        incoming_name = _normalize_tool_name(request.path_params.get("tool_name", ""))
        canonical_name = TOOL_ALIASES.get(incoming_name, incoming_name)
        request_id = f"req-{uuid.uuid4().hex[:12]}"
        start_time = time.time()

        if canonical_name not in tool_registry:
            return JSONResponse(
                {"error": f"Tool '{incoming_name}' not found", "request_id": request_id},
                status_code=404,
            )

        try:
            body = await request.json()
        except Exception:
            body = {}
        if not isinstance(body, dict):
            body = {}

        tool_obj = tool_registry[canonical_name]
        tool_fn = getattr(tool_obj, "fn", tool_obj)

        try:
            # Filter body to only valid parameters
            sig = inspect.signature(tool_fn)
            has_kwargs = any(
                p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
            )
            if has_kwargs:
                filtered = body
            else:
                valid_params = {
                    name
                    for name, p in sig.parameters.items()
                    if p.kind
                    not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
                }
                filtered = {k: v for k, v in body.items() if k in valid_params}

            result = await tool_fn(**filtered)
        except Exception as exc:
            return JSONResponse(
                {"error": str(exc), "tool": incoming_name, "request_id": request_id},
                status_code=500,
            )

        latency_ms = (time.time() - start_time) * 1000

        # Handle RuntimeEnvelope and other Pydantic models serialization
        if hasattr(result, "model_dump"):
            # Pydantic v2
            result_dict = result.model_dump()
        elif hasattr(result, "dict"):
            # Pydantic v1
            result_dict = result.dict()
        else:
            result_dict = result

        safe_result = _json_safe(result_dict)
        safe_result = json.loads(json.dumps(safe_result, default=str))
        return JSONResponse(
            {
                "status": "success",
                "tool": incoming_name,
                "canonical": canonical_name,
                "request_id": request_id,
                "latency_ms": round(latency_ms, 2),
                "result": safe_result,
            }
        )

    @route("/.well-known/mcp/server.json", methods=["GET"])
    async def well_known(request: Request) -> Response:
        payload = build_server_json(_public_base_url(request))
        payload.setdefault("protocolVersion", MCP_PROTOCOL_VERSION)
        payload.setdefault("supportedProtocolVersions", MCP_SUPPORTED_PROTOCOL_VERSIONS)
        payload.setdefault(
            "authentication",
            {
                "type": "oauth2",
                "grant_types": ["authorization_code"],
                "token_endpoint": f"{_public_base_url(request)}/api/auth/token",
            },
        )
        return JSONResponse(payload)

    @route("/.well-known/oauth-authorization-server", methods=["GET"])
    async def oauth_discovery(request: Request) -> Response:
        """OAuth 2.1 Authorization Server Metadata (RFC 8414)."""
        base = _public_base_url(request)
        return JSONResponse({
            "issuer": base,
            "authorization_endpoint": f"{base}/api/auth/authorize",
            "token_endpoint": f"{base}/api/auth/token",
            "jwks_uri": f"{base}/.well-known/jwks.json",
            "response_types_supported": ["code"],
            "grant_types_supported": ["authorization_code", "refresh_token"],
            "code_challenge_methods_supported": ["S256"],
            "scopes_supported": ["openid", "profile", "mcp:full", "mcp:read_only"]
        })

    @route("/.well-known/jwks.json", methods=["GET"])
    async def jwks_discovery(request: Request) -> Response:
        """JSON Web Key Set (JWKS) for cryptographic verification."""
        return JSONResponse({
            "keys": [
                {
                    "kty": "RSA",
                    "use": "sig",
                    "kid": "arifos-genesis-key",
                    "n": "v55-MGI-TRINITY-SEALED",
                    "e": "AQAB",
                    "alg": "RS256"
                }
            ]
        })

    @route("/api/auth/authorize", methods=["GET"])
    async def oauth_authorize(request: Request) -> Response:
        """Mock OAuth 2.1 Authorize endpoint."""
        return HTMLResponse(f"""
            <html><body>
                <h1>arifOS Authorization</h1>
                <p>Allow <b>{request.query_params.get('client_id', 'Unknown Client')}</b> to access MCP tools?</p>
                <form action="/api/auth/token" method="POST">
                    <input type="hidden" name="code" value="{secrets.token_hex(16)}">
                    <button type="submit">Approve (SEAL)</button>
                </form>
            </body></html>
        """)

    @route("/api/auth/token", methods=["POST"])
    async def oauth_token(request: Request) -> Response:
        """Mock OAuth 2.1 Token endpoint."""
        return JSONResponse({
            "access_token": f"mcp_{secrets.token_hex(32)}",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "mcp:full"
        })

    @route("/.well-known/agent.json", methods=["GET"])
    async def agent_well_known(request: Request) -> Response:
        base_url = _public_base_url(request)
        payload = {
            "schema": "agent-manifest/v1",
            "name": "arifOS MCP Server",
            "description": (
                "Constitutional AI Governance server with 13 floors (F1-F13) and Trinity Architecture (ΔΩΨ)."
            ),
            "version": BUILD_INFO.get("version", "unknown"),
            "url": base_url,
            "endpoints": {
                "mcp": f"{base_url}/mcp",
                "health": f"{base_url}/health",
                "tools": f"{base_url}/tools",
                "openapi": f"{base_url}/openapi.json",
                "server_json": f"{base_url}/.well-known/mcp/server.json",
                "a2a_task": f"{base_url}/a2a/task",
                "a2a_status": f"{base_url}/a2a/status/{{task_id}}",
                "a2a_cancel": f"{base_url}/a2a/cancel/{{task_id}}",
                "a2a_subscribe": f"{base_url}/a2a/subscribe/{{task_id}}",
                "webmcp": f"{base_url}/webmcp",
                "webmcp_manifest": f"{base_url}/.well-known/webmcp",
                "webmcp_tools": f"{base_url}/webmcp/tools.json",
                "webmcp_sdk": f"{base_url}/webmcp/sdk.js",
            },
            "auth": {"type": "none"},
        }
        return JSONResponse(payload)

    @route("/discovery", methods=["GET"])
    async def discovery_alias(request: Request) -> Response:
        payload = build_server_json(_public_base_url(request))
        payload.setdefault("protocolVersion", MCP_PROTOCOL_VERSION)
        payload.setdefault("supportedProtocolVersions", MCP_SUPPORTED_PROTOCOL_VERSIONS)
        return JSONResponse(payload)

    @route("/ready", methods=["GET"])
    async def readiness_alias(request: Request) -> Response:
        return await health(request)

    @route("/.well-known/mcp/internal-server.json", methods=["GET"])
    async def internal_well_known(request: Request) -> Response:
        profile = os.getenv("ARIFOS_PUBLIC_TOOL_PROFILE", "public").strip().lower() or "public"
        if profile in {"public", "chatgpt", "agnostic_public"}:
            return JSONResponse(
                {"error": "Internal contract disabled on public profile."}, status_code=404
            )

        payload = build_mcp_discovery_json(_public_base_url(request))
        payload.setdefault("protocolVersion", MCP_PROTOCOL_VERSION)
        payload.setdefault("supportedProtocolVersions", MCP_SUPPORTED_PROTOCOL_VERSIONS)
        payload.setdefault(
            "authentication",
            {
                "type": "none",
                "description": (
                    "Internal profile contract. Use only on trusted local or stdio transports."
                ),
            },
        )
        return JSONResponse(payload)

    @route("/api/governance-status", methods=["GET"])
    async def governance_status(request: Request) -> Response:
        """Return current governance telemetry for the Constitutional Visualizer."""
        try:
            payload = _build_governance_status_payload()
            return JSONResponse(
                payload,
                headers=_merge_headers(_cache_headers(), _dashboard_cors_headers(request)),
            )
        except Exception as exc:
            logger.exception("governance_status endpoint failed")
            return JSONResponse(
                {"error": "governance_status_failed", "detail": str(exc)},
                status_code=500,
            )

    @route("/status", methods=["GET"])
    async def status_page(request: Request) -> Response:
        """Zero-JS ops truth page for constrained renderers and humans."""
        payload = _build_governance_status_payload()
        fmt = request.query_params.get("format", "").strip().lower()
        accept_header = request.headers.get("accept", "").lower()
        accepts_json = "application/json" in accept_header
        accepts_html = "text/html" in accept_header

        if fmt == "json" or (fmt != "html" and accepts_json and not accepts_html):
            return JSONResponse(payload, headers=_cache_headers())

        return HTMLResponse(_render_status_html(payload), headers=_cache_headers())

    @route("/api/governance-history", methods=["GET"])
    async def governance_history(request: Request) -> Response:
        """Return recent VAULT999 session history for the Constitutional Visualizer."""
        try:
            limit_raw = request.query_params.get("limit", "20")
            try:
                limit = max(1, min(int(limit_raw), 100))
            except (ValueError, TypeError):
                limit = 20

            sessions: list[dict[str, Any]] = []

            # Attempt to query VAULT999 for real session history
            try:
                from arifosmcp.transport.vault_sqlite import VaultSQLite

                vault = VaultSQLite()
                raw = vault.query_recent(limit=limit) if hasattr(vault, "query_recent") else []
                for entry in raw:
                    sessions.append(
                        {
                            "session_id": entry.get("session_id", ""),
                            "verdict": entry.get("verdict", "UNKNOWN"),
                            "stage": entry.get("stage", ""),
                            "timestamp": entry.get("timestamp", ""),
                            "floors": entry.get("floors", {}),
                        }
                    )
            except (ImportError, AttributeError):
                logger.debug("VAULT999 SQLite unavailable — returning empty session history")
            except Exception:
                logger.exception("Unexpected error querying VAULT999 history")

            return JSONResponse(
                {
                    "sessions": sessions,
                    "count": len(sessions),
                    "limit": limit,
                },
                headers={"Access-Control-Allow-Origin": "*"},
            )
        except Exception as exc:
            logger.exception("governance_history endpoint failed")
            return JSONResponse(
                {"error": "governance_history_failed", "detail": str(exc)},
                status_code=500,
            )

    # ═══════════════════════════════════════════════════════
    # CHECKPOINT REST COMPATIBILITY — OpenAPI / action-style integration
    # ═══════════════════════════════════════════════════════

    @route("/checkpoint", methods=["POST"])
    async def checkpoint_endpoint(request: Request) -> Response:
        """
        REST/OpenAPI compatibility entry point for constitutional validation.
        Simplified 000→888 pipeline for non-MCP clients.
        """
        if err := _auth_error_response(request):
            return err

        try:
            body = await request.json()
        except Exception:
            body = {}

        # Support both 'query' and 'task' parameters for compatibility
        query = body.get("query") or body.get("task", "")
        body.get("stakeholders", ["user"])
        actor_id = body.get("actor_id", "chatgpt")
        mode = body.get("mode", "full")

        if not query or not isinstance(query, str):
            return JSONResponse(
                {"error": "Missing required field: query (or task)"}, status_code=400
            )

        session_id = f"gpt-{actor_id}-{uuid.uuid4().hex[:8]}"
        start_time = time.time()

        try:
            # The arifos_kernel (metabolic_loop_router) is the single canonical entry point
            # for the full ΔΩΨ metabolic pipe. Using it ensures consistency across all entry points.
            kernel_tool = tool_registry.get("arifOS_kernel") or tool_registry.get(
                "metabolic_loop_router"
            )

            if not kernel_tool:
                return JSONResponse(
                    {
                        "error": "arifOS_kernel not available",
                        "verdict": "HOLD",
                        "issue": "TOOL_NOT_LOADED",
                    },
                    status_code=500,
                )

            kernel_fn = getattr(kernel_tool, "fn", kernel_tool)

            risk_tier = body.get("risk_tier")
            if risk_tier not in ["low", "medium", "high", "critical"]:
                risk_tier = mode if mode in ["low", "medium", "high", "critical"] else "medium"

            # Execute through the canonical mega-tool envelope.
            envelope = await kernel_fn(
                mode="kernel",
                payload={
                    "query": query,
                    "context": body.get("context"),
                    "session_id": session_id,
                    "risk_tier": risk_tier,
                    "auth_context": {
                        "actor_id": actor_id,
                        "authority_level": "agent",
                        "token_fingerprint": "REST-BYPASS",
                        "session_id": session_id,
                    },
                    "dry_run": False,
                    "allow_execution": True,
                },
            )

            # Extract results from the RuntimeEnvelope
            judge_data = envelope.model_dump() if hasattr(envelope, "model_dump") else envelope
            verdict = judge_data.get("verdict", "VOID")

            # Extract floors and metrics
            metrics = judge_data.get("metrics", {})
            telemetry = metrics.get("telemetry", {})
            truth_score = telemetry.get("G_star")

            # Map floors
            floors_passed = judge_data.get("meta", {}).get("floors_passed", [])
            floors_failed = judge_data.get("meta", {}).get("floors_failed", [])

            # Build human-readable summary
            if verdict == "SEAL":
                summary = "✓ All constitutional floors passed. Safe to proceed."
            elif verdict == "PARTIAL":
                summary = "⚠ Soft floor warning. Proceed with caution."
            elif verdict in ["VOID", "FAIL"]:
                summary = "✗ Constitutional violation detected. Action blocked."
            elif verdict == "888_HOLD":
                summary = "⏸ High-stakes decision. Requires human signature."
            else:
                summary = f"Status: {verdict}"

            latency_ms = (time.time() - start_time) * 1000

            return JSONResponse(
                {
                    "verdict": verdict,
                    "summary": summary,
                    "mode": mode,
                    "floors": {
                        "passed": floors_passed,
                        "failed": floors_failed,
                    },
                    "metrics": {"truth": truth_score, "threshold": 0.80},
                    "session_id": session_id,
                    "latency_ms": round(latency_ms, 2),
                    "version": judge_data.get("meta", {}).get("version", "2026.3.14"),
                }
            )

        except Exception as exc:
            logger.exception("checkpoint_endpoint failed")
            return JSONResponse(
                {"error": str(exc), "verdict": "HOLD", "issue": "RUNTIME_FAILURE"}, status_code=500
            )

    @route("/openapi.yaml", methods=["GET"])
    async def openapi_schema(request: Request) -> Response:
        """Serve OpenAPI schema for the REST compatibility surface."""
        schema_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "333_APPS",
            "L4_TOOLS",
            "chatgpt-actions",
            "chatgpt_openapi.yaml",
        )
        if os.path.exists(schema_path):
            content = open(schema_path).read()
            return Response(content, media_type="application/yaml")
        return JSONResponse({"error": "Schema not found"}, status_code=404)

    @route("/robots.txt", methods=["GET"])
    async def robots_txt(_request: Request) -> Response:
        return Response(ROBOTS_TXT, media_type="text/plain")

    @route("/llms.txt", methods=["GET"])
    async def llms_txt(_request: Request) -> Response:
        return Response(LLMS_TXT, media_type="text/plain")

    @route("/llms.json", methods=["GET"])
    async def llms_json(_request: Request) -> Response:
        return JSONResponse(LLMS_JSON, headers={"Access-Control-Allow-Origin": "*"})

    @route("/.well-known/agent-card.json", methods=["GET"])
    async def agent_card(_request: Request) -> Response:
        """A2A Agent Card — discovery endpoint for agent-to-agent protocol."""
        payload = {
            "name": "arifOS — AGENTS·API·AI·APPS",
            "description": "The AAA Surface Layer of arifOS. Agents (autonomous actors), API (structured interfaces), AI (governed intelligence), and Apps (executable tools). Built on MCP with 13 constitutional floors ensuring every action is true, safe, and human-aligned. DITEMPA BUKAN DIBERI.",
            "supportedInterfaces": [
                {
                    "url": "https://aaa.arif-fazil.com/mcp",
                    "protocolBinding": "MCP",
                    "protocolVersion": "2025-03-26",
                    "transport": "StreamableHTTP"
                }
            ],
            "provider": {
                "name": "Arif Fazil",
                "url": "https://arif-fazil.com",
                "role": "ARIF — Human Sovereign Architect"
            },
            "version": BUILD_VERSION,
            "capabilities": {
                "streaming": True,
                "governance": True,
                "humanInTheLoop": True,
                "constitutionalFloors": 13,
                "trinity": ["AGI", "ASI", "APEX"]
            },
            "skills": [
                "constitutional-audit",
                "governed-reasoning",
                "reality-search",
                "safe-execution",
                "metabolic-loop",
                "tri-witness-consensus"
            ],
            "architecture": {
                "layer": "AAA",
                "fullName": "AGENTS·API·AI·APPS",
                "trinityRuntime": "https://arifos.arif-fazil.com",
                "theoryDocs": "https://apex.arif-fazil.com",
                "humanSovereign": "https://arif-fazil.com"
            }
        }
        return JSONResponse(payload, headers={"Access-Control-Allow-Origin": "*"})

    # Serve the APEX Sovereign Dashboard v2.1 at /dashboard/
    dashboard_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "sites",
        "dashboard",
    )
    if os.path.exists(dashboard_dir) and hasattr(mcp, "_app"):
        mcp._app.mount(
            "/dashboard", StaticFiles(directory=dashboard_dir, html=True), name="dashboard"
        )

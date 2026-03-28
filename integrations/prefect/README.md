# arifOS × Prefect Ecosystem Integration

> **PrefectHQ Tools Integration** — Workflow orchestration, AI agents, and modern CLI

## Overview

This module integrates arifOS with the Prefect ecosystem:

| Component | Repository | Purpose |
|-----------|------------|---------|
| **Prefect** | `PrefectHQ/prefect` | Workflow orchestration |
| **Marvin** | `PrefectHQ/marvin` | AI/Agent framework |
| **Cyclopts** | `BrianPugh/cyclopts` | Modern CLI framework |
| **prefect-mcp-server** | `PrefectHQ/prefect-mcp-server` | MCP bridge |
| **pydantic-ai** | `pydantic/pydantic-ai` | LLM integration |

---

## Installation

```bash
# Install Prefect ecosystem
pip install prefect marvin cyclopts pydantic-ai

# Or install all at once
pip install "prefect[all]" marvin cyclopts
```

---

## Usage

### 1. arifOS Tools as Prefect Tasks

```python
from prefect import flow
from arifosmcp.integrations.prefect import constitutional_flow

@flow
def my_workflow():
    result = constitutional_flow(
        query="constitutional AI frameworks",
        session_id="my-session",
        require_safety=True
    )
    return result
```

### 2. Marvin AI with arifOS Governance

```python
from arifosmcp.integrations.prefect import arifos_agent

# Create governed AI agent
writer = arifos_agent(
    name="Technical Writer",
    instructions="Write clear documentation",
    enable_governance=True
)

# Run with automatic safety checks
result = writer.run("Explain Python async")
```

### 3. Cyclopts CLI

```bash
# Install CLI
pip install cyclopts

# Use arifOS CLI
python -m arifosmcp.integrations.prefect.cli --help

# Or create your own
from arifosmcp.integrations.prefect import create_cyclopts_app

app = create_cyclopts_app()
app()
```

CLI Commands:
```bash
arifos init --session-id=test --actor-id=admin
arifos search "constitutional AI" --top-k=10
arifos reason "How to implement F1 floor?" --mode=forge
arifos critique "Deploy to production without tests"
arifos judge "if x: return True" --mode=validate
arifos seal '{"decision": "approved"}'
arifos tools
arifos health
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     arifOS Kernel                            │
│              (11 Mega-Tools + F1-F13 Floors)                 │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼───────┐  ┌────────▼────────┐  ┌──────▼──────┐
│   Prefect     │  │     Marvin      │  │  Cyclopts   │
│  @flow/@task  │  │   AI Agents     │  │    CLI      │
│ Orchestration │  │   marvin.run    │  │  Commands   │
└───────────────┘  └─────────────────┘  └─────────────┘
```

---

## Module Structure

```
arifosmcp/integrations/prefect/
├── __init__.py           # Exports
├── tasks.py              # Prefect @task wrappers
├── marvin_bridge.py      # Marvin AI integration
├── cli.py                # Cyclopts CLI
└── README.md             # This file
```

---

## Examples

### Constitutional Research Pipeline

```python
from prefect import flow
from arifosmcp.integrations.prefect.tasks import (
    research_task, vault_seal_task, safety_check_task
)

@flow(name="Research with Governance")
async def research_flow(query: str):
    # Research
    findings = await research_task(query)
    
    # Safety check
    safety = await safety_check_task(findings)
    
    # Record to vault
    record = await vault_seal_task({
        "query": query,
        "findings": findings,
        "safety": safety
    })
    
    return record
```

### Governed AI Classification

```python
from arifosmcp.integrations.prefect.marvin_bridge import governed_classify

# Classify with safety checks
label = await governed_classify(
    text="User input text",
    labels=["safe", "suspicious", "dangerous"],
    enable_critique=True
)
```

---

## References

- Prefect: https://docs.prefect.io
- Marvin: https://www.askmarvin.ai
- Cyclopts: https://cyclopts.readthedocs.io
- pydantic-ai: https://ai.pydantic.dev

---

**ΔΩΨ | DITEMPA BUKAN DIBERI**

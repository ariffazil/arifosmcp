"""
arifosmcp.intelligence — ACLIP Console for AI

The local ops surface and console layer for arifOS AI agents.
Agents use this to see and operate the local machine — system health,
memory queries, and platform tooling.

Conceptually: what a CLI is for humans, ACLIP is for AI.

Protocol:  MCP (transport detail, not the identity)
Identity:  ACLIP CAI — Console for AI on arifOS
Relation:  Ops layer. aaa-mcp is the Constitution. This is the Console.

Entry: python -m arifosmcp.transport [stdio|sse|http|rest]
Legacy transport alias: python -m arifosmcp.intelligence [stdio|sse|http]
"""

__version__ = "1.0.0"
__server_name__ = "aclip-cai"
__description__ = "ACLIP — Console for AI on arifOS"

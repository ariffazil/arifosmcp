"""
arifosmcp.intelligence CLI Entry Point — Triple Transport Support

Usage:
    python -m arifosmcp.intelligence                # stdio (delegates to arifosmcp.transport)
    python -m arifosmcp.intelligence stdio          # stdio (delegates to arifosmcp.transport)
    python -m arifosmcp.intelligence sse            # SSE (delegates to arifosmcp.transport)
    python -m arifosmcp.intelligence http           # HTTP (delegates to arifosmcp.transport)
    python -m arifosmcp.intelligence health         # CLI subcommand
    python -m arifosmcp.intelligence processes      # CLI subcommand
    python -m arifosmcp.intelligence fs             # CLI subcommand

DITEMPA BUKAN DIBERI
"""

import asyncio
import json
import sys

TRANSPORT_MODES = {"stdio", "sse", "http", "streamable-http", "rest"}


async def minimal_cli():
    """Minimal CLI for subcommands without external dependencies."""
    from . import console_tools

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "help").strip().lower()

    if cmd == "health":
        res = await console_tools.system_health()
        print(json.dumps(res.to_dict(), indent=2))
    elif cmd in ("processes", "ps"):
        res = await console_tools.process_list()
        print(json.dumps(res.to_dict(), indent=2))
    elif cmd == "fs":
        path = sys.argv[2] if len(sys.argv) > 2 else "."
        res = await console_tools.fs_inspect(path=path)
        print(json.dumps(res.to_dict(), indent=2))
    else:
        print(__doc__)


def main():
    if len(sys.argv) > 1:
        mode = sys.argv[1].strip().lower()
    else:
        mode = "stdio"

    # Transport now lives in the canonical arifosmcp.transport entrypoint.
    if mode in TRANSPORT_MODES or mode in {"", "-h", "--help"}:
        import warnings

        try:
            from arifosmcp.runtime.__main__ import main as aaa_main
        except ImportError:
            print("Error: arifosmcp.runtime not found. Ensure package is installed.")
            sys.exit(1)

        warnings.warn(
            "arifosmcp.intelligence transport modes are deprecated; use 'python -m arifosmcp.runtime' directly.",
            DeprecationWarning,
            stacklevel=2,
        )
        forwarded_mode = mode
        forwarded_args = sys.argv[2:]
        if mode == "streamable-http":
            forwarded_mode = "http"
        elif mode in {"", "-h", "--help"}:
            forwarded_mode = None
            forwarded_args = sys.argv[1:]

        forwarded_argv = ["arifosmcp.runtime"]
        if forwarded_mode is not None:
            forwarded_argv.append(forwarded_mode)
        forwarded_argv.extend(forwarded_args)
        sys.argv = forwarded_argv
        aaa_main()
        return

    # Fall through to minimal CLI
    asyncio.run(minimal_cli())


if __name__ == "__main__":
    main()

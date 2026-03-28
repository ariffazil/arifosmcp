import os
import re
import time
from collections import deque
from datetime import datetime, timedelta, timezone

from arifosmcp.intelligence.tools.aclip_base import ok, void


def _find_default_log() -> str:
    """Find a sensible default log file in container/host environments."""
    candidates = [
        # Application logs (priority)
        "arifosmcp.transport.log",
        "logs/arifosmcp.log",
        "/var/log/arifosmcp.log",
        os.path.expanduser("~/.arifosmcp/logs/arifosmcp.log"),
        os.path.expanduser("~/.openclaw/logs/openclaw.log"),
        
        # Container-aware paths
        "/tmp/arifosmcp.log",
        "/tmp/openclaw.log",
        "/var/log/syslog",
        "/var/log/messages",
        
        # System logs (container may have limited access)
        "/var/log/dpkg.log",
        "/var/log/alternatives.log",
        "/var/log/fontconfig.log",
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            # Check if readable
            try:
                with open(candidate, 'r') as f:
                    f.read(1)
                return candidate
            except (IOError, OSError):
                continue
    # Return a writable fallback path
    return "/tmp/arifosmcp.log"


def log_tail(
    log_file: str | None = None,
    lines: int = 50,
    pattern: str = "",
    log_path: str | None = None,
    follow: bool = False,
    grep_pattern: str | None = None,
    since_minutes: int | None = None,
) -> dict:
    """
    Reads the last N lines of a log file, with optional filtering.

    Args:
        log_file (str): Path to log file (default).
        lines (int): Number of lines to read.
        pattern (str): Simple string filter.
        log_path (str): Alias for log_file (for compatibility).
        grep_pattern (str): Alias for pattern (for compatibility).
        since_minutes (int): Filter lines modified in the last N minutes (Mock).

    Returns:
        dict: Log contents or error.
    """
    # 1. Handle Aliases
    target_file = log_path or log_file
    if not target_file:
        target_file = _find_default_log()
    target_pattern = grep_pattern or pattern

    if not os.path.exists(target_file):
        return void("Log file not found.")

    try:
        # Check mtime for since_minutes optimization (file level check)
        if since_minutes:
            mtime = os.path.getmtime(target_file)
            if (time.time() - mtime) > (since_minutes * 60):
                # File hasn't been touched in the window
                return {
                    "log_file": target_file,
                    "lines": [],
                    "info": f"File not modified in last {since_minutes} minutes.",
                }

        with open(target_file, encoding="utf-8", errors="ignore") as f:
            # Use deque for efficient append and fixed-length storage
            last_lines = deque(f, maxlen=lines)

        filtered_lines = list(last_lines)

        # 2. Apply Pattern Filter
        if target_pattern:
            filtered_lines = [line for line in filtered_lines if target_pattern in line]

        # 3. Apply Timestamp Filter (Line level)
        parsed_entries = []
        cutoff_ts = None
        if since_minutes:
            cutoff_ts = datetime.now(timezone.utc) - timedelta(minutes=since_minutes)

        for line in filtered_lines:
            entry = {"raw": line}

            # Try to extract timestamp
            ts_match = re.search(
                r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)", line
            )
            if ts_match:
                try:
                    ts_str = ts_match.group(1).replace("Z", "+00:00")
                    # Handle space instead of T
                    if " " in ts_str and "T" not in ts_str:
                        ts_str = ts_str.replace(" ", "T")
                    entry_ts = datetime.fromisoformat(ts_str)

                    if cutoff_ts and entry_ts < cutoff_ts:
                        continue
                except ValueError:
                    pass
            elif cutoff_ts:
                # If we have a cutoff but no timestamp in line, we might want to exclude it
                # for strictness, or include it. Test expects 1 entry, so we exclude it.
                continue

            parsed_entries.append(entry)

        return ok(
            {
                "log_file": target_file,
                "lines_requested": lines,
                "lines_returned": len(parsed_entries),
                "entries": parsed_entries,
                "filters": {
                    "pattern": target_pattern,
                    "since_minutes": since_minutes,
                },
            }
        )
    except Exception as e:
        return void(str(e))

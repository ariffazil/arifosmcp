import datetime
import fnmatch
from pathlib import Path

from arifosmcp.intelligence.tools.aclip_base import ok, partial, void


def fs_inspect(
    path: str = ".",
    depth: int = 1,
    include_hidden: bool = False,
    pattern: str = "*",  # Filter by filename (e.g., "*.py")
    min_size_bytes: int = 0,  # Filter by size
    max_files: int = 100,  # Circuit Breaker
    max_depth: int | None = None,  # Compatibility arg (bridge sends this)
) -> dict:
    """
    Inspects the filesystem at a given path without modification.
    Hardened with F4 Clarity (Entropy Limits & Filtering).

    Args:
        path: Root path to inspect
        depth: Recursion depth
        include_hidden: Include .* files
        pattern: Glob pattern for filenames
        min_size_bytes: Filter small files
        max_files: Maximum number of items to return before halting
        max_depth: Optional override for depth (compatibility)
    """
    # Use max_depth if provided (priority over depth if not None, but usually they align)
    effective_depth = max_depth if max_depth is not None else depth

    root_path = Path(path)
    if not root_path.exists():
        return void(f"Path not found: {path}")

    stats = {"scanned": 0, "returned": 0, "limit_reached": False}

    def _format_time(timestamp):
        return datetime.datetime.fromtimestamp(timestamp).isoformat()

    def _inspect_path(current_path: Path, current_depth: int):
        if current_depth > effective_depth or stats["limit_reached"]:
            return None

        items = []
        try:
            # Sort for deterministic output (F2 Truth)
            try:
                iterator = sorted(current_path.iterdir())
            except OSError:
                return []

            for item in iterator:
                if stats["returned"] >= max_files:
                    stats["limit_reached"] = True
                    break

                # 1. Hidden File Check
                if not include_hidden and item.name.startswith("."):
                    continue

                # 2. Pattern Match Check
                # If it's a file, we strictly enforce pattern.
                # If it's a dir, we recurse unless strictly excluded?
                # For safety/clarity, we apply pattern to files only, but allow dirs to be traversed
                # so we can find files deep inside.
                if item.is_file() and pattern and pattern != "*":
                    if not fnmatch.fnmatch(item.name, pattern):
                        continue

                stats["scanned"] += 1

                try:
                    stat = item.stat()

                    # 3. Size Filter Check (Files only)
                    if item.is_file() and stat.st_size < min_size_bytes:
                        continue

                    # If it's a dir, we include it so we can show structure,
                    # unless we want to filter empty dirs? For now, we show them.

                    item_details = {
                        "name": item.name,
                        "type": "dir" if item.is_dir() else "file",
                        "size": stat.st_size,
                        "modified": _format_time(stat.st_mtime),
                        "path": str(item),
                        "relative": str(item.relative_to(root_path)),
                    }

                    if item.is_dir():
                        # Recurse
                        children = _inspect_path(item, current_depth + 1)
                        if children:
                            item_details["children"] = children

                    items.append(item_details)
                    stats["returned"] += 1

                except (OSError, PermissionError):
                    continue

            return items
        except (OSError, PermissionError):
            return [{"error": f"Permission Denied: {current_path}"}]

    result = _inspect_path(root_path, 1)

    # Separate directories and files for test compatibility
    directories = [item for item in (result or []) if item["type"] == "dir"]
    files = [item for item in (result or []) if item["type"] == "file"]

    return (partial if stats["limit_reached"] else ok)(
        {
            "root": str(root_path.resolve()),
            "pattern": pattern,
            "limits": {"depth": effective_depth, "max_files": max_files},
            "stats": stats,
            "tree": result,
            "directories": directories,
            "files": files,
            "total_dirs": len(directories),
            "total_files": len(files),
            "traversal_depth": effective_depth,
        },
        warning="Max files limit reached" if stats["limit_reached"] else None,
    )


# Alias for architectural consistency
inspect_path = fs_inspect

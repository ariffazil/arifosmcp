from __future__ import annotations

import os
import re
import sys
from pathlib import Path

# Platform-aware path resolution.
# Windows Forge:  C:/arifOS/0_KERNEL/FLOORS
# Linux VPS:      /root/arifOS/0_KERNEL/FLOORS  (or set ARIFOS_MIND_PATH env var)
_DEFAULT_MIND_ROOT = (
    Path("C:/arifOS")
    if os.name == "nt"
    else Path(os.environ.get("ARIFOS_MIND_PATH", "/root/arifOS"))
)


class ManifestLoader:
    """
    Dynamically loads constitutional thresholds from the Mind (arifOS kernel).
    Bridges Markdown theory into Python runtime enforcement.
    Works on both Windows Forge (C:/arifOS) and Linux VPS (/root/arifOS).
    Override path with ARIFOS_MIND_PATH env var.
    """

    CANON_FLOORS_PATH = _DEFAULT_MIND_ROOT / "0_KERNEL" / "FLOORS"

    @classmethod
    def load_thresholds(cls) -> dict[str, float]:
        """
        Scrapes FXX_*.md files in the Mind for threshold values.
        Looks for 'Threshold: X' or 'Threshold: [X, Y]' patterns.
        """
        thresholds = {}
        if not cls.CANON_FLOORS_PATH.exists():
            return thresholds

        for floor_file in cls.CANON_FLOORS_PATH.glob("F*.md"):
            try:
                content = floor_file.read_text(encoding="utf-8")

                # Match Floor ID (e.g., F1, F01)
                floor_id_match = re.search(r"Floor:\s*F(\d+)", content)
                if not floor_id_match:
                    # Fallback to filename
                    floor_id_match = re.search(r"F(\d+)", floor_file.name)

                if floor_id_match:
                    # Canonicalize to F1, F2... (no leading zeros for dict compatibility)
                    raw_id = floor_id_match.group(1).lstrip("0")
                    if not raw_id:
                        raw_id = "0"
                    f_id = f"F{raw_id}"

                    # Match Threshold (e.g., Threshold: 0.95 or Threshold: ≥ 0.99)
                    # We look for words like 'Threshold:' followed by optional symbols
                    # and then the number
                    threshold_match = re.search(r"Threshold:\s*(?:[≥≤\s]*)\s*([\d\.]+)", content)
                    if threshold_match:
                        thresholds[f_id] = float(threshold_match.group(1))
                    else:
                        # Try range match (e.g., F7 Humility [0.03, 0.05])
                        range_match = re.search(r"Threshold:\s*\[([\d\.]+),\s*([\d\.]+)\]", content)
                        if range_match:
                            thresholds[f_id] = float(range_match.group(2))

            except Exception as e:
                sys.stderr.write(f"[arifOS] Error loading {floor_file}: {e}\n")

        return thresholds


def sync_runtime_floors():
    """Update core.shared.floors.THRESHOLDS with Mind-derived values."""
    try:
        from arifosmcp.core.shared.floors import FLOOR_SPEC_KEYS, THRESHOLDS

        dynamic_thresholds = ManifestLoader.load_thresholds()

        for f_id, val in dynamic_thresholds.items():
            spec_key = FLOOR_SPEC_KEYS.get(f_id)
            if spec_key and spec_key in THRESHOLDS:
                old_val = THRESHOLDS[spec_key].get("threshold")
                if old_val != val:
                    sys.stderr.write(f"[arifOS] Updating {f_id} ({spec_key}): {old_val} -> {val}\n")
                    THRESHOLDS[spec_key]["threshold"] = val

        return True
    except Exception as e:
        sys.stderr.write(f"[arifOS] Failed to sync runtime floors: {e}\n")
        return False


if __name__ == "__main__":
    t = ManifestLoader.load_thresholds()
    print(f"Dynamic Thresholds Scraped: {t}")
    sync_runtime_floors()

import yaml
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

MANIFEST_DIR = Path(__file__).parent / "manifests"

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self._load_manifests()

    def _load_manifests(self):
        if not MANIFEST_DIR.exists():
            return
        
        for manifest_path in MANIFEST_DIR.glob("**/*.yaml"):
            with open(manifest_path, 'r') as f:
                try:
                    manifest = yaml.safe_load(f)
                    if manifest and 'name' in manifest:
                        self.tools[manifest['name']] = manifest
                except Exception:
                    continue

    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        return list(self.tools.keys())

registry = ToolRegistry()

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class AppLayer(Enum):
    """Application layer in the refined 4-layer taxonomy."""
    L0_CONSTITUTION = "L0"
    L1_INSTRUCTION = "L1"
    L2_OPERATION = "L2"
    L3_CIVILIZATION = "L3"

class FloorClassification(Enum):
    """How a floor is classified for an app."""
    HARD = "hard"
    SOFT = "soft"
    N_A = "n/a"

@dataclass
class FloorManifesto:
    """Manifesto entry for one floor."""
    floor_id: str
    classification: FloorClassification
    custom_threshold: Any | None = None
    rationale: str = ""

@dataclass
class AppManifesto:
    """Constitutional manifesto for an application."""
    app_name: str
    layer: AppLayer
    description: str
    version: str = "1.0.0"
    floors: list[FloorManifesto] = field(default_factory=list)
    requires_sovereign_gate: bool = False
    irreversible_actions: list[str] = field(default_factory=list)
    l0_organs_used: list[str] = field(default_factory=lambda: ["agi_cognition"])
    author: str = ""
    dependencies: list[str] = field(default_factory=list)

    def validate(self) -> bool:
        if not self.floors:
            raise ValueError(f"App '{self.app_name}' must declare at least one floor")
        floor_ids = {floor.floor_id for floor in self.floors}
        missing_required = {"F1", "F2", "F7"} - floor_ids
        if missing_required:
            raise ValueError(
                f"App '{self.app_name}' missing required floors: {sorted(missing_required)}"
            )
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "app_name": self.app_name,
            "layer": self.layer.value,
            "version": self.version,
            "description": self.description,
            "floors": [
                {
                    "floor_id": floor.floor_id,
                    "classification": floor.classification.value,
                    "threshold": floor.custom_threshold,
                    "rationale": floor.rationale,
                }
                for floor in self.floors
            ],
            "requires_sovereign_gate": self.requires_sovereign_gate,
            "irreversible_actions": self.irreversible_actions,
            "l0_organs_used": self.l0_organs_used,
        }

class AppRegistry:
    """In-memory registry of constitutional applications."""
    _apps: dict[str, AppManifesto] = {}

    @classmethod
    def register(cls, manifesto: AppManifesto) -> None:
        manifesto.validate()
        cls._apps[manifesto.app_name] = manifesto

    @classmethod
    def get(cls, app_name: str) -> AppManifesto | None:
        return cls._apps.get(app_name)

    @classmethod
    def list_all(cls) -> list[str]:
        return list(cls._apps.keys())

    @classmethod
    def audit(cls) -> dict[str, Any]:
        by_layer: dict[str, int] = {}
        sovereign_gates = 0
        for app in cls._apps.values():
            layer = app.layer.value
            by_layer[layer] = by_layer.get(layer, 0) + 1
            if app.requires_sovereign_gate:
                sovereign_gates += 1
        return {
            "total_apps": len(cls._apps),
            "by_layer": by_layer,
            "sovereign_gates_required": sovereign_gates,
            "apps": {name: manifesto.to_dict() for name, manifesto in cls._apps.items()},
        }

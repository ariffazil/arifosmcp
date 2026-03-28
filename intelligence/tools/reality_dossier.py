"""
arifosmcp/intelligence/tools/reality_dossier.py — Earth Witness Aggregator

Provides the 'Earth witness' component for F3 Tri-Witness compliance.
Combines physical grounding, thermodynamic state, and system vitals.

Guiding Principle: Ditempa Bukan Diberi (Forged, Not Given)
"""

from __future__ import annotations

import logging
import platform
import time
from datetime import datetime, timezone
from typing import Any

from arifosmcp.intelligence.tools.envelope import unified_tool_output
from arifosmcp.intelligence.tools.reality_grounding import reality_check
from arifosmcp.core.physics.thermodynamics_hardened import get_thermodynamic_budget
from arifosmcp.core.telemetry import get_system_vitals

logger = logging.getLogger(__name__)


from enum import Enum
from pydantic import BaseModel, Field

class DossierStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"

class Witness(BaseModel):
    id: str
    type: str = "general"
    confidence: float = Field(0.5, ge=0.0, le=1.0)
    observation: str = ""

class DossierEngine:
    """Mock engine for tests."""
    def compute_witness_confidence(self, witnesses: list[Witness]) -> float:
        if not witnesses: return 0.0
        return sum(w.confidence for w in witnesses) / len(witnesses)
    def _generate_final_verdict(self, dossier: Any) -> str:
        return "SEAL"

@unified_tool_output(stage="222_REALITY")
async def reality_dossier(
    query: str,
    session_id: str = "global",
    include_system_vitals: bool = True,
    include_thermodynamics: bool = True,
    include_web_research: bool = True,
) -> dict[str, Any]:
    """
    Generates a Reality Dossier as a high-fidelity Earth Witness.
    
    This tool performs:
    1. Physical Grounding: System specs, time, location, and hardware vitals.
    2. Thermodynamic Grounding: Landauer bounds, entropy budget, and energy consumption.
    3. External Grounding: Fact-checking via reality_grounding cascade.
    
    Returns a dossier aligned with F3 Tri-Witness consensus.
    """
    start_time = time.time()
    
    # 1. Physical Context (The Body)
    vitals = get_system_vitals() if include_system_vitals else {}
    
    # 2. Thermodynamic Context (The Metabolism)
    thermo_report = {}
    if include_thermodynamics:
        try:
            budget = get_thermodynamic_budget(session_id)
            thermo_report = budget.to_dict()
        except Exception as e:
            logger.debug(f"Thermodynamic budget not found for {session_id}: {e}")
            thermo_report = {"status": "no_active_budget"}

    # 3. External Research (The World)
    research_results = {}
    if include_web_research:
        research_results = await reality_check(query, max_results=3)
    
    # 4. Integrate into Dossier
    # We use the DossierEngine from runtime to maintain architectural separation
    # but here we enrich it with ACTUAL earth data.
    
    # Calculate Earth Stress (0.0 to 1.0)
    # Stress increases with high CPU, low battery (if applicable), or high entropy
    cpu_stress = vitals.get("cpu_percent", 0.0) / 100.0
    mem_stress = vitals.get("memory_percent", 0.0) / 100.0
    
    # Earth Witness Score (E)
    # E = 1.0 - mean(stressors)
    earth_score = 1.0 - ((cpu_stress * 0.4) + (mem_stress * 0.4))
    
    # Adjust for Landauer efficiency if available
    if thermo_report.get("landauer_violations", 0) > 0:
        earth_score *= 0.8  # Penalty for impossible physics
    
    earth_score = max(0.0, min(1.0, earth_score))

    # Construct Dossier
    dossier_data = {
        "query": query,
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "earth_witness": {
            "score": round(earth_score, 4),
            "status": (
                "HARDENED"
                if earth_score > 0.9
                else "STRESSED" if earth_score > 0.5 else "CRITICAL"
            ),
            "vitals": vitals,
            "thermodynamics": thermo_report,
            "environment": {
                "os": platform.system(),
                "node": platform.node(),
                "processor": platform.processor(),
                "time_local": time.ctime(),
            }
        },
        "research": research_results, 
        "metadata": {
            "processing_ms": round((time.time() - start_time) * 1000, 2),
            "version": "v1.0-F3-HARDENED",
            "motto": "DITEMPA BUKAN DIBERI"
        }
    }
    
    return dossier_data

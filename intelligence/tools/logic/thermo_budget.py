"""
arifosmcp.intelligence/tools/logic/thermo_budget.py -- Legacy Thermodynamic Budget Manager

APEX_THERMOBUDGET = True

DEPRECATED: Use core.physics.thermo_budget for all new code.
This module is kept for legacy compatibility and will be removed in v2026.04.
"""

from __future__ import annotations

import warnings

from arifosmcp.core.physics.thermo_budget import ThermoBudget as CanonicalThermoBudget
from arifosmcp.core.physics.thermo_budget import ThermoSnapshot as CanonicalThermoSnapshot

# Issue deprecation warning on import
warnings.warn(
    "arifosmcp.intelligence.tools.logic.thermo_budget is deprecated. "
    "Use core.physics.thermo_budget instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Alias the canonical implementations to maintain compatibility during migration
ThermoBudget = CanonicalThermoBudget
ThermoSnapshot = CanonicalThermoSnapshot

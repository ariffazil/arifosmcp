import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    from arifosmcp.core.physics.thermodynamics_hardened import (
        ThermodynamicBudget,
        ThermodynamicError,
        get_thermodynamic_budget,
    )
    THERMODYNAMICS_AVAILABLE = True
except ImportError:
    ThermodynamicBudget = None  # type: ignore[assignment]
    get_thermodynamic_budget = None  # type: ignore[assignment]
    THERMODYNAMICS_AVAILABLE = False
    ThermodynamicError = Exception  # type: ignore[assignment,misc]
    LandauerViolation = Exception  # type: ignore[assignment,misc]
    EntropyIncreaseViolation = Exception  # type: ignore[assignment,misc]

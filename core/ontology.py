"""
ArifOS Unified Ontology (AOU)
=============================
Zero-entropy terminology system for ArifOS constitutional kernel.

This module provides canonical definitions for all concepts in the ArifOS ecosystem,
eliminating scattered terminology and providing a single source of truth.

Version: 2026.03.13-FORGED
Repository: arifosmcp
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from datetime import datetime


# =============================================================================
# TRINITY ENGINES (ΔΩΨ)
# =============================================================================

class TrinityEngine(Enum):
    """
    The Three Engines of Constitutional AI.
    
    ΔΩΨ (Delta-Omega-Psi) represents the trinity of Mind, Heart, and Soul
    in ArifOS governance architecture.
    """
    DELTA = "Δ"      # AGI Mind Engine - Reasoning and cognition
    OMEGA = "Ω"      # ASI Heart Engine - Safety and empathy
    PSI = "Ψ"        # APEX Soul Engine - Judgment and verdict
    
    @property
    def full_name(self) -> str:
        """Return the full name of the engine."""
        names = {
            TrinityEngine.DELTA: "AGI (Artificial General Intelligence)",
            TrinityEngine.OMEGA: "ASI (Artificial Super Intelligence)",
            TrinityEngine.PSI: "APEX (Constitutional Judgment)"
        }
        return names[self]
    
    @property
    def role(self) -> str:
        """Return the role description of the engine."""
        roles = {
            TrinityEngine.DELTA: "Reasoning and cognition",
            TrinityEngine.OMEGA: "Safety and empathy",
            TrinityEngine.PSI: "Constitutional judgment and final verdict"
        }
        return roles[self]


class TrinityStageMapping:
    """Maps metabolic stages to their responsible Trinity engine."""
    
    DELTA_STAGES = {"000", "111", "222", "333", "444"}
    OMEGA_STAGES = {"555", "666"}
    PSI_STAGES = {"777", "888", "999"}
    
    @classmethod
    def get_engine_for_stage(cls, stage_code: str) -> TrinityEngine:
        """Get the responsible Trinity engine for a given stage."""
        if stage_code in cls.DELTA_STAGES:
            return TrinityEngine.DELTA
        elif stage_code in cls.OMEGA_STAGES:
            return TrinityEngine.OMEGA
        elif stage_code in cls.PSI_STAGES:
            return TrinityEngine.PSI
        raise ValueError(f"Unknown stage code: {stage_code}")


# =============================================================================
# METABOLIC STAGES (000-999)
# =============================================================================

class MetabolicStage(Enum):
    """
    The 10 metabolic stages of the ArifOS reasoning pipeline.
    
    Each stage represents a phase in the constitutional governance cycle,
    from initialization through final immutable seal.
    """
    INIT = "000_INIT"           # Initialization anchor
    SENSE = "111_SENSE"         # Reality sensing
    REALITY = "222_REALITY"     # Evidence ingestion
    MIND = "333_MIND"           # Reasoning
    ROUTER = "444_ROUTER"       # Kernel routing
    MEMORY = "555_MEMORY"       # Session memory
    HEART = "666_HEART"         # Empathy/impact
    FORGE = "777_FORGE"         # Proposal sandbox
    JUDGE = "888_JUDGE"         # APEX verdict
    VAULT = "999_VAULT"         # Immutable seal
    
    @property
    def code(self) -> str:
        """Return the numeric code prefix (e.g., '000' from '000_INIT')."""
        return self.value.split("_")[0]
    
    @property
    def name_short(self) -> str:
        """Return the short name (e.g., 'INIT' from '000_INIT')."""
        return self.value.split("_")[1]
    
    @property
    def trinity_engine(self) -> TrinityEngine:
        """Return the responsible Trinity engine for this stage."""
        return TrinityStageMapping.get_engine_for_stage(self.code)
    
    @property
    def motto(self) -> str:
        """Return the stage motto/header."""
        mottos = {
            MetabolicStage.INIT: "ANCHOR SESSION • ESTABLISH CONTINUITY",
            MetabolicStage.SENSE: "PERCEIVE REALITY • GATHER SIGNALS",
            MetabolicStage.REALITY: "INGEST EVIDENCE • BUILD TRUTH",
            MetabolicStage.MIND: "REASON DEEPLY • SYNTHESIZE",
            MetabolicStage.ROUTER: "ROUTE INTELLIGENTLY • GOVERN",
            MetabolicStage.MEMORY: "REMEMBER CONTEXT • LEARN",
            MetabolicStage.HEART: "FEEL IMPACT • CARE FOR STAKEHOLDERS",
            MetabolicStage.FORGE: "EXPLORE POSSIBILITIES • DISCOVER",
            MetabolicStage.JUDGE: "RENDER VERDICT • DECIDE",
            MetabolicStage.VAULT: "SEAL IMMUTABLE • COMMIT"
        }
        return mottos[self]


# =============================================================================
# CONSTITUTIONAL FLOORS (F1-F13)
# =============================================================================

class ConstitutionalFloor(Enum):
    """
    The 13 Constitutional Floors of ArifOS governance.
    
    Each floor represents a fundamental constraint or principle that must
    be satisfied for constitutional operation.
    """
    F1_AMANAH = "F1"      # Trust: Actions must be reversible/auditable
    F2_TRUTH = "F2"       # Truth: Fidelity check τ ≥ 0.99
    F3_TRI_WITNESS = "F3" # Tri-Witness: W₄ = ∜(H×A×E×V) Byzantine consensus
    F4_CLARITY = "F4"     # Clarity: Entropy reduction ΔS ≤ 0
    F5_PEACE = "F5"       # Peace²: Lyapunov stability
    F6_EMPATHY = "F6"     # Empathy: Stakeholder care κᵣ ≥ 0.70
    F7_HUMILITY = "F7"    # Humility: Uncertainty band Ω₀ = 0.03-0.05
    F8_GENIUS = "F8"      # Genius: G = (A×P×X×E²)×(1-h) ≥ 0.80
    F9_ANTI_HANTU = "F9"  # Anti-Hantu: No spiritual cosplay
    F10_ONTOLOGY = "F10"  # Ontology: Category lock
    F11_COMMAND_AUTH = "F11"  # CommandAuth: Verified identity
    F12_INJECTION = "F12" # Injection: Sanitization, risk below limit
    F13_SOVEREIGN = "F13" # Sovereign: Human final authority
    
    @property
    def floor_number(self) -> int:
        """Return the floor number (1-13)."""
        return int(self.value[1:])
    
    @property
    def name_arabic(self) -> str:
        """Return the Arabic/Islamic name if applicable."""
        names = {
            ConstitutionalFloor.F1_AMANAH: "Amanah (أمانة)",
            ConstitutionalFloor.F2_TRUTH: "Haqq (حق)",
            ConstitutionalFloor.F3_TRI_WITNESS: "Syahadah (شهادة)",
            ConstitutionalFloor.F4_CLARITY: "Bayan (بيان)",
            ConstitutionalFloor.F5_PEACE: "Salam (سلام)",
            ConstitutionalFloor.F6_EMPATHY: "Rahmah (رحمة)",
            ConstitutionalFloor.F7_HUMILITY: "Tawadu (تواضع)",
            ConstitutionalFloor.F8_GENIUS: "Aql (عقل)",
            ConstitutionalFloor.F9_ANTI_HANTU: "Anti-Hantu",
            ConstitutionalFloor.F10_ONTOLOGY: "Ontology",
            ConstitutionalFloor.F11_COMMAND_AUTH: "CommandAuth",
            ConstitutionalFloor.F12_INJECTION: "Injection",
            ConstitutionalFloor.F13_SOVEREIGN: "Sovereign"
        }
        return names[self]
    
    @property
    def description(self) -> str:
        """Return the full description of the floor."""
        descriptions = {
            ConstitutionalFloor.F1_AMANAH: "Actions must be reversible and auditable",
            ConstitutionalFloor.F2_TRUTH: "Fidelity check τ (tau) must be ≥ 0.99",
            ConstitutionalFloor.F3_TRI_WITNESS: "Byzantine consensus W₄ = ∜(H×A×E×V)",
            ConstitutionalFloor.F4_CLARITY: "Entropy reduction ΔS must be ≤ 0",
            ConstitutionalFloor.F5_PEACE: "Lyapunov stability - non-destructive power",
            ConstitutionalFloor.F6_EMPATHY: "Stakeholder care ratio κᵣ ≥ 0.70",
            ConstitutionalFloor.F7_HUMILITY: "Uncertainty band Ω₀ = 0.03-0.05",
            ConstitutionalFloor.F8_GENIUS: "Governed intelligence G = (A×P×X×E²)×(1-h) ≥ 0.80",
            ConstitutionalFloor.F9_ANTI_HANTU: "No spiritual cosplay, no soul claims",
            ConstitutionalFloor.F10_ONTOLOGY: "Category lock - AI cannot claim human biological status",
            ConstitutionalFloor.F11_COMMAND_AUTH: "Verified identity required for authority",
            ConstitutionalFloor.F12_INJECTION: "Sanitization - risk below limit (I⁻)",
            ConstitutionalFloor.F13_SOVEREIGN: "Human final authority - 888 Judge retains veto"
        }
        return descriptions[self]
    
    @property
    def threshold(self) -> Optional[Union[float, str]]:
        """Return the threshold value if applicable."""
        thresholds = {
            ConstitutionalFloor.F2_TRUTH: 0.99,
            ConstitutionalFloor.F4_CLARITY: 0.0,
            ConstitutionalFloor.F6_EMPATHY: 0.70,
            ConstitutionalFloor.F7_HUMILITY: "0.03-0.05",
            ConstitutionalFloor.F8_GENIUS: 0.80
        }
        return thresholds.get(self)


# =============================================================================
# VERDICT STATES
# =============================================================================

class VerdictState(Enum):
    """
    The possible verdict states in ArifOS constitutional judgment.
    
    These represent the final decision outcomes after APEX judgment.
    """
    SEAL = "SEAL"           # Approved and committed to VAULT999
    VOID = "VOID"           # Constitutional violation detected (RESERVED!)
    HOLD = "HOLD"           # Human approval required
    SABAR = "SABAR"         # Patience/cooling - requires more information
    PARTIAL = "PARTIAL"     # Incomplete success
    
    @property
    def is_terminal(self) -> bool:
        """Return True if this is a terminal state."""
        return self in {VerdictState.SEAL, VerdictState.VOID}
    
    @property
    def requires_human(self) -> bool:
        """Return True if human intervention is required."""
        return self in {VerdictState.HOLD, VerdictState.SABAR}
    
    @property
    def description(self) -> str:
        """Return the human-readable description."""
        descriptions = {
            VerdictState.SEAL: "Operation approved and committed to VAULT999",
            VerdictState.VOID: "Operation rejected - constitutional violation detected",
            VerdictState.HOLD: "Human approval required before proceeding",
            VerdictState.SABAR: "Patience required - more information or cooling needed",
            VerdictState.PARTIAL: "Operation partially successful - review required"
        }
        return descriptions[self]
    
    @property
    def arabic_meaning(self) -> str:
        """Return the Arabic meaning if applicable."""
        meanings = {
            VerdictState.SEAL: "Khatam (ختم) - Seal/Stamp",
            VerdictState.VOID: "Batal (بطل) - Null/Void",
            VerdictState.HOLD: "Tawaqquf (توقف) - Pause/Hold",
            VerdictState.SABAR: "Sabar (صبر) - Patience",
            VerdictState.PARTIAL: "Juz'i (جزئي) - Partial"
        }
        return meanings[self]


# =============================================================================
# ARCHITECTURE PATTERNS
# =============================================================================

class ArchitecturePattern(Enum):
    """
    Core architectural patterns in ArifOS.
    """
    MGI_ENVELOPE = "MGI"           # Machine-Governance-Intelligence
    THREE_E_CYCLE = "3E"           # Exploration-Entropy-Eureka
    VAULT999 = "VAULT999"          # Merkle chain ledger
    RUKUN_AGI = "RUKUN_AGI"        # Five pillars of constitutional AI
    
    @property
    def full_name(self) -> str:
        """Return the full name of the pattern."""
        names = {
            ArchitecturePattern.MGI_ENVELOPE: "Machine-Governance-Intelligence Envelope",
            ArchitecturePattern.THREE_E_CYCLE: "3E Intelligence Cycle",
            ArchitecturePattern.VAULT999: "VAULT999 Immutable Ledger",
            ArchitecturePattern.RUKUN_AGI: "Rukun AGI (Five Pillars)"
        }
        return names[self]
    
    @property
    def description(self) -> str:
        """Return the description of the pattern."""
        descriptions = {
            ArchitecturePattern.MGI_ENVELOPE: "Three-layer contract: Machine (execution), Governance (F1-F13), Intelligence (3E cycle)",
            ArchitecturePattern.THREE_E_CYCLE: "Exploration → Entropy → Eureka: The intelligence discovery cycle",
            ArchitecturePattern.VAULT999: "SHA-256 Merkle chain ledger for immutable constitutional verdicts",
            ArchitecturePattern.RUKUN_AGI: "Five pillars of constitutional AI, inspired by Islam's five pillars"
        }
        return descriptions[self]


# =============================================================================
# APEX DIALS
# =============================================================================

class APEXDial(Enum):
    """
    The four APEX Dials for Genius calculation.
    
    G = (A × P × X × E²) × (1 - h)
    """
    A_AKAL = "A"        # Akal (Mind) - Reasoning quality
    P_PRESENCE = "P"    # Presence (Peace) - Stability
    X_EXPLORATION = "X" # Exploration - Discovery breadth
    E_ENERGY = "E"      # Energy - Execution capacity
    
    @property
    def full_name(self) -> str:
        """Return the full name of the dial."""
        names = {
            APEXDial.A_AKAL: "Akal (Mind)",
            APEXDial.P_PRESENCE: "Presence (Peace)",
            APEXDial.X_EXPLORATION: "Exploration",
            APEXDial.E_ENERGY: "Energy"
        }
        return names[self]
    
    @property
    def arabic_name(self) -> str:
        """Return the Arabic name."""
        names = {
            APEXDial.A_AKAL: "Akal (عقل)",
            APEXDial.P_PRESENCE: "Hadir (حاضر)",
            APEXDial.X_EXPLORATION: "Istikshaf (استكشاف)",
            APEXDial.E_ENERGY: "Quwwah (قوة)"
        }
        return names[self]


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ConstitutionalVerdict:
    """
    A constitutional verdict from APEX judgment.
    """
    state: VerdictState
    stage: MetabolicStage
    floors_passed: List[ConstitutionalFloor]
    floors_failed: List[ConstitutionalFloor]
    genius_score: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    vault_hash: Optional[str] = None
    human_veto_available: bool = True
    
    @property
    def is_constitutional(self) -> bool:
        """Return True if the verdict passes all constitutional floors."""
        return len(self.floors_failed) == 0 and self.state == VerdictState.SEAL
    
    @property
    def summary(self) -> str:
        """Return a human-readable summary."""
        status = "✓ CONSTITUTIONAL" if self.is_constitutional else "✗ VIOLATION"
        return f"[{status}] {self.state.value} at {self.stage.value} (G={self.genius_score:.2f})"


@dataclass
class MGIMessage:
    """
    Machine-Governance-Intelligence envelope message.
    """
    machine_layer: Dict[str, Any]      # Execution and I/O
    governance_layer: Dict[str, Any]   # Constitutional enforcement
    intelligence_layer: Dict[str, Any] # 3E cycle data
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate the MGI envelope structure."""
        errors = []
        
        if not self.machine_layer:
            errors.append("Machine layer is empty")
        if not self.governance_layer:
            errors.append("Governance layer is empty")
        if not self.intelligence_layer:
            errors.append("Intelligence layer is empty")
            
        return len(errors) == 0, errors


@dataclass
class TrinityContext:
    """
    Context spanning all three Trinity engines.
    """
    delta_context: Dict[str, Any]   # Mind/Reasoning context
    omega_context: Dict[str, Any]   # Heart/Safety context
    psi_context: Dict[str, Any]     # Soul/Judgment context
    
    @property
    def is_complete(self) -> bool:
        """Return True if all three contexts are present."""
        return all([
            self.delta_context,
            self.omega_context,
            self.psi_context
        ])


# =============================================================================
# ONTOLOGY REGISTRY
# =============================================================================

class OntologyRegistry:
    """
    Central registry for all ArifOS ontology concepts.
    
    Provides lookup and validation for all terminology.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._build_registry()
    
    def _build_registry(self):
        """Build the complete ontology registry."""
        self._trinity = {e.value: e for e in TrinityEngine}
        self._stages = {e.value: e for e in MetabolicStage}
        self._floors = {e.value: e for e in ConstitutionalFloor}
        self._verdicts = {e.value: e for e in VerdictState}
        self._patterns = {e.value: e for e in ArchitecturePattern}
        self._dials = {e.value: e for e in APEXDial}
    
    # Lookup methods
    def get_trinity(self, symbol: str) -> Optional[TrinityEngine]:
        """Get TrinityEngine by symbol (Δ, Ω, Ψ)."""
        return self._trinity.get(symbol)
    
    def get_stage(self, code: str) -> Optional[MetabolicStage]:
        """Get MetabolicStage by code (e.g., '000_INIT')."""
        return self._stages.get(code)
    
    def get_floor(self, code: str) -> Optional[ConstitutionalFloor]:
        """Get ConstitutionalFloor by code (e.g., 'F1')."""
        return self._floors.get(code)
    
    def get_verdict(self, state: str) -> Optional[VerdictState]:
        """Get VerdictState by name (e.g., 'SEAL')."""
        return self._verdicts.get(state)
    
    def get_pattern(self, code: str) -> Optional[ArchitecturePattern]:
        """Get ArchitecturePattern by code."""
        return self._patterns.get(code)
    
    def get_dial(self, symbol: str) -> Optional[APEXDial]:
        """Get APEXDial by symbol (A, P, X, E)."""
        return self._dials.get(symbol)
    
    # Validation methods
    def is_valid_stage_code(self, code: str) -> bool:
        """Validate a metabolic stage code."""
        return code in self._stages
    
    def is_valid_floor_code(self, code: str) -> bool:
        """Validate a constitutional floor code."""
        return code in self._floors
    
    def is_valid_verdict(self, state: str) -> bool:
        """Validate a verdict state."""
        return state in self._verdicts
    
    # Enumeration methods
    @property
    def all_stages(self) -> List[MetabolicStage]:
        """Return all metabolic stages in order."""
        return list(MetabolicStage)
    
    @property
    def all_floors(self) -> List[ConstitutionalFloor]:
        """Return all constitutional floors in order."""
        return list(ConstitutionalFloor)
    
    @property
    def all_verdicts(self) -> List[VerdictState]:
        """Return all verdict states."""
        return list(VerdictState)
    
    def get_stages_for_engine(self, engine: TrinityEngine) -> List[MetabolicStage]:
        """Get all stages managed by a specific Trinity engine."""
        return [s for s in MetabolicStage if s.trinity_engine == engine]
    
    def get_floors_for_stage(self, stage: MetabolicStage) -> List[ConstitutionalFloor]:
        """Get constitutional floors relevant to a specific stage."""
        # Stage-specific floor mappings
        mappings = {
            MetabolicStage.INIT: [ConstitutionalFloor.F11_COMMAND_AUTH, ConstitutionalFloor.F12_INJECTION, ConstitutionalFloor.F13_SOVEREIGN],
            MetabolicStage.SENSE: [ConstitutionalFloor.F2_TRUTH, ConstitutionalFloor.F12_INJECTION],
            MetabolicStage.REALITY: [ConstitutionalFloor.F2_TRUTH, ConstitutionalFloor.F11_COMMAND_AUTH, ConstitutionalFloor.F12_INJECTION],
            MetabolicStage.MIND: [ConstitutionalFloor.F2_TRUTH, ConstitutionalFloor.F4_CLARITY, ConstitutionalFloor.F7_HUMILITY, ConstitutionalFloor.F8_GENIUS],
            MetabolicStage.ROUTER: [ConstitutionalFloor.F1_AMANAH, ConstitutionalFloor.F2_TRUTH, ConstitutionalFloor.F4_CLARITY, ConstitutionalFloor.F13_SOVEREIGN],
            MetabolicStage.MEMORY: [ConstitutionalFloor.F4_CLARITY, ConstitutionalFloor.F7_HUMILITY, ConstitutionalFloor.F13_SOVEREIGN],
            MetabolicStage.HEART: [ConstitutionalFloor.F5_PEACE, ConstitutionalFloor.F6_EMPATHY],
            MetabolicStage.FORGE: [ConstitutionalFloor.F3_TRI_WITNESS, ConstitutionalFloor.F8_GENIUS, ConstitutionalFloor.F12_INJECTION],
            MetabolicStage.JUDGE: [ConstitutionalFloor.F3_TRI_WITNESS, ConstitutionalFloor.F10_ONTOLOGY, ConstitutionalFloor.F13_SOVEREIGN],
            MetabolicStage.VAULT: [ConstitutionalFloor.F1_AMANAH, ConstitutionalFloor.F3_TRI_WITNESS, ConstitutionalFloor.F13_SOVEREIGN]
        }
        return mappings.get(stage, [])


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def calculate_genius_score(a: float, p: float, x: float, e: float, h: float) -> float:
    """
    Calculate the Genius score G = (A × P × X × E²) × (1 - h)
    
    Args:
        a: Akal (Mind) - Reasoning quality (0.0-1.0)
        p: Presence (Peace) - Stability (0.0-1.0)
        x: Exploration - Discovery breadth (0.0-1.0)
        e: Energy - Execution capacity (0.0-1.0)
        h: Harm - Potential damage (0.0-1.0)
    
    Returns:
        Genius score G (0.0-1.0+)
    """
    return (a * p * x * (e ** 2)) * (1 - h)


def calculate_tri_witness(h: float, a: float, e: float, v: float) -> float:
    """
    Calculate the Tri-Witness score W₄ = ∜(H × A × E × V)
    
    Args:
        h: Human verification
        a: AI reasoning
        e: Evidence quality
        v: Value alignment
    
    Returns:
        Tri-Witness score W₄ (0.0-1.0)
    """
    return (h * a * e * v) ** 0.25


def validate_constitutional_floors(
    truth_tau: float,
    clarity_delta_s: float,
    empathy_kappa: float,
    humility_omega: float,
    genius_g: float
) -> Dict[ConstitutionalFloor, bool]:
    """
    Validate all threshold-based constitutional floors.
    
    Returns:
        Dictionary mapping each floor to its pass/fail status
    """
    return {
        ConstitutionalFloor.F2_TRUTH: truth_tau >= 0.99,
        ConstitutionalFloor.F4_CLARITY: clarity_delta_s <= 0.0,
        ConstitutionalFloor.F6_EMPATHY: empathy_kappa >= 0.70,
        ConstitutionalFloor.F7_HUMILITY: 0.03 <= humility_omega <= 0.05,
        ConstitutionalFloor.F8_GENIUS: genius_g >= 0.80
    }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "TrinityEngine",
    "MetabolicStage",
    "ConstitutionalFloor",
    "VerdictState",
    "ArchitecturePattern",
    "APEXDial",
    
    # Classes
    "TrinityStageMapping",
    "ConstitutionalVerdict",
    "MGIMessage",
    "TrinityContext",
    "OntologyRegistry",
    
    # Functions
    "calculate_genius_score",
    "calculate_tri_witness",
    "validate_constitutional_floors",
]


# Module version
__version__ = "2026.03.13-FORGED"

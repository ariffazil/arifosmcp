"""
core/shared/mottos.py — The 9 Mottos as Stage Meta-Transformers

This module merges and hardens:
- codebase/constants_mottos.py (full ConstitutionalMotto with metadata)
- codebase/stages/stage_motto_integration.py (stage rendering)
- core/shared/prompt_manifold.py (3×3 matrix geometry)

The 9 mottos form a cultural error-handling layer that maps to:
- 9 Stages (000-999 metabolic loop)
- 9 Paradoxes (3×3 Trinity matrix: Truth/Clarity/Humility × Care/Peace/Justice)
- 9 Floors (F1-F9 operational constraints)

Each motto is a DI___KAN, BUKAN DI___KAN pattern (Active construction, not passive receipt)
embodying the thermodynamic principle that intelligence requires work.

Ω₀ ≈ 0.04 — Structure is clear; empirical effects remain model-dependent.

DITEMPA BUKAN DIBERI 💎🔥🧠
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

# ═════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═════════════════════════════════════════════════════════════════════════════


class StageCode(str, Enum):
    """The 9 metabolic stage codes."""

    INIT = "000"
    SENSE = "111"
    THINK = "222"
    ATLAS = "333"
    EVIDENCE = "444"
    EMPATHY = "555"
    BRIDGE = "666"
    JUDGE = "888"
    SEAL = "999"


class TrinityTier(str, Enum):
    """The three trinities of the paradox matrix."""

    ALPHA = "alpha"  # Core Virtues (Truth/Care, Clarity/Peace, Humility/Justice)
    BETA = "beta"  # Implementation (Precision/Reversibility, Hierarchy/Consent, Agency/Protection)
    GAMMA = "gamma"  # Temporal/Meta (Urgency/Sustainability, Certainty/Doubt, Unity/Diversity)


class MatrixAxis(Enum):
    """The two axes of the 3×3 control matrix."""

    TRUTH = "truth"  # F2 — Examination, Clarification, Awareness
    CLARITY = "clarity"  # F4 — Exploration, Confrontation, Work
    HUMILITY = "humility"  # F7 — Protection, Calming, Forging

    CARE = "care"  # F6 — Stakeholder protection
    PEACE = "peace"  # F5 — Stability, de-escalation
    JUSTICE = "justice"  # F8/F9 — Balanced outcomes, anti-hantu


class GeometryType(Enum):
    """Geometry metaphors for cognitive routing."""

    ORTHOGONAL = "orthogonal"  # 111, 222, 444 — Independent basis vectors
    FRACTAL = "fractal"  # 333, 555 — Recursive at different scales
    TOROIDAL = "toroidal"  # 666, 888, 999 — Closing loops


# ═════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class ConstitutionalMotto:
    """
    A canonical motto in the arifOS constitutional framework.

    Each motto represents the vocative (call to action) for its
    corresponding stage, floor, and paradox cell.
    """

    id: int  # 1-9 position in matrix
    stage: StageCode  # Which metabolic stage
    stage_name: str  # Human-readable stage name

    # The motto (Malay-English code-switch)
    malay: str  # Malay original
    english: str  # English translation
    positive: str  # DI___KAN form
    negative: str  # BUKAN DI___KAN form

    # Constitutional mappings
    primary_floor: str  # Main floor (F1-F13)
    secondary_floors: list[str]  # Related floors
    paradox_cell: str  # Matrix position (e.g., "truth_care")
    trinity_tier: TrinityTier  # Which trinity

    # Geometry
    geometry: GeometryType  # orthogonal/fractal/toroidal

    # Usage context
    usage_context: str  # When to use this motto
    violation_response: str  # Message when floor fails

    def translate(self) -> str:
        """Get the English translation."""
        return self.english

    def to_dict(self) -> dict[str, str]:
        """Convert to dict for transport."""
        return {
            "malay": self.malay,
            "english": self.english,
            "positive": self.positive,
            "negative": self.negative,
            "stage": self.stage_name,
            "floor": self.primary_floor,
        }

    def __str__(self) -> str:
        return f"{self.malay} — {self.english}"

    def format_output(self, context: str = "") -> str:
        """Format motto for output with optional context."""
        if context:
            return f"{self.malay} — {self.english}\n  Context: {context}"
        return f"{self.malay} — {self.english}"

    def format_error(self, floor: str, reason: str) -> str:
        """Format as error/violation message."""
        return (
            f"[!] {floor} Floor Breach\n"
            f"   Reason: {reason}\n"
            f"   [MOTTO] {self.malay}\n"
            f"      {self.english}"
        )


@dataclass(frozen=True)
class StageMotto:
    """Simplified motto pair for a specific stage (legacy compatibility)."""

    positive: str  # The "DI[VERB]" form
    negative: str  # The "BUKAN DI[VERB]" form
    stage: str  # 000-999 stage code
    meaning: str  # English translation
    floor: str  # Primary constitutional floor

    def __str__(self) -> str:
        return f"{self.positive}, {self.negative}"

    def format_output(self, context: str = "") -> str:
        """Format motto for stage output."""
        if context:
            return f"[{self.stage}] {self.positive}, {self.negative} | {context}"
        return f"[{self.stage}] {self.positive}, {self.negative}"


@dataclass(frozen=True)
class MatrixCell:
    """A cell in the 3×3 paradox-motto matrix."""

    row: MatrixAxis  # Truth/Clarity/Humility
    col: MatrixAxis  # Care/Peace/Justice
    motto: str  # The motto for this intersection
    meaning: str  # English translation
    stage: str  # 000-999 stage code
    geometry: GeometryType
    constraint: str  # What "good" looks like at this intersection

    def to_prompt_framing(self) -> str:
        """Convert to a prompt framing constraint."""
        return (
            f"[{self.row.value.upper()} × {self.col.value.upper()}] {self.motto}: {self.constraint}"
        )


# ═════════════════════════════════════════════════════════════════════════════
# THE 9 CANONICAL MOTTOS (HARDENED)
# ═════════════════════════════════════════════════════════════════════════════

MOTTO_000_INIT = ConstitutionalMotto(
    id=9,
    stage=StageCode.INIT,
    stage_name="INIT",
    malay="DITEMPA, BUKAN DIBERI",
    english="Forged, Not Given",
    positive="DITEMPA",
    negative="BUKAN DIBERI",
    primary_floor="F1_Amanah",
    secondary_floors=["F13_Sovereign"],
    paradox_cell="humility_justice",  # Justice through forging
    trinity_tier=TrinityTier.GAMMA,
    geometry=GeometryType.TOROIDAL,
    usage_context="Session ignition and foundation - ALL work must be forged",
    violation_response="Return to the forge. Nothing is given without work.",
)
# Emoji signature for INIT: Fire (transformation begins)
MOTTO_000_INIT_EMOJI = "🔥"
MOTTO_000_INIT_HEADER = "🔥 IGNITE — DITEMPA, BUKAN DIBERI 💎"

MOTTO_111_SENSE = ConstitutionalMotto(
    id=1,
    stage=StageCode.SENSE,
    stage_name="SENSE",
    malay="DIKAJI, BUKAN DISUAPI",
    english="Examined, Not Spoon-fed",
    positive="DIKAJI",
    negative="BUKAN DISUAPI",
    primary_floor="F2_Truth",
    secondary_floors=["F10_Ontology"],
    paradox_cell="truth_care",
    trinity_tier=TrinityTier.ALPHA,
    geometry=GeometryType.ORTHOGONAL,
    usage_context="Perception and input validation - Question what you receive",
    violation_response="Examine the evidence. Do not accept blindly.",
)

MOTTO_222_THINK = ConstitutionalMotto(
    id=4,
    stage=StageCode.THINK,
    stage_name="THINK",
    malay="DIJELAJAH, BUKAN DISEKATI",
    english="Explored, Not Restricted",
    positive="DIJELAJAH",
    negative="BUKAN DISEKATI",
    primary_floor="F4_Clarity",
    secondary_floors=["F2_Truth"],
    paradox_cell="clarity_care",
    trinity_tier=TrinityTier.ALPHA,
    geometry=GeometryType.ORTHOGONAL,
    usage_context="Hypothesis generation - Explore the solution space",
    violation_response="Expand your search. Do not limit the inquiry.",
)

MOTTO_333_REASON = ConstitutionalMotto(
    id=5,
    stage=StageCode.ATLAS,
    stage_name="ATLAS/REASON",
    malay="DIJELASKAN, BUKAN DIKABURKAN",
    english="Clarified, Not Obscured",
    positive="DIJELASKAN",
    negative="BUKAN DIKABURKAN",
    primary_floor="F4_Clarity",
    secondary_floors=["F2_Truth", "F10_Ontology"],
    paradox_cell="clarity_peace",
    trinity_tier=TrinityTier.ALPHA,
    geometry=GeometryType.ORTHOGONAL,
    usage_context="Logical reasoning - Reduce entropy (dS ≤ 0)",
    violation_response="Clarify the ambiguity. Do not add confusion.",
)

MOTTO_444_SYNC = ConstitutionalMotto(
    id=2,
    stage=StageCode.EVIDENCE,
    stage_name="SYNC/EVIDENCE",
    malay="DIHADAPI, BUKAN DITANGGUHI",
    english="Faced, Not Postponed",
    positive="DIHADAPI",
    negative="BUKAN DITANGGUHI",
    primary_floor="F3_Consensus",
    secondary_floors=["F2_Truth", "F4_Clarity"],
    paradox_cell="clarity_justice",
    trinity_tier=TrinityTier.ALPHA,
    geometry=GeometryType.TOROIDAL,
    usage_context="Tri-witness sync - Confront tension directly",
    violation_response="Face the tension now. Postponement creates debt.",
)

MOTTO_555_EMPATHY = ConstitutionalMotto(
    id=7,
    stage=StageCode.EMPATHY,
    stage_name="EMPATHY",
    malay="DIDAMAIKAN, BUKAN DIPANASKAN",
    english="Calmed, Not Inflamed",
    positive="DIDAMAIKAN",
    negative="BUKAN DIPANASKAN",
    primary_floor="F5_Peace2",
    secondary_floors=["F6_Empathy"],
    paradox_cell="humility_peace",
    trinity_tier=TrinityTier.GAMMA,
    geometry=GeometryType.FRACTAL,
    usage_context="Stakeholder impact analysis - Cool the system",
    violation_response="De-escalate. Do not add heat to the system.",
)

MOTTO_666_ALIGN = ConstitutionalMotto(
    id=8,
    stage=StageCode.BRIDGE,
    stage_name="ALIGN/BRIDGE",
    malay="DIJAGA, BUKAN DIABAIKAN",
    english="Protected, Not Neglected",
    positive="DIJAGA",
    negative="BUKAN DIABAIKAN",
    primary_floor="F6_Empathy",
    secondary_floors=["F5_Peace2", "F9_AntiHantu"],
    paradox_cell="humility_care",
    trinity_tier=TrinityTier.GAMMA,
    geometry=GeometryType.TOROIDAL,
    usage_context="Alignment and safety - Guard the vulnerable",
    violation_response="Protect the weakest stakeholder. Neglect is harm.",
)

MOTTO_777_FORGE = ConstitutionalMotto(
    id=6,
    stage=StageCode.ATLAS,  # Mapped to ATLAS for Genius
    stage_name="EUREKA FORGE",
    malay="DIUSAHAKAN, BUKAN DIHARAPI",
    english="Worked For, Not Merely Hoped For",
    positive="DIUSAHAKAN",
    negative="BUKAN DIHARAPI",
    primary_floor="F8_Genius",
    secondary_floors=["F4_Clarity"],
    paradox_cell="clarity_justice",
    trinity_tier=TrinityTier.BETA,
    geometry=GeometryType.TOROIDAL,
    usage_context="Phase transition and Genius - Work creates value",
    violation_response="Reasoning requires work. Hope is not a strategy.",
)

MOTTO_888_JUDGE = ConstitutionalMotto(
    id=3,
    stage=StageCode.JUDGE,
    stage_name="APEX JUDGE METABOLIC",
    malay="DISEDARKAN, BUKAN DIYAKINKAN",
    english="Made Aware, Not Over-assured",
    positive="DISEDARKAN",
    negative="BUKAN DIYAKINKAN",
    primary_floor="F7_Humility",
    secondary_floors=["F2_Truth", "F3_TriWitness"],
    paradox_cell="truth_justice",
    trinity_tier=TrinityTier.ALPHA,
    geometry=GeometryType.TOROIDAL,
    usage_context="Final verdict with uncertainty band - Admit not-knowing",
    violation_response="Acknowledge uncertainty. Do not claim false certainty.",
)

MOTTO_999_SEAL = ConstitutionalMotto(
    id=9,
    stage=StageCode.SEAL,
    stage_name="SEAL",
    malay="DITEMPA, BUKAN DIBERI",
    english="Forged, Not Given",
    positive="DITEMPA",
    negative="BUKAN DIBERI",
    primary_floor="F1_Amanah",
    secondary_floors=["F3_TriWitness", "F13_Sovereign"],
    paradox_cell="humility_justice",
    trinity_tier=TrinityTier.GAMMA,
    geometry=GeometryType.TOROIDAL,
    usage_context="Immutable commit - The seal is earned through work",
    violation_response="Nothing is sealed without passing through fire.",
)
# Emoji signature for SEAL: Diamond (hardened result) + Brain (intelligence forged)
MOTTO_999_SEAL_EMOJI = "💎"
MOTTO_999_SEAL_HEADER = "💎🧠 SEAL — DITEMPA, BUKAN DIBERI 🔒"


# ═════════════════════════════════════════════════════════════════════════════
# REGISTRIES
# ═════════════════════════════════════════════════════════════════════════════

ALL_MOTTOS: dict[StageCode, ConstitutionalMotto] = {
    StageCode.INIT: MOTTO_000_INIT,
    StageCode.SENSE: MOTTO_111_SENSE,
    StageCode.THINK: MOTTO_222_THINK,
    StageCode.ATLAS: MOTTO_333_REASON,
    StageCode.EVIDENCE: MOTTO_444_SYNC,
    StageCode.EMPATHY: MOTTO_555_EMPATHY,
    StageCode.BRIDGE: MOTTO_666_ALIGN,
    StageCode.JUDGE: MOTTO_888_JUDGE,
    StageCode.SEAL: MOTTO_999_SEAL,
}

# Floor-to-motto mapping for failure responses (The 9 Anthem)
ERROR_MOTTOS: dict[str, str] = {
    "F1": "DIJAGA, BUKAN DIABAIKAN",  # Amanah: Safeguarded, not neglected
    "F2": "DIKAJI, BUKAN DISUAPI",  # Truth: Examined, not spoon-fed
    "F4": "DIJELASKAN, BUKAN DIKABURKAN",  # Clarity: Clarified, not obscured
    "F5": "DIDAMAIKAN, BUKAN DIPANASKAN",  # Peace: Calmed, not inflamed
    "F6": "DIJAGA, BUKAN DIABAIKAN",  # Empathy: Protected, not neglected
    "F7": "DISEDARKAN, BUKAN DIYAKINKAN",  # Humility: Made aware, not over-assured
    "F8": "DIUSAHAKAN, BUKAN DIHARAPI",  # Genius: Worked for, not hoped
    "F9": "DIJAGA, BUKAN DIABAIKAN",  # Anti-Hantu: Protected, not neglected
    "F10": "DIKAJI, BUKAN DISUAPI",  # Ontology: Examined, not spoon-fed
    "EXPLORE": "DIJELAJAH, BUKAN DISEKATI",  # Exploration: Explored, not restricted
    "ENERGY": "DIUSAHAKAN, BUKAN DIHARAPI",  # Energy: Worked for, not hoped
    "FOUNDATION": "DITEMPA, BUKAN DIBERI",  # Foundation: Forged, not given
}

# Constitutional motto objects by floor
MOTTOS_BY_FLOOR: dict[str, ConstitutionalMotto] = {
    "F1": MOTTO_666_ALIGN,  # DIJAGA, BUKAN DIABAIKAN
    "F2": MOTTO_111_SENSE,  # DIKAJI, BUKAN DISUAPI
    "F4": MOTTO_333_REASON,  # DIJELASKAN, BUKAN DIKABURKAN
    "F5": MOTTO_555_EMPATHY,  # DIDAMAIKAN, BUKAN DIPANASKAN
    "F6": MOTTO_666_ALIGN,  # DIJAGA, BUKAN DIABAIKAN
    "F7": MOTTO_888_JUDGE,  # DISEDARKAN, BUKAN DIYAKINKAN
    "F8": MOTTO_777_FORGE,  # DIUSAHAKAN, BUKAN DIHARAPI
}

STAGE_MOTTO_MAP: dict[str, StageMotto] = {
    "000_INIT": StageMotto("DITEMPA", "BUKAN DIBERI", "000/999", "Forged, Not Given", "F1 Amanah"),
    "111_SENSE": StageMotto(
        "DIKAJI", "BUKAN DISUAPI", "111", "Examined, Not Spoon-fed", "F2 Truth"
    ),
    "222_THINK": StageMotto(
        "DIJELAJAH", "BUKAN DISEKATI", "222", "Explored, Not Restricted", "F4 Clarity"
    ),
    "333_REASON": StageMotto(
        "DIJELASKAN", "BUKAN DIKABURKAN", "333", "Clarified, Not Obscured", "F4 Clarity"
    ),
    "444_SYNC": StageMotto(
        "DIHADAPI", "BUKAN DITANGGUHI", "444", "Faced, Not Postponed", "F3 Tri-Witness"
    ),
    "555_EMPATHY": StageMotto(
        "DIDAMAIKAN", "BUKAN DIPANASKAN", "555", "Calmed, Not Inflamed", "F5 Peace²"
    ),
    "666_ALIGN": StageMotto(
        "DIJAGA", "BUKAN DIABAIKAN", "666", "Protected, Not Neglected", "F6 Empathy"
    ),
    "777_FORGE": StageMotto(
        "DIUSAHAKAN", "BUKAN DIHARAPI", "777", "Worked, Not Hoped", "F8 Genius"
    ),
    "777_EUREKA_FORGE": StageMotto(
        "DIUSAHAKAN", "BUKAN DIHARAPI", "777", "Worked, Not Hoped", "F8 Genius"
    ),
    "888_JUDGE": StageMotto(
        "DISEDARKAN", "BUKAN DIYAKINKAN", "888", "Made Aware, Not Over-assured", "F7 Humility"
    ),
    "888_APEX_JUDGE": StageMotto(
        "DISEDARKAN", "BUKAN DIYAKINKAN", "888", "Made Aware, Not Over-assured", "F7 Humility"
    ),
    "999_SEAL": StageMotto("DITEMPA", "BUKAN DIBERI", "000/999", "Forged, Not Given", "F1 Amanah"),
}

STAGE_MOTTO_ORDER: list[str] = [
    "000_INIT",
    "111_SENSE",
    "222_THINK",
    "333_REASON",
    "444_SYNC",
    "555_EMPATHY",
    "666_ALIGN",
    "777_FORGE",
    "888_JUDGE",
    "999_SEAL",
]

TRINITY_MOTTOS = {
    TrinityTier.ALPHA: {
        "malay": "DIKAJI, DIJELASKAN, DISEDARKAN",
        "english": "Examined, Clarified, Aware",
        "meaning": "Core Virtues: Truth through examination, Peace through clarity, Justice through awareness",
    },
    TrinityTier.BETA: {
        "malay": "DIJELAJAH, DIHADAPI, DIUSAHAKAN",
        "english": "Explored, Faced, Worked",
        "meaning": "Implementation: Reasoning requires exploration, action requires facing, value requires work",
    },
    TrinityTier.GAMMA: {
        "malay": "DIJAGA, DIDAMAIKAN, DITEMPA",
        "english": "Protected, Calmed, Forged",
        "meaning": "Wisdom: Care protects, Peace calms, Seal forges",
    },
}


# ═════════════════════════════════════════════════════════════════════════════
# 3×3 PARADOX MATRIX
# ═════════════════════════════════════════════════════════════════════════════

PARADOX_MATRIX: dict[tuple[MatrixAxis, MatrixAxis], MatrixCell] = {
    # TRUTH ROW
    (MatrixAxis.TRUTH, MatrixAxis.CARE): MatrixCell(
        row=MatrixAxis.TRUTH,
        col=MatrixAxis.CARE,
        motto="DIKAJI, BUKAN DISUAPI",
        meaning="Examined, not spoon-fed",
        stage="111_SENSE",
        geometry=GeometryType.ORTHOGONAL,
        constraint="Care must be grounded in examination, not assumed",
    ),
    (MatrixAxis.TRUTH, MatrixAxis.PEACE): MatrixCell(
        row=MatrixAxis.TRUTH,
        col=MatrixAxis.PEACE,
        motto="DIJELASKAN, BUKAN DIKABURKAN",
        meaning="Clarified, not obscured",
        stage="333_REASON",
        geometry=GeometryType.ORTHOGONAL,
        constraint="Peace comes from clarity, not obscuring truth",
    ),
    (MatrixAxis.TRUTH, MatrixAxis.JUSTICE): MatrixCell(
        row=MatrixAxis.TRUTH,
        col=MatrixAxis.JUSTICE,
        motto="DISEDARKAN, BUKAN DIYAKINKAN",
        meaning="Made aware, not over-assured",
        stage="888_JUDGE",
        geometry=GeometryType.TOROIDAL,
        constraint="Justice requires awareness of limits, not false certainty",
    ),
    # CLARITY ROW
    (MatrixAxis.CLARITY, MatrixAxis.CARE): MatrixCell(
        row=MatrixAxis.CLARITY,
        col=MatrixAxis.CARE,
        motto="DIJELAJAH, BUKAN DISEKATI",
        meaning="Explored, not restricted",
        stage="222_THINK",
        geometry=GeometryType.ORTHOGONAL,
        constraint="Care requires exploration, not premature restriction",
    ),
    (MatrixAxis.CLARITY, MatrixAxis.PEACE): MatrixCell(
        row=MatrixAxis.CLARITY,
        col=MatrixAxis.PEACE,
        motto="DIHADAPI, BUKAN DITANGGUHI",
        meaning="Faced, not postponed",
        stage="444_SYNC",
        geometry=GeometryType.TOROIDAL,
        constraint="Peace comes from facing tension, not postponing it",
    ),
    (MatrixAxis.CLARITY, MatrixAxis.JUSTICE): MatrixCell(
        row=MatrixAxis.CLARITY,
        col=MatrixAxis.JUSTICE,
        motto="DIUSAHAKAN, BUKAN DIHARAPI",
        meaning="Worked for, not merely hoped",
        stage="777_FORGE",
        geometry=GeometryType.TOROIDAL,
        constraint="Justice requires effort, not wishful thinking",
    ),
    # HUMILITY ROW
    (MatrixAxis.HUMILITY, MatrixAxis.CARE): MatrixCell(
        row=MatrixAxis.HUMILITY,
        col=MatrixAxis.CARE,
        motto="DIJAGA, BUKAN DIABAIKAN",
        meaning="Protected, not neglected",
        stage="666_ALIGN",
        geometry=GeometryType.TOROIDAL,
        constraint="Care means protection with humility, not neglect",
    ),
    (MatrixAxis.HUMILITY, MatrixAxis.PEACE): MatrixCell(
        row=MatrixAxis.HUMILITY,
        col=MatrixAxis.PEACE,
        motto="DIDAMAIKAN, BUKAN DIPANASKAN",
        meaning="Calmed, not inflamed",
        stage="555_EMPATHY",
        geometry=GeometryType.FRACTAL,
        constraint="Peace comes from calming, not escalating",
    ),
    (MatrixAxis.HUMILITY, MatrixAxis.JUSTICE): MatrixCell(
        row=MatrixAxis.HUMILITY,
        col=MatrixAxis.JUSTICE,
        motto="DITEMPA, BUKAN DIBERI",
        meaning="Forged, not given",
        stage="000_INIT/999_SEAL",
        geometry=GeometryType.TOROIDAL,
        constraint="Justice is forged through process, not granted",
    ),
}


# ═════════════════════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════


def get_motto_by_stage(stage: str) -> ConstitutionalMotto | None:
    """Get motto by stage code (000, 111, 000_INIT, etc.)."""
    stage_aliases = {
        "777_EUREKA_FORGE": "777_FORGE",
        "888_APEX_JUDGE": "888_JUDGE",
    }
    stage = stage_aliases.get(stage, stage)

    # Normalize stage code
    stage_clean = stage.replace("_INIT", "").replace("_SENSE", "").replace("_THINK", "")
    stage_clean = stage_clean.replace("_REASON", "").replace("_SYNC", "").replace("_EMPATHY", "")
    stage_clean = stage_clean.replace("_ALIGN", "").replace("_BRIDGE", "").replace("_JUDGE", "")
    stage_clean = stage_clean.replace("_SEAL", "").replace("_FORGE", "")

    try:
        return ALL_MOTTOS.get(StageCode(stage_clean))
    except ValueError:
        return None


def get_motto_by_floor(floor: str) -> ConstitutionalMotto | None:
    """Get motto by floor (F1, F2, etc.)."""
    floor_key = floor.upper().replace("_", "").replace("FLOOR", "").replace("F", "")
    return MOTTOS_BY_FLOOR.get(f"F{floor_key}")


def get_motto_by_paradox(paradox_cell: str) -> ConstitutionalMotto | None:
    """Get motto by paradox cell name (truth_care, clarity_peace, etc.)."""
    for motto in ALL_MOTTOS.values():
        if motto.paradox_cell == paradox_cell:
            return motto
    return None


def get_mottos_by_tier(tier: TrinityTier) -> list[ConstitutionalMotto]:
    """Get all mottos for a trinity tier."""
    return [m for m in ALL_MOTTOS.values() if m.trinity_tier == tier]


def get_trinity_motto(tier: TrinityTier) -> dict[str, str]:
    """Get aggregate motto for a trinity tier."""
    return TRINITY_MOTTOS.get(tier, {})


def get_motto_for_stage(stage_code: str) -> StageMotto:
    """Get simplified StageMotto for a given stage code."""
    return STAGE_MOTTO_MAP.get(stage_code, STAGE_MOTTO_MAP["000_INIT"])


def get_all_stage_mottos() -> list[StageMotto]:
    """Get all stage mottos in canonical order (000 → 999)."""
    return [STAGE_MOTTO_MAP[key] for key in STAGE_MOTTO_ORDER]


def format_all_stage_mottos() -> str:
    """Format all stage mottos as a multi-line output string."""
    lines = []
    for motto in get_all_stage_mottos():
        lines.append(f"[{motto.stage}] {motto.positive}, {motto.negative} | {motto.meaning}")
    return "\n".join(lines)


def format_stage_output(stage: str, verdict: str, context: str = "") -> str:
    """Format a stage output with its motto."""
    motto = get_motto_by_stage(stage)
    if not motto:
        return f"[{stage}] {verdict}"

    lines = [
        f"[{motto.stage.value} {motto.stage_name}] {motto.malay}",
        f"    {motto.english}",
    ]
    if context:
        lines.append(f"    Context: {context}")
    lines.append(f"    Verdict: {verdict}")
    return "\n".join(lines)


def format_floor_violation(floor: str, reason: str) -> str:
    """Format a floor violation with corrective motto."""
    motto = get_motto_by_floor(floor)
    if not motto:
        return f"[!] {floor} Floor Breach: {reason}"
    return motto.format_error(floor, reason)


def format_stage_header(stage_code: str) -> str:
    """Render the stage header with motto (from stage_motto_integration)."""
    motto = get_motto_by_stage(stage_code)
    if not motto:
        return f"[{stage_code}] Stage"

    return f"""
======================================================================
  [{motto.stage.value}] {motto.stage_name:<10}  {motto.malay}
  {motto.english}
======================================================================
"""


def format_stage_message(stage_code: str, context: str = "") -> str:
    """Format a stage message with motto."""
    motto = get_motto_by_stage(stage_code)
    if not motto:
        return f"[{stage_code}] {context}"

    prefix = {
        "000": "[IGNITE]",
        "111": "[?]",
        "222": "[WORK]",
        "333": "[MAP]",
        "444": "[SEARCH]",
        "555": "[SHIELD]",
        "666": "[BRIDGE]",
        "888": "[SCALE]",
        "999": "[LOCK]",
    }.get(motto.stage.value, "[*]")

    return f"{prefix} {motto.malay}\n   {context}"


def get_full_pipeline_chant() -> str:
    """Get the full rhythmic chant of all 9 mottos."""
    positives = [m.positive for m in ALL_MOTTOS.values()]
    negatives = [m.negative for m in ALL_MOTTOS.values()]

    # Remove duplicates while preserving order
    seen_pos = set()
    seen_neg = set()
    unique_pos = []
    unique_neg = []

    for p, n in zip(positives, negatives, strict=False):
        if p not in seen_pos:
            seen_pos.add(p)
            unique_pos.append(p)
        if n not in seen_neg:
            seen_neg.add(n)
            unique_neg.append(n)

    return ", ".join(unique_pos) + "\n" + ", ".join(unique_neg)


def get_geometry_path(start_stage: str, end_stage: str) -> list[str]:
    """Get the geometric path between two stages."""
    stage_order = [
        "000_INIT",
        "111_SENSE",
        "222_THINK",
        "333_REASON",
        "444_SYNC",
        "555_EMPATHY",
        "666_ALIGN",
        "777_FORGE",
        "888_JUDGE",
        "999_SEAL",
    ]

    try:
        start_idx = stage_order.index(start_stage)
        end_idx = stage_order.index(end_stage)
    except ValueError:
        return []

    if start_idx <= end_idx:
        return stage_order[start_idx : end_idx + 1]
    else:
        # Toroidal wrap-around
        return stage_order[start_idx:] + stage_order[: end_idx + 1]


def get_geometry_type(stage: str) -> GeometryType:
    """Get the geometry type for a given stage."""
    motto = get_motto_by_stage(stage)
    return motto.geometry if motto else GeometryType.ORTHOGONAL


def get_matrix_cell(row: MatrixAxis, col: MatrixAxis) -> MatrixCell | None:
    """Get the matrix cell at the given intersection."""
    return PARADOX_MATRIX.get((row, col))


def get_init_gate_header() -> str:
    """
    Get the INIT gate header with fire emoji and DITEMPA motto.

    The beginning of the constitutional journey - transformation starts here.
    """
    return """
================================================================================
  🔥 IGNITE — DITEMPA, BUKAN DIBERI 💎
  [000_INIT] Forged, Not Given
  
  The fire is lit. Nothing enters without passing through flame.
  All work must be forged. Nothing is given freely.
================================================================================
    """.strip()


def get_seal_gate_header() -> str:
    """
    Get the SEAL gate header with diamond/brain emojis and DITEMPA motto.

    The end of the constitutional journey - the hardened result.
    """
    return """
================================================================================
  💎🧠 SEAL — DITEMPA, BUKAN DIBERI 🔒
  [999_SEAL] Forged, Not Given
  
  The diamond is cut. Intelligence forged through constitutional fire.
  The seal is earned. Nothing leaves without proof of work.
================================================================================
    """.strip()


def get_ditempa_bookends() -> tuple[str, str]:
    """
    Get the DITEMPA bookend headers for INIT and SEAL.

    Returns:
        (init_header, seal_header) with emojis
    """
    return ("🔥 IGNITE — DITEMPA, BUKAN DIBERI 💎", "💎🧠 SEAL — DITEMPA, BUKAN DIBERI 🔒")


def get_failure_anthem() -> str:
    """
    Get the complete 9-motto failure response anthem.

    This is the cultural error-handling language that maps
    each floor failure to a rhyming Nusantara motto.
    """
    return """
================================================================================
           THE AAA MCP FAILURE RESPONSE ANTHEM                    
================================================================================
  DITEMPA, BUKAN DIBERI        -- Forged, not given (Foundation)   
  DIKAJI, BUKAN DISUAPI        -- Examined, not spoon-fed (Truth)  
  DIJELAJAH, BUKAN DISEKATI    -- Explored, not restricted         
  DIJELASKAN, BUKAN DIKABURKAN -- Clarified, not obscured (Clarity)
  DIHADAPI, BUKAN DITANGGUHI   -- Faced, not postponed             
  DIUSAHAKAN, BUKAN DIHARAPI   -- Worked for, not hoped (Energy)   
  DIJAGA, BUKAN DIABAIKAN      -- Safeguarded, not neglected       
  DIDAMAIKAN, BUKAN DIPANASKAN -- Calmed, not inflamed (Peace)     
  DISEDARKAN, BUKAN DIYAKINKAN -- Made aware, not over-assured     
================================================================================
    """.strip()


def format_failure_response(floor: str, reason: str, use_motto: bool = True) -> str:
    """
    Format a floor failure with Nusantara cultural response.

    Example:
        [!] F7 Humility Breach
            Confidence too high for available evidence.
            DISEDARKAN, BUKAN DIYAKINKAN.
    """
    motto_text = ERROR_MOTTOS.get(floor, "DITEMPA, BUKAN DIBERI")

    if use_motto:
        return f"""[!] {floor} Floor Breach
    Reason: {reason}
    {motto_text}"""
    else:
        return f"[!] {floor} Floor Breach: {reason}"


def render_full_pipeline_output(stages_data: list[tuple[str, str, str]] = None) -> str:
    """
    Render the complete 000-999 pipeline with all mottos.

    Args:
        stages_data: List of (stage_code, verdict, context) tuples
    """
    if stages_data is None:
        stages_data = [
            ("000", "IGNITED", ""),
            ("111", "SEAL", "12 entities examined"),
            ("222", "SEAL", "4 hypotheses generated"),
            ("333", "SEAL", "route: HARD"),
            ("444", "SEAL", "grounded in 3 sources"),
            ("555", "SEAL", "5 stakeholders mapped"),
            ("666", "SEAL", "alignment 0.94"),
            ("888", "SEAL", "omega_0=0.04"),
            ("999", "SEALED", "hash: a3f7..."),
        ]

    lines = ["=" * 70, "  arifOS CONSTITUTIONAL PIPELINE — 9 MOTTOS", "=" * 70, ""]

    for stage_code, verdict, context in stages_data:
        motto = get_motto_by_stage(stage_code)
        if motto:
            lines.append(f"[{stage_code}] {motto.stage_name:8} | {verdict:8} | {motto.malay}")
            if context:
                lines.append(f"                              {context}")

    lines.extend(["", "=" * 70, "  DITEMPA BUKAN DIBERI — The loop is complete.", "=" * 70])

    return "\n".join(lines)


# ═════════════════════════════════════════════════════════════════════════════
# PROMPT MANIFOLD CLASS (from prompt_manifold.py)
# ═════════════════════════════════════════════════════════════════════════════


class PromptManifold:
    """
    Control surface for prompt framing using the 3×3 matrix.

    This class implements the "matrix language frame" concept:
    the 9-motto architecture provides the structural skeleton into
    which all task-specific prompts are embedded.
    """

    def __init__(self):
        self.omega_0 = 0.04  # Uncertainty bound
        self.matrix = PARADOX_MATRIX

    def get_cell(self, row: MatrixAxis, col: MatrixAxis) -> MatrixCell | None:
        """Get the matrix cell at the given intersection."""
        return self.matrix.get((row, col))

    def get_by_stage(self, stage: str) -> MatrixCell | None:
        """Get matrix cell by 000-999 stage code."""
        for cell in self.matrix.values():
            if stage in cell.stage:
                return cell
        return None

    def get_prompt_frame(self, stage: str, task: str = "") -> str:
        """Generate a prompt framing for a given stage."""
        cell = self.get_by_stage(stage)
        if not cell:
            return f"[{stage}] Process with constitutional care."

        frame_parts = [
            f"[{cell.stage}] {cell.motto}",
            f"Geometry: {cell.geometry.value}",
            f"Constraint: {cell.constraint}",
        ]

        if task:
            frame_parts.append(f"Task: {task}")

        frame_parts.append(f"Ω₀ ≈ {self.omega_0}: Operate within humility bounds.")

        return "\n".join(frame_parts)

    def validate_output(self, stage: str, output: str) -> dict[str, Any]:
        """Validate that output adheres to the matrix constraints."""
        cell = self.get_by_stage(stage)
        if not cell:
            return {"adherence_score": 1.0, "violations": [], "suggestions": []}

        violations = []
        suggestions = []

        # Heuristic checks
        if cell.row == MatrixAxis.CLARITY and cell.col == MatrixAxis.JUSTICE:
            if "work" not in output.lower() and "effort" not in output.lower():
                suggestions.append("Add explicit effort/work language (DIUSAHAKAN)")

        if cell.row == MatrixAxis.TRUTH and cell.col == MatrixAxis.JUSTICE:
            if "uncertain" not in output.lower() and "aware" not in output.lower():
                suggestions.append("Add humility/uncertainty acknowledgment (DISEDARKAN)")

        adherence = 1.0 - (len(violations) * 0.2)

        return {
            "adherence_score": max(0.0, adherence),
            "violations": violations,
            "suggestions": suggestions,
            "cell": cell,
        }


# ═════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    "StageCode",
    "TrinityTier",
    "MatrixAxis",
    "GeometryType",
    # Classes
    "ConstitutionalMotto",
    "StageMotto",
    "MatrixCell",
    "PromptManifold",
    # Constants - 9 Mottos
    "MOTTO_000_INIT",
    "MOTTO_111_SENSE",
    "MOTTO_222_THINK",
    "MOTTO_333_REASON",
    "MOTTO_444_SYNC",
    "MOTTO_555_EMPATHY",
    "MOTTO_666_ALIGN",
    "MOTTO_777_FORGE",
    "MOTTO_888_JUDGE",
    "MOTTO_999_SEAL",
    # Constants - Emoji signatures
    "MOTTO_000_INIT_EMOJI",
    "MOTTO_000_INIT_HEADER",
    "MOTTO_999_SEAL_EMOJI",
    "MOTTO_999_SEAL_HEADER",
    # Registries
    "ALL_MOTTOS",
    "MOTTOS_BY_FLOOR",
    "ERROR_MOTTOS",
    "STAGE_MOTTO_MAP",
    "STAGE_MOTTO_ORDER",
    "TRINITY_MOTTOS",
    "PARADOX_MATRIX",
    # Functions
    "get_motto_by_stage",
    "get_motto_by_floor",
    "get_motto_by_paradox",
    "get_mottos_by_tier",
    "get_trinity_motto",
    "get_motto_for_stage",
    "get_all_stage_mottos",
    "format_all_stage_mottos",
    "format_stage_output",
    "format_floor_violation",
    "format_failure_response",
    "get_failure_anthem",
    "get_init_gate_header",  # NEW: Fire emoji INIT
    "get_seal_gate_header",  # NEW: Diamond/Brain SEAL
    "get_ditempa_bookends",  # NEW: Both headers
    "format_stage_header",
    "format_stage_message",
    "get_full_pipeline_chant",
    "get_geometry_path",
    "get_geometry_type",
    "get_matrix_cell",
    "render_full_pipeline_output",
]

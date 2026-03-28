"""
arifOS Ontology - Unified Terminology for the Canon-13 Regime.

This module defines the canonical terminology used throughout the arifOS system,
ensuring consistent naming and understanding across all components.

The ontology is organized into domains:
- MGI: Machine -> Governance -> Intelligence envelope
- 3E: Exploration -> Entropy -> Eureka cycle
- 13-Floors: Metabolic loop floors F1-F13
- Verdicts: Seal types and verdict states
- Constitution: Canon-13 articles
"""

from enum import Enum
from typing import Dict, List, Any


# =============================================================================
# MGI (Machine -> Governance -> Intelligence) Envelope
# =============================================================================

class MGITerminology:
    """
    Terminology for the MGI envelope system.
    
    The MGI envelope is the canonical wrapper for all tool outputs,
    providing full provenance and constitutional compliance tracking.
    """
    
    # Layers
    MACHINE_LAYER = "Machine Layer"
    GOVERNANCE_LAYER = "Governance Layer"
    INTELLIGENCE_LAYER = "Intelligence Layer"
    
    # Machine Layer components
    SESSION_ID = "session_id"
    GOVERNANCE_TOKEN = "governance_token"
    TOKEN_TYPE = "token_type"
    TIMESTAMP_UTC = "timestamp_utc"
    CONTINUITY_STATUS = "continuity_status"
    PARENT_TOKEN = "parent_token"
    MERKLE_LEAF = "merkle_leaf"
    
    # Token types
    TOKEN_ANCHOR = "ANCHOR"
    TOKEN_JUDGE = "JUDGE"
    TOKEN_WITNESS = "WITNESS"
    TOKEN_KERNEL = "KERNEL"
    TOKEN_VAULT = "VAULT"
    
    # Continuity statuses
    CONTINUITY_FRESH = "FRESH"
    CONTINUITY_CONTINUOUS = "CONTINUOUS"
    CONTINUITY_RESUMED = "RESUMED"
    CONTINUITY_FRAGMENTED = "FRAGMENTED"
    
    # Governance Layer components
    ACTIVE_FLOORS = "active_floors"
    CONSTITUTIONAL_ARTICLES = "constitutional_articles"
    VALIDATION_RESULT = "validation_result"
    VIOLATIONS = "violations"
    JUDGE_OVERRIDE = "judge_override"
    HOLD_STATE_ID = "hold_state_id"
    FLOOR_METRICS = "floor_metrics"
    
    # Validation results
    VALIDATION_VALID = "VALID"
    VALIDATION_VIOLATION = "VIOLATION"
    VALIDATION_WARNING = "WARNING"
    VALIDATION_PENDING = "PENDING"
    
    # Intelligence Layer components
    EVIDENCE_BUNDLES = "evidence_bundles"
    REASONING_CHAIN = "reasoning_chain"
    SYNTHESIS_HASH = "synthesis_hash"
    CONFIDENCE_SCORE = "confidence_score"
    CONFIDENCE_INTERVAL = "confidence_interval"
    UNCERTAINTY_OMEGA = "uncertainty_omega"
    UNSTABLE_ASSUMPTIONS = "unstable_assumptions"
    KNOWLEDGE_GAPS = "knowledge_gaps"
    EVIDENCE_GRADE = "evidence_grade"
    
    # Evidence grades
    EVIDENCE_PRIMARY = "PRIMARY"
    EVIDENCE_SECONDARY = "SECONDARY"
    EVIDENCE_TERTIARY = "TERTIARY"
    EVIDENCE_ANECDOTAL = "ANECDOTAL"


# =============================================================================
# 3E Cycle (Exploration -> Entropy -> Eureka)
# =============================================================================

class Cycle3ETerminology:
    """
    Terminology for the 3E cognitive metabolism cycle.
    
    The 3E cycle represents the flow from data acquisition through
    processing to insight generation.
    """
    
    # Phases
    PHASE_EXPLORATION = "Exploration"
    PHASE_ENTROPY = "Entropy"
    PHASE_EUREKA = "Eureka"
    
    # Exploration components
    SEARCH_ENGINES = "search_engines"
    FETCH_METHODS = "fetch_methods"
    EVIDENCE_BUNDLE = "evidence_bundle"
    QUERY = "query"
    SOURCES = "sources"
    
    # Search engines
    SEARCH_WEB = "WEB"
    SEARCH_VECTOR = "VECTOR"
    SEARCH_LOCAL = "LOCAL"
    SEARCH_ACADEMIC = "ACADEMIC"
    SEARCH_NEWS = "NEWS"
    SEARCH_IMAGE = "IMAGE"
    SEARCH_CODE = "CODE"
    
    # Fetch methods
    FETCH_HTTP_GET = "HTTP_GET"
    FETCH_HTTP_POST = "HTTP_POST"
    FETCH_BROWSER = "BROWSER"
    FETCH_API = "API"
    FETCH_DATABASE = "DATABASE"
    FETCH_FILESYSTEM = "FILESYSTEM"
    
    # Source attribution
    SOURCE_ID = "source_id"
    SOURCE_TYPE = "source_type"
    SOURCE_URI = "uri"
    SOURCE_TITLE = "title"
    SOURCE_AUTHOR = "author"
    SOURCE_CREDIBILITY = "credibility_score"
    
    # Entropy components
    CONTRADICTIONS = "contradictions"
    NODES_CREATED = "nodes_created"
    EDGES_CREATED = "edges_created"
    METABOLIZATION_SCORE = "metabolization_score"
    UNCERTAINTY_DELTA = "uncertainty_delta"
    
    # Contradiction types
    CONTRADICTION_DIRECT = "DIRECT"
    CONTRADICTION_IMPLICIT = "IMPLICIT"
    CONTRADICTION_TEMPORAL = "TEMPORAL"
    CONTRADICTION_SCOPE = "SCOPE"
    CONTRADICTION_SOURCE = "SOURCE"
    
    # Vector graph
    VECTOR_NODE = "VectorNode"
    VECTOR_EDGE = "VectorEdge"
    NODE_ID = "node_id"
    EDGE_ID = "edge_id"
    VECTOR = "vector"
    CONTENT = "content"
    CONTENT_HASH = "content_hash"
    RELATIONSHIP_TYPE = "relationship_type"
    STRENGTH = "strength"
    
    # Eureka components
    TRI_WITNESS = "tri_witness"
    SYNTHESIS = "synthesis"
    VERDICT = "verdict"
    CONFIDENCE_FINAL = "confidence_final"
    
    # Witness types
    WITNESS_EARTH = "EARTH"
    WITNESS_AI = "AI"
    WITNESS_LOGIC = "LOGIC"


# =============================================================================
# 13 Floors Metabolic Loop
# =============================================================================

class FloorsTerminology:
    """
    Terminology for the 13-floor metabolic loop.
    
    Each floor represents a distinct phase of operation processing.
    """
    
    # Floor names
    F1_ANCHOR = "F1_ANCHOR"
    F2_QUERY = "F2_QUERY"
    F3_EXPLORE = "F3_EXPLORE"
    F4_METABOLIZE = "F4_METABOLIZE"
    F5_SYNTHESIZE = "F5_SYNTHESIZE"
    F6_CALCULATE = "F6_CALCULATE"
    F7_CONSTITUTE = "F7_CONSTITUTE"
    F8_RATIFY = "F8_RATIFY"
    F9_SEAL = "F9_SEAL"
    F10_PERSIST = "F10_PERSIST"
    F11_REPORT = "F11_REPORT"
    F12_MONITOR = "F12_MONITOR"
    F13_CLOSE = "F13_CLOSE"
    
    # Floor descriptions
    FLOOR_DESCRIPTIONS: Dict[str, str] = {
        F1_ANCHOR: "Session anchoring and initialization",
        F2_QUERY: "Query validation and preprocessing",
        F3_EXPLORE: "Evidence exploration and gathering",
        F4_METABOLIZE: "Evidence metabolization and contradiction detection",
        F5_SYNTHESIZE: "Tri-Witness synthesis",
        F6_CALCULATE: "Metric calculation (κᵣ, Peace², G)",
        F7_CONSTITUTE: "Constitutional validation",
        F8_RATIFY: "Ratification check",
        F9_SEAL: "Seal assignment",
        F10_PERSIST: "Vector persistence",
        F11_REPORT: "Report generation",
        F12_MONITOR: "Health monitoring",
        F13_CLOSE: "Session closure"
    }
    
    # Floor states
    FLOOR_INACTIVE = "INACTIVE"
    FLOOR_ACTIVE = "ACTIVE"
    FLOOR_COMPLETE = "COMPLETE"
    FLOOR_HOLD = "HOLD"
    FLOOR_ERROR = "ERROR"
    FLOOR_BYPASSED = "BYPASSED"
    
    # Canonical coefficients
    KAPPA_R = "kappa_r"  # Stakeholder impact
    PEACE_SQUARED = "peace_squared"  # Stability
    G_COEFFICIENT = "G_coefficient"  # Efficiency


# =============================================================================
# Verdicts and Seals
# =============================================================================

class VerdictTerminology:
    """
    Terminology for verdicts and seals.
    
    The three canonical seals determine operation outcomes.
    """
    
    # Canonical seals
    SEAL_STEEL = "STEEL"
    SEAL_HOLD = "HOLD"
    SEAL_VOID = "VOID"
    SEAL_PARTIAL = "PARTIAL"
    
    # Seal meanings
    SEAL_MEANINGS: Dict[str, str] = {
        SEAL_STEEL: "Operation successful, confident, compliant",
        SEAL_HOLD: "Uncertainty detected, requires escalation",
        SEAL_VOID: "Contradiction or violation, operation invalid",
        SEAL_PARTIAL: "Partial success with acknowledged limitations"
    }
    
    # Verdict states
    VERDICT_STEEL_CERTAIN = "STEEL_CERTAIN"
    VERDICT_STEEL_PROBABLE = "STEEL_PROBABLE"
    VERDICT_HOLD_888 = "HOLD_888"
    VERDICT_HOLD_PARTIAL = "HOLD_PARTIAL"
    VERDICT_VOID_CONTRADICTION = "VOID_CONTRADICTION"
    VERDICT_VOID_VIOLATION = "VOID_VIOLATION"
    
    # 888 Judge
    JUDGE_888 = "888_JUDGE"
    RATIFICATION = "ratification"
    RATIFICATION_APPROVE = "APPROVE"
    RATIFICATION_REJECT = "REJECT"
    RATIFICATION_MODIFY = "MODIFY"
    RATIFICATION_EXTEND = "EXTEND"
    RATIFICATION_ESCALATE = "ESCALATE"


# =============================================================================
# Canon-13 Constitution
# =============================================================================

class ConstitutionTerminology:
    """
    Terminology for the Canon-13 Constitution.
    
    The 13 articles define the fundamental rules of the regime.
    """
    
    # Articles
    A1_STEEL = "A1_STEEL"
    A2_HOLD = "A2_HOLD"
    A3_VOID = "A3_VOID"
    A4_PARTIAL = "A4_PARTIAL"
    A5_JUDGE = "A5_JUDGE"
    A6_TRACE = "A6_TRACE"
    A7_EQUITY = "A7_EQUITY"
    A8_MEMORY = "A8_MEMORY"
    A9_EPOCH = "A9_EPOCH"
    A10_ENTROPY = "A10_ENTROPY"
    A11_SYNTHESIS = "A11_SYNTHESIS"
    A12_PEACE = "A12_PEACE"
    A13_G = "A13_G"
    
    # Article descriptions
    ARTICLE_DESCRIPTIONS: Dict[str, str] = {
        A1_STEEL: "Default to transparency",
        A2_HOLD: "Escalate uncertainty",
        A3_VOID: "Void on contradiction",
        A4_PARTIAL: "Partial truth acknowledgment",
        A5_JUDGE: "Human-in-the-loop trigger",
        A6_TRACE: "Provenance requirement",
        A7_EQUITY: "Stakeholder fairness",
        A8_MEMORY: "Vector persistence",
        A9_EPOCH: "Temporal anchoring",
        A10_ENTROPY: "Uncertainty quantification",
        A11_SYNTHESIS: "Tri-Witness requirement",
        A12_PEACE: "Stability metric",
        A13_G: "Efficiency coefficient"
    }
    
    @classmethod
    def get_article_description(cls, article_code: str) -> str:
        """Get description for an article code."""
        return cls.ARTICLE_DESCRIPTIONS.get(article_code, "Unknown article")


# =============================================================================
# Thermodynamic Budget
# =============================================================================

class ThermodynamicTerminology:
    """
    Terminology for thermodynamic budget management.
    
    Tracks computational and cognitive resource consumption.
    """
    
    # Budget types
    BUDGET_TOKENS = "tokens"
    BUDGET_OPERATIONS = "operations"
    BUDGET_TIME = "time"
    BUDGET_ENTROPY = "entropy"
    
    # Budget status
    BUDGET_HEALTHY = "healthy"
    BUDGET_WARNING = "warning"
    BUDGET_EXHAUSTED = "exhausted"
    
    # Metrics
    MAX_TOKENS = "max_tokens"
    USED_TOKENS = "used_tokens"
    MAX_OPERATIONS = "max_operations"
    USED_OPERATIONS = "used_operations"
    MAX_TIME = "max_time_seconds"
    USED_TIME = "used_time_seconds"
    ENTROPY_LIMIT = "entropy_limit"
    CURRENT_ENTROPY = "current_entropy"


# =============================================================================
# Merkle Chain
# =============================================================================

class MerkleTerminology:
    """
    Terminology for Merkle chain provenance.
    
    Cryptographic verification of operation history.
    """
    
    # Components
    MERKLE_NODE = "MerkleNode"
    MERKLE_TREE = "MerkleTree"
    MERKLE_CHAIN = "MerkleChain"
    
    # Node fields
    NODE_ID = "node_id"
    DATA_HASH = "data_hash"
    PARENT_HASH = "parent_hash"
    OPERATION_TYPE = "operation_type"
    
    # Tree fields
    SESSION_ID = "session_id"
    ROOT_HASH = "root_hash"
    LEAF_HASH = "leaf_hash"
    
    # Verification
    CHAIN_VALID = "valid"
    CHAIN_ERRORS = "errors"
    NODE_COUNT = "node_count"


# =============================================================================
# Unified Ontology Access
# =============================================================================

class ArifOSOntology:
    """
    Unified access to all arifOS terminology.
    
    Provides a single point of access for all canonical terms.
    """
    
    MGI = MGITerminology
    CYCLE_3E = Cycle3ETerminology
    FLOORS = FloorsTerminology
    VERDICT = VerdictTerminology
    CONSTITUTION = ConstitutionTerminology
    THERMODYNAMIC = ThermodynamicTerminology
    MERKLE = MerkleTerminology
    
    @classmethod
    def get_all_terms(cls) -> Dict[str, Any]:
        """Get all terminology as a dictionary."""
        return {
            "MGI": {
                "layers": [
                    cls.MGI.MACHINE_LAYER,
                    cls.MGI.GOVERNANCE_LAYER,
                    cls.MGI.INTELLIGENCE_LAYER
                ],
                "token_types": [
                    cls.MGI.TOKEN_ANCHOR,
                    cls.MGI.TOKEN_JUDGE,
                    cls.MGI.TOKEN_WITNESS,
                    cls.MGI.TOKEN_KERNEL,
                    cls.MGI.TOKEN_VAULT
                ],
                "continuity_statuses": [
                    cls.MGI.CONTINUITY_FRESH,
                    cls.MGI.CONTINUITY_CONTINUOUS,
                    cls.MGI.CONTINUITY_RESUMED,
                    cls.MGI.CONTINUITY_FRAGMENTED
                ]
            },
            "3E_CYCLE": {
                "phases": [
                    cls.CYCLE_3E.PHASE_EXPLORATION,
                    cls.CYCLE_3E.PHASE_ENTROPY,
                    cls.CYCLE_3E.PHASE_EUREKA
                ],
                "witness_types": [
                    cls.CYCLE_3E.WITNESS_EARTH,
                    cls.CYCLE_3E.WITNESS_AI,
                    cls.CYCLE_3E.WITNESS_LOGIC
                ]
            },
            "13_FLOORS": {
                "floors": list(cls.FLOORS.FLOOR_DESCRIPTIONS.keys()),
                "coefficients": [
                    cls.FLOORS.KAPPA_R,
                    cls.FLOORS.PEACE_SQUARED,
                    cls.FLOORS.G_COEFFICIENT
                ]
            },
            "VERDICTS": {
                "seals": list(cls.VERDICT.SEAL_MEANINGS.keys()),
                "seal_meanings": cls.VERDICT.SEAL_MEANINGS
            },
            "CONSTITUTION": {
                "articles": list(cls.CONSTITUTION.ARTICLE_DESCRIPTIONS.keys()),
                "article_descriptions": cls.CONSTITUTION.ARTICLE_DESCRIPTIONS
            }
        }


# Export main ontology class
__all__ = [
    "ArifOSOntology",
    "MGITerminology",
    "Cycle3ETerminology",
    "FloorsTerminology",
    "VerdictTerminology",
    "ConstitutionTerminology",
    "ThermodynamicTerminology",
    "MerkleTerminology",
]

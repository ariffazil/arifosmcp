"""
3E Cycle Models - Exploration -> Entropy -> Eureka

The 3E cycle represents the cognitive metabolism of the arifOS system:
- Exploration: Data acquisition, search, fetch (input gathering)
- Entropy: Metabolization, contradiction handling, vector storage (processing)
- Eureka: Synthesis, verdict formation, insight delivery (output generation)
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Union
from enum import Enum
from pydantic import BaseModel, Field, field_validator
import hashlib
import json


class SearchEngine(str, Enum):
    """Available search engines for Exploration phase."""
    WEB = "WEB"                    # General web search
    VECTOR = "VECTOR"              # Vector database search
    LOCAL = "LOCAL"                # Local file/document search
    ACADEMIC = "ACADEMIC"          # Academic/scholarly search
    NEWS = "NEWS"                  # News/current events search
    IMAGE = "IMAGE"                # Image search
    CODE = "CODE"                  # Code repository search


class FetchMethod(str, Enum):
    """Methods for fetching data during Exploration."""
    HTTP_GET = "HTTP_GET"
    HTTP_POST = "HTTP_POST"
    BROWSER = "BROWSER"
    API = "API"
    DATABASE = "DATABASE"
    FILESYSTEM = "FILESYSTEM"


class SourceAttribution(BaseModel):
    """
    Attribution for a single source of evidence.
    
    Tracks provenance, credibility, and access metadata for any
    piece of evidence gathered during Exploration.
    """
    source_id: str = Field(
        ...,
        description="Unique identifier for this source"
    )
    source_type: str = Field(
        ...,
        description="Type of source (web, document, database, etc.)"
    )
    uri: Optional[str] = Field(
        default=None,
        description="URI/URL of the source"
    )
    title: Optional[str] = Field(
        default=None,
        description="Title or name of source"
    )
    author: Optional[str] = Field(
        default=None,
        description="Author or creator of source"
    )
    publication_date: Optional[datetime] = Field(
        default=None,
        description="Date of publication"
    )
    access_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this source was accessed"
    )
    search_engine: Optional[SearchEngine] = Field(
        default=None,
        description="Search engine used to find this source"
    )
    fetch_method: Optional[FetchMethod] = Field(
        default=None,
        description="Method used to fetch this source"
    )
    credibility_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Credibility rating (0-1)"
    )
    raw_content_hash: Optional[str] = Field(
        default=None,
        description="Hash of raw content for verification"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional source metadata"
    )


class EvidenceBundle(BaseModel):
    """
    A bundle of evidence gathered during Exploration.
    
    EvidenceBundles are the primary output of the Exploration phase
    and input to the Entropy phase. They contain structured evidence
    with full provenance tracking.
    """
    bundle_id: str = Field(
        ...,
        description="Unique identifier for this evidence bundle"
    )
    query: str = Field(
        ...,
        description="Original query that generated this bundle"
    )
    sources: List[SourceAttribution] = Field(
        default_factory=list,
        description="Attributed sources in this bundle"
    )
    raw_evidence: Dict[str, Any] = Field(
        default_factory=dict,
        description="Raw evidence data by source_id"
    )
    aggregated_content: str = Field(
        default="",
        description="Aggregated and deduplicated content"
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Aggregate confidence in this evidence"
    )
    coverage_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="How well evidence covers the query space"
    )
    contradictions_detected: int = Field(
        default=0,
        ge=0,
        description="Number of contradictions within this bundle"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this bundle was created"
    )
    exploration_phase: str = Field(
        default="complete",
        description="Status of exploration for this bundle"
    )
    
    def compute_content_hash(self) -> str:
        """Compute hash of aggregated content for verification."""
        return hashlib.sha256(
            self.aggregated_content.encode()
        ).hexdigest()
    
    def add_source(self, source: SourceAttribution, content: Any) -> "EvidenceBundle":
        """Add a source with its content to this bundle."""
        self.sources.append(source)
        self.raw_evidence[source.source_id] = content
        return self


class ContradictionType(str, Enum):
    """Types of contradictions detected during Entropy."""
    DIRECT = "DIRECT"              # Direct factual contradiction
    IMPLICIT = "IMPLICIT"          # Implied contradiction
    TEMPORAL = "TEMPORAL"          # Time-based contradiction
    SCOPE = "SCOPE"                # Scope/context contradiction
    SOURCE = "SOURCE"              # Source credibility contradiction


class Contradiction(BaseModel):
    """
    A detected contradiction between evidence items.
    
    Contradictions are identified during the Entropy phase and
    must be resolved or flagged for the Eureka phase.
    """
    contradiction_id: str = Field(..., description="Unique contradiction ID")
    type: ContradictionType = Field(..., description="Type of contradiction")
    source_a: str = Field(..., description="First conflicting source ID")
    source_b: str = Field(..., description="Second conflicting source ID")
    description: str = Field(..., description="Description of the contradiction")
    severity: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Severity of contradiction (0-1)"
    )
    resolution: Optional[str] = Field(
        default=None,
        description="Proposed or applied resolution"
    )


class VectorNode(BaseModel):
    """
    A node in the vector memory graph (Atlas).
    
    Represents a concept, claim, or piece of knowledge stored
    in the vector database with full metadata.
    """
    node_id: str = Field(..., description="Unique node identifier")
    vector: Optional[List[float]] = Field(
        default=None,
        description="Embedding vector"
    )
    content: str = Field(..., description="Text content of node")
    content_hash: str = Field(..., description="Hash of content")
    evidence_bundle_id: Optional[str] = Field(
        default=None,
        description="Source evidence bundle"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VectorEdge(BaseModel):
    """
    An edge in the vector memory graph (Atlas).
    
    Represents a relationship between two nodes with
    relationship type and strength.
    """
    edge_id: str = Field(..., description="Unique edge identifier")
    source_node: str = Field(..., description="Source node ID")
    target_node: str = Field(..., description="Target node ID")
    relationship_type: str = Field(..., description="Type of relationship")
    strength: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Relationship strength (0-1)"
    )
    bidirectional: bool = Field(
        default=False,
        description="Whether edge is bidirectional"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExplorationPhase(BaseModel):
    """
    Exploration Phase: Data acquisition, search, fetch.
    
    The first phase of the 3E cycle. Gathers evidence from
    multiple sources using various search and fetch methods.
    """
    phase_id: str = Field(..., description="Unique phase identifier")
    query: str = Field(..., description="Original exploration query")
    search_engines_used: List[SearchEngine] = Field(default_factory=list)
    fetch_methods_used: List[FetchMethod] = Field(default_factory=list)
    evidence_bundle: Optional[EvidenceBundle] = Field(
        default=None,
        description="Resulting evidence bundle"
    )
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = Field(default=None)
    status: str = Field(default="in_progress")
    
    def complete(self, bundle: EvidenceBundle) -> "ExplorationPhase":
        """Mark exploration as complete with evidence bundle."""
        self.evidence_bundle = bundle
        self.end_time = datetime.utcnow()
        self.status = "complete"
        return self


class EntropyPhase(BaseModel):
    """
    Entropy Phase: Metabolization, contradiction handling, vector storage.
    
    The second phase of the 3E cycle. Processes evidence from
    Exploration, detects contradictions, and stores in vector memory.
    """
    phase_id: str = Field(..., description="Unique phase identifier")
    input_bundle_id: str = Field(..., description="Input evidence bundle ID")
    contradictions: List[Contradiction] = Field(default_factory=list)
    nodes_created: List[VectorNode] = Field(default_factory=list)
    edges_created: List[VectorEdge] = Field(default_factory=list)
    metabolization_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="How well evidence was metabolized"
    )
    uncertainty_delta: float = Field(
        default=0.0,
        description="Change in uncertainty (negative = more certain)"
    )
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = Field(default=None)
    status: str = Field(default="in_progress")
    
    def add_contradiction(self, contradiction: Contradiction) -> "EntropyPhase":
        """Add a detected contradiction."""
        self.contradictions.append(contradiction)
        return self
    
    def add_node(self, node: VectorNode) -> "EntropyPhase":
        """Add a created vector node."""
        self.nodes_created.append(node)
        return self
    
    def add_edge(self, edge: VectorEdge) -> "EntropyPhase":
        """Add a created vector edge."""
        self.edges_created.append(edge)
        return self
    
    def complete(self) -> "EntropyPhase":
        """Mark entropy phase as complete."""
        self.end_time = datetime.utcnow()
        self.status = "complete"
        return self


class WitnessType(str, Enum):
    """Types of witnesses in Tri-Witness synthesis."""
    EARTH = "EARTH"                # External/ground truth evidence
    AI = "AI"                      # AI model confidence
    LOGIC = "LOGIC"                # Logical inference chain


class WitnessStatement(BaseModel):
    """
    A statement from one witness in Tri-Witness synthesis.
    """
    witness_type: WitnessType = Field(..., description="Type of witness")
    statement: str = Field(..., description="The witness statement")
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Witness confidence"
    )
    evidence_refs: List[str] = Field(
        default_factory=list,
        description="References to supporting evidence"
    )


class EurekaPhase(BaseModel):
    """
    Eureka Phase: Synthesis, verdict formation, insight delivery.
    
    The third phase of the 3E cycle. Synthesizes processed evidence
    into a verdict, insight, or actionable output.
    """
    phase_id: str = Field(..., description="Unique phase identifier")
    entropy_phase_id: str = Field(..., description="Input entropy phase ID")
    tri_witness: List[WitnessStatement] = Field(
        default_factory=list,
        description="Tri-Witness statements"
    )
    synthesis: str = Field(
        default="",
        description="Synthesized conclusion"
    )
    verdict: Optional[str] = Field(
        default=None,
        description="Final verdict"
    )
    confidence_final: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Final confidence score"
    )
    unstable_assumptions: List[str] = Field(default_factory=list)
    knowledge_gaps: List[str] = Field(default_factory=list)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = Field(default=None)
    status: str = Field(default="in_progress")
    
    def add_witness(self, witness: WitnessStatement) -> "EurekaPhase":
        """Add a witness statement."""
        self.tri_witness.append(witness)
        return self
    
    def complete(self, verdict: str, confidence: float) -> "EurekaPhase":
        """Mark eureka phase as complete with verdict."""
        self.verdict = verdict
        self.confidence_final = confidence
        self.end_time = datetime.utcnow()
        self.status = "complete"
        return self


class Cycle3E(BaseModel):
    """
    Complete 3E Cycle: Exploration -> Entropy -> Eureka.
    
    Encapsulates the full cognitive metabolism cycle from
    data acquisition through processing to insight generation.
    """
    cycle_id: str = Field(..., description="Unique cycle identifier")
    query: str = Field(..., description="Original query")
    exploration: Optional[ExplorationPhase] = Field(default=None)
    entropy: Optional[EntropyPhase] = Field(default=None)
    eureka: Optional[EurekaPhase] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    status: str = Field(default="initialized")
    
    def start_exploration(self, exploration: ExplorationPhase) -> "Cycle3E":
        """Start exploration phase."""
        self.exploration = exploration
        self.status = "exploring"
        return self
    
    def start_entropy(self, entropy: EntropyPhase) -> "Cycle3E":
        """Start entropy phase."""
        self.entropy = entropy
        self.status = "metabolizing"
        return self
    
    def start_eureka(self, eureka: EurekaPhase) -> "Cycle3E":
        """Start eureka phase."""
        self.eureka = eureka
        self.status = "synthesizing"
        return self
    
    def complete(self) -> "Cycle3E":
        """Mark entire cycle as complete."""
        self.completed_at = datetime.utcnow()
        self.status = "complete"
        return self

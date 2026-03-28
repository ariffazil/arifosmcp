from __future__ import annotations

import uuid
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

StatusState = Literal["SUCCESS", "PARTIAL", "SABAR", "VOID", "ERROR"]
Stage = Literal["111_SENSE", "222_REALITY", "333_MIND"]
Verdict = Literal["SEAL", "SABAR", "VOID"]

ErrorCode = Literal[
    "DNS_FAIL",
    "TLS_FAIL",
    "TIMEOUT",
    "WAF_BLOCK",
    "HTTP_4XX",
    "HTTP_5XX",
    "ENGINE_422",
    "NO_RESULTS",
    "SCHEMA_FAIL",
    "PARSE_FAIL",
    "COERCED_MODE",
    "RENDER_FAIL",
]


class classproperty(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


class StatusError(BaseModel):
    code: ErrorCode
    detail: str
    recoverable: bool = True
    hint: str = ""


class BundleStatus(BaseModel):
    model_config = ConfigDict(ignored_types=(classproperty,))

    state: StatusState
    stage: Stage
    verdict: Verdict
    message: str = ""
    label: str | None = None
    errors: list[StatusError] = Field(default_factory=list)

    # Legacy attributes for test compatibility
    @classproperty
    def COMPLETE(cls):
        return cls(state="SUCCESS", stage="222_REALITY", verdict="SEAL", label="COMPLETE")

    @classproperty
    def PENDING(cls):
        return cls(state="SABAR", stage="111_SENSE", verdict="SABAR", label="PENDING")

    @classproperty
    def ERROR(cls):
        return cls(state="ERROR", stage="111_SENSE", verdict="VOID", label="ERROR")


class Policy(BaseModel):
    obey_robots: bool = True
    allow_paywalls: bool = False
    allow_login: bool = False
    max_redirects: int = 10
    max_hops: int = 3


class BundleInput(BaseModel):
    type: Literal["query", "url"]
    value: str
    mode: Literal["auto", "search", "fetch"] = "auto"
    top_k: int = 5
    fetch_top_k: int = 2
    render: Literal["auto", "never", "always"] = "auto"
    budget_ms: int = 15000
    policy: Policy = Field(default_factory=Policy)


class Actor(BaseModel):
    actor_id: str = "anonymous"
    role: str = "user"
    auth_state: Literal["unverified", "verified"] = "unverified"
    authority_level: Literal["anonymous", "user", "admin", "apex"] = "anonymous"
    token_fingerprint: str | None = None


class Claim(BaseModel):
    type: str = "statement"
    text: str
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    confidence: float = 1.0


class SearchResult(BaseModel):
    engine: str
    query: str
    status_code: int = 200
    results: list[dict[str, Any]] = Field(default_factory=list)
    error: str | None = None
    latency_ms: float = 0.0
    request_params: dict[str, Any] = Field(default_factory=dict)
    response_diagnostics: dict[str, Any] = Field(default_factory=dict)


class FetchResult(BaseModel):
    url: str
    status_code: int | None = None
    content_type: str | None = None
    content_length: int = 0
    raw_content: str | None = None
    structured_data: dict[str, Any] = Field(default_factory=dict)
    latency_ms: dict[str, float] = Field(default_factory=dict)  # dns, connect, ttfb, total
    exception_class: str | None = None
    error_message: str | None = None
    redirects: int = 0
    final_url: str | None = None
    headers_subset: dict[str, str] = Field(default_factory=dict)
    render_fallback_used: bool = False


class EvidenceBundle(BaseModel):
    id: str = Field(default_factory=lambda: f"eb-{uuid.uuid4().hex[:8]}")
    status: BundleStatus = Field(default_factory=lambda: BundleStatus.PENDING)
    input: BundleInput = Field(default_factory=lambda: BundleInput(type="query", value="INIT"))
    actor: Actor = Field(default_factory=Actor)
    claims: list[Claim] = Field(default_factory=list)
    results: list[SearchResult | FetchResult] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)


class AtlasNode(BaseModel):
    id: str
    type: Literal["URL", "DOCUMENT", "CLAIM", "ENTITY", "TOPIC", "ENGINE"]
    metadata: dict[str, Any] = Field(default_factory=dict)


class AtlasEdge(BaseModel):
    source: str
    target: str
    type: Literal["DERIVED_FROM", "SUPPORTS", "CONTRADICTS", "MENTIONS", "SAME_AS"]
    weight: float = 1.0


class RealityAtlas(BaseModel):
    nodes: list[AtlasNode] = Field(default_factory=list)
    edges: list[AtlasEdge] = Field(default_factory=list)
    delta: dict[str, Any] | None = None


class DuplexReport(BaseModel):
    search_health: dict[str, Any] = Field(default_factory=dict)
    search_winner: str | None = None
    fetch_recommendation: str | None = None

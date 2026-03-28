"""
arifosmcp/init_000/__init__.py

arifOS init 000 — Session binding via provider soul + runtime truth.

4 tables:
- provider_soul_profiles  : routing archetype
- deployments              : runtime truth
- session_anchors         : per-session snapshot
- drift_events             : mismatch log
"""

from arifosmcp.init_000.models import init_db, reset_db, SCHEMA_SQL
from arifosmcp.init_000.db import (
    get_deployment,
    get_provider_soul,
    create_session_anchor,
    get_session_anchor,
    end_session_anchor,
    log_drift_event,
    get_drift_events_for_session,
    load_seeds_from_dir,
)
from arifosmcp.init_000.schemas import (
    SELF_CLAIM_BOUNDARY_V1,
    ALLOWED_ROLES,
    DRIFT_EVENT_TYPES,
)
from arifosmcp.init_000.tools import (
    init_anchor_v1,
    get_deployment as get_deployment_tool,
    get_provider_soul as get_provider_soul_tool,
    get_session_anchor as get_session_anchor_tool,
    log_drift_event as log_drift_event_tool,
)

__all__ = [
    "init_db",
    "reset_db",
    "get_deployment",
    "get_provider_soul",
    "create_session_anchor",
    "get_session_anchor",
    "end_session_anchor",
    "log_drift_event",
    "get_drift_events_for_session",
    "load_seeds_from_dir",
    "SELF_CLAIM_BOUNDARY_V1",
    "ALLOWED_ROLES",
    "DRIFT_EVENT_TYPES",
    "init_anchor_v1",
    "get_deployment_tool",
    "get_provider_soul_tool",
    "get_session_anchor_tool",
    "log_drift_event_tool",
]

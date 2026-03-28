"""Lazy exports for shared constitutional utilities.

Importing ``core.shared`` used to eagerly import physics, atlas, types, crypto,
and guards, which pulled large ML dependencies into unrelated code paths.
Keep this package light and resolve symbols lazily on first access.
"""

from __future__ import annotations

from importlib import import_module

_ATLAS_EXPORTS = {
    "ATLAS",
    "GPV",
    "Lambda",
    "Lane",
    "Phi",
    "Theta",
    "classify",
    "classify_query",
    "route",
    "route_query",
}

_PHYSICS_EXPORTS = {
    "ConstitutionalTensor",
    "DISTRESS_SIGNALS",
    "G",
    "G_from_dial",
    "GeniusDial",
    "Omega_0",
    "Peace2",
    "PeaceSquared",
    "Stakeholder",
    "TrinityTensor",
    "UncertaintyBand",
    "W_3",
    "W_3_check",
    "W_3_from_tensor",
    "clarity_ratio",
    "delta_S",
    "empathy_coeff",
    "entropy_delta",
    "geometric_mean",
    "genius_score",
    "humility_band",
    "identify_stakeholders",
    "is_cooling",
    "kalman_gain",
    "kappa_r",
    "peace_squared",
    "pi",
    "std_dev",
    "tri_witness",
}

_TYPE_EXPORTS = {
    "AgiMetrics",
    "ApexMetrics",
    "AsiMetrics",
    "FloorScores",
    "ThoughtChain",
    "ThoughtNode",
    "Verdict",
}

_CRYPTO_EXPORTS = {
    "ed25519_sign",
    "ed25519_verify",
    "generate_session_id",
    "merkle_root",
    "sha256_hash",
    "sha256_hash_dict",
}

_GUARD_EXPORTS = {
    "detect_hantu",
    "validate_ontology",
}

__all__ = sorted(
    _ATLAS_EXPORTS | _PHYSICS_EXPORTS | _TYPE_EXPORTS | _CRYPTO_EXPORTS | _GUARD_EXPORTS
)


def __getattr__(name: str):
    if name in _ATLAS_EXPORTS:
        return getattr(import_module(".atlas", __name__), name)
    if name in _PHYSICS_EXPORTS:
        return getattr(import_module(".physics", __name__), name)
    if name in _TYPE_EXPORTS:
        return getattr(import_module(".types", __name__), name)
    if name in _CRYPTO_EXPORTS:
        return getattr(import_module(".crypto", __name__), name)
    if name in _GUARD_EXPORTS:
        return getattr(import_module(".guards", __name__), name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))

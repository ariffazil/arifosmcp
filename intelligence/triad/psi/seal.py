"""
arifosmcp.intelligence/triad/psi/seal.py — Stage 999 Vault
Commit to VAULT999 + Phoenix-72.
"""

from arifosmcp.core.kernel import kernel
from arifosmcp.core.organs import seal as core_seal
from arifosmcp.core.shared.physics import (
    ConstitutionalTensor,
    GeniusDial,
    Peace2,
    TrinityTensor,
    UncertaintyBand,
)


async def seal(
    session_id: str,
    task_summary: str,
    was_modified: bool = False,
    verdict: str | None = None,
) -> dict:
    """
    STAGE 999: Immutability.
    Seal the session and commit to the vault.

    Args:
        verdict: Pre-verified verdict from the Amanah Handshake (apex_judge
                 governance_token). When supplied, the kernel audit still runs
                 for observability but the vault records the Judge-signed verdict,
                 not the audit re-evaluation.
    """
    # 1. Run a final audit on the summary (observability)
    audit_res = kernel.audit(action=task_summary, context="FINAL_SEAL", severity="high")
    final_verdict = verdict if verdict is not None else audit_res.verdict.value
    if final_verdict in {"HOLD", "HOLD_888"}:
        final_verdict = "888_HOLD"

    # 2. Call the canonical core organ for cryptographic sealing
    # We pass placeholders for agi/asi as they are transient in this stateless call
    # but the core now handles the persistence.
    receipt = await core_seal(
        judge_output={"verdict": final_verdict, "W_3": 1.0, "genius_G": 0.9},
        agi_tensor=ConstitutionalTensor(
            witness=TrinityTensor(H=1.0, A=1.0, S=1.0),
            entropy_delta=0.0,
            humility=UncertaintyBand(omega_0=0.04),
            genius=GeniusDial(A=1.0, P=1.0, X=1.0, E=1.0),
            peace=Peace2({}),
            empathy=1.0,
            truth_score=1.0,
        ),
        asi_output={"peace_squared": 1.0},
        session_id=session_id,
        query=task_summary,
        authority="JUDGE",
    )

    # 3. Log to the witness ledger (H+A+E consensus)
    # The record is now dual-logged: once in the core JSONL and once in the Witness ledger.
    kernel.vault.log_witness(
        session_id=session_id,
        agent_id="JUDGE",
        stage="999_SEAL",
        statement=task_summary,
        verdict=final_verdict,
    )

    # Phoenix-72 logic is now handled internally by core_seal (SABAR status)
    status_msg = "sealed" if final_verdict == "SEAL" else "partial"
    if hasattr(receipt, "status") and receipt.status == "SABAR":
        status_msg = "cooling"

    return {
        "verdict": final_verdict,
        "audit_cross_check": audit_res.verdict.value,
        "status": status_msg,
        "vault_id": getattr(receipt, "seal_id", f"V999-{session_id[:8]}"),
        "cooling": "Phoenix-72 initialized" if was_modified else "None",
        "entry_hash": getattr(receipt, "entry_hash", None),
    }

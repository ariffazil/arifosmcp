"""
arifosmcp.intelligence/triad/delta/anchor.py — Stage 000 Ignition
Anchor session + F12 injection scan.
"""


async def anchor(session_id: str, user_id: str, context: str, jurisdiction: str = "GLOBAL") -> dict:
    """
    STAGE 000: Establishing Authority and Defense.
    Scan context for injection (F12) and establish session.
    """
    from arifosmcp.core.lifecycle import KernelState

    from arifosmcp.core.kernel import kernel

    # Initialize session through lifecycle manager
    session = kernel.lifecycle.init_session(
        session_id=session_id, user_id=user_id, jurisdiction=jurisdiction, context=context
    )

    # Run constitutional audit
    audit_res = kernel.audit(action="SESSION_IGNITION", context=context, severity="low")

    # Log the event to Vault
    kernel.vault.log_witness(
        session_id=session_id,
        agent_id="ARCHITECT",
        stage="000_INIT",
        statement=f"Ignition attempt for user {user_id}",
        verdict=audit_res.verdict.value,
    )

    # Register session in thermo budget and get APEX snapshot
    kernel.thermo.open_session(session_id)
    thermo_snap = kernel.thermo.record_step(
        session_id=session_id,
        delta_s=audit_res.delta_s,
    )

    return {
        "status": "success" if session.state != KernelState.VOID else "void",
        "session_id": session.session_id,
        "state": session.state.value,
        "verdict": audit_res.verdict.value,
        "telemetry": {
            "created_at": session.created_at.isoformat(),
            "pass_rate": audit_res.pass_rate,
            "dS": audit_res.delta_s,
        },
        "apex_output": thermo_snap.as_apex_output(),
    }

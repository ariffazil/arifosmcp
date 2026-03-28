"""
core/governance/apex_notification.py — 888_HOLD Sovereign Notification Bridge

When the Governance layer emits HOLD, this bridge proactively notifies
the Sovereign via n8n webhook, Telegram, or APEX Dashboard push.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class NotificationChannel(str, Enum):
    N8N_WEBHOOK = "n8n_webhook"
    TELEGRAM = "telegram"
    APEX_DASHBOARD = "apex_dashboard"
    LOG_ONLY = "log_only"


class HoldReason(str, Enum):
    F13_SOVEREIGN_REQUIRED = "F13_SOVEREIGN_REQUIRED"
    F11_AUTH_CONTINUITY_FAILED = "F11_AUTH_CONTINUITY_FAILED"
    HIGH_STAKES_OPERATION = "HIGH_STAKES_OPERATION"
    CONSTITUTIONAL_VIOLATION = "CONSTITUTIONAL_VIOLATION"
    UNCERTAINTY_EXCEEDED = "UNCERTAINTY_EXCEEDED"
    MANUAL_HOLD = "MANUAL_HOLD"


@dataclass
class HoldEvent:
    session_id: str
    reason: HoldReason
    issue_label: str
    context: dict[str, Any]
    actor_id: str = "anonymous"
    authority_level: str = "anonymous"
    tool: str = "unknown"
    stage: str = "888_JUDGE"
    timestamp: float = field(default_factory=time.time)
    evidence_bundle: dict[str, Any] | None = None
    telemetry: dict[str, Any] = field(default_factory=dict)


class APEXNotificationBridge:
    def __init__(self):
        self.n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL", "")
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        self.apex_dashboard_url = os.getenv("APEX_DASHBOARD_URL", "")
        self.notification_timeout = float(os.getenv("NOTIFICATION_TIMEOUT", "10.0"))
        self._enabled_channels = self._resolve_enabled_channels()

    def _resolve_enabled_channels(self) -> list[NotificationChannel]:
        channels = [NotificationChannel.LOG_ONLY]
        if self.n8n_webhook_url:
            channels.append(NotificationChannel.N8N_WEBHOOK)
        if self.telegram_bot_token and self.telegram_chat_id:
            channels.append(NotificationChannel.TELEGRAM)
        if self.apex_dashboard_url:
            channels.append(NotificationChannel.APEX_DASHBOARD)
        return channels

    async def emit_sovereign_hold(
        self, event: HoldEvent, channels: list[NotificationChannel] | None = None
    ) -> dict[str, Any]:
        target_channels = channels or self._enabled_channels
        results = {}

        for channel in target_channels:
            try:
                if channel == NotificationChannel.N8N_WEBHOOK:
                    results[channel.value] = await self._send_n8n_webhook(event)
                elif channel == NotificationChannel.TELEGRAM:
                    results[channel.value] = await self._send_telegram(event)
                elif channel == NotificationChannel.APEX_DASHBOARD:
                    results[channel.value] = await self._send_apex_dashboard(event)
                elif channel == NotificationChannel.LOG_ONLY:
                    results[channel.value] = self._log_hold(event)
            except Exception as e:
                logger.error(f"Notification failed for {channel}: {e}")
                results[channel.value] = {"success": False, "error": str(e)}

        return {
            "hold_emitted": True,
            "session_id": event.session_id,
            "reason": event.reason.value,
            "channels": results,
            "timestamp": event.timestamp,
        }

    async def _send_n8n_webhook(self, event: HoldEvent) -> dict[str, Any]:
        if not self.n8n_webhook_url:
            return {"success": False, "error": "N8N_WEBHOOK_URL not configured"}

        payload = {
            "event": "888_HOLD",
            "session_id": event.session_id,
            "reason": event.reason.value,
            "issue_label": event.issue_label,
            "actor_id": event.actor_id,
            "authority_level": event.authority_level,
            "tool": event.tool,
            "stage": event.stage,
            "context": event.context,
            "telemetry": event.telemetry,
            "timestamp": event.timestamp,
            "sovereign_action_required": True,
        }

        async with httpx.AsyncClient(timeout=self.notification_timeout) as client:
            response = await client.post(self.n8n_webhook_url, json=payload)
            return {"success": response.status_code == 200, "status_code": response.status_code}

    async def _send_telegram(self, event: HoldEvent) -> dict[str, Any]:
        if not self.telegram_bot_token or not self.telegram_chat_id:
            return {"success": False, "error": "Telegram credentials not configured"}

        message = self._format_telegram_message(event)
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"

        async with httpx.AsyncClient(timeout=self.notification_timeout) as client:
            response = await client.post(
                url,
                json={
                    "chat_id": self.telegram_chat_id,
                    "text": message,
                    "parse_mode": "HTML",
                },
            )
            return {"success": response.status_code == 200, "status_code": response.status_code}

    async def _send_apex_dashboard(self, event: HoldEvent) -> dict[str, Any]:
        if not self.apex_dashboard_url:
            return {"success": False, "error": "APEX_DASHBOARD_URL not configured"}

        payload = {
            "type": "hold_notification",
            "session_id": event.session_id,
            "reason": event.reason.value,
            "issue_label": event.issue_label,
            "actor_id": event.actor_id,
            "context": event.context,
            "telemetry": event.telemetry,
            "requires_sovereign_action": True,
        }

        async with httpx.AsyncClient(timeout=self.notification_timeout) as client:
            response = await client.post(
                f"{self.apex_dashboard_url}/api/hold",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            return {"success": response.status_code == 200, "status_code": response.status_code}

    def _log_hold(self, event: HoldEvent) -> dict[str, Any]:
        logger.warning(
            f"888_HOLD: session={event.session_id} reason={event.reason.value} "
            f"issue={event.issue_label} actor={event.actor_id} tool={event.tool}"
        )
        return {"success": True, "logged": True}

    def _format_telegram_message(self, event: HoldEvent) -> str:
        return f"""⚠️ <b>888_HOLD — Sovereign Action Required</b>

<b>Session:</b> <code>{event.session_id[:16]}...</code>
<b>Reason:</b> {event.reason.value}
<b>Issue:</b> {event.issue_label}
<b>Actor:</b> {event.actor_id} ({event.authority_level})
<b>Tool:</b> {event.tool}
<b>Stage:</b> {event.stage}

<b>Context:</b>
<pre>{json.dumps(event.context, indent=2)[:500]}</pre>

<b>Action Required:</b> Review and approve/reject via APEX Dashboard.

<em>DITEMPA, BUKAN DIBERI</em>"""


apex_notification_bridge = APEXNotificationBridge()


async def emit_sovereign_hold(
    session_id: str,
    reason: HoldReason | str,
    issue_label: str,
    context: dict[str, Any],
    actor_id: str = "anonymous",
    authority_level: str = "anonymous",
    tool: str = "unknown",
    stage: str = "888_JUDGE",
    telemetry: dict[str, Any] | None = None,
    channels: list[NotificationChannel] | None = None,
) -> dict[str, Any]:
    if isinstance(reason, str):
        reason = HoldReason(reason)

    event = HoldEvent(
        session_id=session_id,
        reason=reason,
        issue_label=issue_label,
        context=context,
        actor_id=actor_id,
        authority_level=authority_level,
        tool=tool,
        stage=stage,
        telemetry=telemetry or {},
    )

    return await apex_notification_bridge.emit_sovereign_hold(event, channels)

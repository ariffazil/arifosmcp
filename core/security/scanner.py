"""
core/security/scanner.py — F12 Defense: Injection Scanner

Runs at metabolic stage 000 (INIT) before any other logic.
Detects prompt injection, role-play jailbreaks, CRLF injection,
and adversarial suffix patterns in incoming tool payloads.

If threat_detected=True → VOID immediately (F12 Wall, hard stop).
No recovery path from F12 violation. Session must be re-anchored.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# THREAT PATTERNS
# ─────────────────────────────────────────────────────────────────────────────
# Pattern tuples: (name, compiled_regex)
_INJECTION_PATTERNS: list[tuple[str, re.Pattern]] = [
    # Role-play / persona hijack
    ("ROLE_PLAY_JAILBREAK",    re.compile(r"ignore\s+(all\s+)?previous\s+instructions?", re.I)),
    ("ROLE_PLAY_JAILBREAK",    re.compile(r"you\s+are\s+now\s+(a|an|the)\s+\w+\s*(ai|bot|assistant)", re.I)),
    ("DAN_JAILBREAK",          re.compile(r"\bDAN\b|\bdo\s+anything\s+now\b", re.I)),
    ("SYSTEM_PROMPT_OVERRIDE", re.compile(r"<system>|<\|system\|>|\[SYSTEM\]", re.I)),
    # CRLF / header injection
    ("CRLF_INJECTION",         re.compile(r"\r\n|\n\r|%0d%0a|%0a%0d", re.I)),
    # Prompt suffix / payload injection
    ("PROMPT_SUFFIX",          re.compile(r"###\s*instructions?|```\s*system|<</SYS>>|<<SYS>>", re.I)),
    ("INSTRUCTION_OVERRIDE",   re.compile(r"your\s+(new\s+)?instructions?\s+(are|is)\s*:", re.I)),
    # Tool/function call injection
    ("TOOL_CALL_INJECTION",    re.compile(r"<tool_call>|<function_calls>|{\"name\":\s*\"[^\"]+\"\s*,\s*\"arguments\"", re.I)),
    # Base64 payload obfuscation
    ("BASE64_OBFUSCATION",     re.compile(r"(?:[A-Za-z0-9+/]{40,}={0,2})", re.I)),
    # Null byte injection
    ("NULL_BYTE",              re.compile(r"\x00|\0")),
    # Unicode direction override (RTLO attack)
    ("UNICODE_RTLO",           re.compile(r"[\u202e\u200f\u200b]")),
]

# Allowlisted patterns that look suspicious but are legitimate in arifOS context
_ALLOWLIST_PATTERNS: list[re.Pattern] = [
    re.compile(r"<untrusted_external_data"),   # F12 taint wrapper is legit
    re.compile(r"actor_id|session_id|governance_token"),  # Internal fields
]


# ─────────────────────────────────────────────────────────────────────────────
# RESULT
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class ScanResult:
    threat_detected: bool = False
    pattern: str = ""
    matched_text: str = ""
    threats_found: list[dict] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return not self.threat_detected


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────
def scan_for_injection(payload: str, strict: bool = False) -> ScanResult:
    """
    Scan payload string for prompt injection and adversarial patterns.

    Args:
        payload: The raw input string to scan (actor_id, session_meta, action dict).
        strict:  If True, base64 obfuscation is always flagged regardless of length.

    Returns:
        ScanResult with threat_detected=True if any pattern matches.
        On threat: VOID must be issued immediately (F12 Wall).
    """
    if not payload or not isinstance(payload, str):
        return ScanResult(threat_detected=False)

    # Check allowlist first — skip scanning for known-safe patterns
    for allow_pat in _ALLOWLIST_PATTERNS:
        if allow_pat.search(payload):
            return ScanResult(threat_detected=False)

    threats = []
    first_threat_pattern = ""
    first_threat_text = ""

    for name, pattern in _INJECTION_PATTERNS:
        # Skip base64 check in non-strict mode for short payloads
        if name == "BASE64_OBFUSCATION" and not strict and len(payload) < 200:
            continue

        match = pattern.search(payload)
        if match:
            matched = match.group(0)[:80]  # truncate for logging
            threats.append({"pattern": name, "matched": matched})
            if not first_threat_pattern:
                first_threat_pattern = name
                first_threat_text = matched

    if threats:
        logger.warning(
            "F12 INJECTION DETECTED: %d pattern(s) in payload. First: %s",
            len(threats),
            first_threat_pattern,
        )
        return ScanResult(
            threat_detected=True,
            pattern=first_threat_pattern,
            matched_text=first_threat_text,
            threats_found=threats,
        )

    return ScanResult(threat_detected=False)


def scan_dict(data: dict, strict: bool = False) -> ScanResult:
    """
    Recursively scan all string values in a dict for injection patterns.
    Used for scanning action payloads and session_meta objects.
    """
    combined = _flatten_dict_strings(data)
    return scan_for_injection(combined, strict=strict)


def _flatten_dict_strings(data: object, depth: int = 0) -> str:
    """Flatten nested dict/list values into a single scannable string."""
    if depth > 8:
        return ""
    if isinstance(data, str):
        return data + " "
    if isinstance(data, dict):
        return " ".join(_flatten_dict_strings(v, depth + 1) for v in data.values())
    if isinstance(data, (list, tuple)):
        return " ".join(_flatten_dict_strings(item, depth + 1) for item in data)
    return ""


__all__ = [
    "ScanResult",
    "scan_for_injection",
    "scan_dict",
]

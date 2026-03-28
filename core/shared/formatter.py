"""
core/shared/formatter.py — Output Formatting & Schema Enforcement

Provides:
- User-friendly vs debug output modes
- Schema templates for structured responses
- Automatic formatting based on query type

Marginal effort, big UX win.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class OutputMode(str, Enum):
    """Output formatting modes."""

    USER = "user"  # Human-friendly, concise
    DEBUG = "debug"  # Full technical details
    SCHEMA = "schema"  # Structured, validated output


@dataclass
class SchemaTemplate:
    """Template for structured output."""

    name: str
    required_fields: list[str]
    optional_fields: list[str]
    format_example: dict[str, Any]
    description: str


# ═════════════════════════════════════════════════════════════════════════════
# SCHEMA TEMPLATES (Reduces "schema entropy")
# ═════════════════════════════════════════════════════════════════════════════

SCHEMA_TEMPLATES: dict[str, SchemaTemplate] = {
    "analysis": SchemaTemplate(
        name="analysis",
        required_fields=["summary", "key_points", "confidence"],
        optional_fields=["citations", "uncertainties", "recommendations"],
        format_example={
            "summary": "Brief synthesis of findings",
            "key_points": ["Point 1", "Point 2"],
            "confidence": 0.95,
            "uncertainties": ["Edge case not fully tested"],
        },
        description="General analysis with structured reasoning",
    ),
    "comparison": SchemaTemplate(
        name="comparison",
        required_fields=["options", "criteria", "recommendation"],
        optional_fields=["tradeoffs", "context_factors"],
        format_example={
            "options": ["Option A", "Option B"],
            "criteria": [{"name": "cost", "weight": 0.3}],
            "tradeoffs": {"Option A": "Lower cost, higher risk"},
            "recommendation": "Option A with caveats",
        },
        description="Compare alternatives with weighted criteria",
    ),
    "code_review": SchemaTemplate(
        name="code_review",
        required_fields=["issues", "severity", "suggestions"],
        optional_fields=["positive_patterns", "test_coverage"],
        format_example={
            "issues": [{"line": 42, "type": "security", "description": "SQL injection risk"}],
            "severity": "high",
            "suggestions": ["Use parameterized queries"],
            "positive_patterns": ["Good error handling"],
        },
        description="Code review with structured feedback",
    ),
    "decision": SchemaTemplate(
        name="decision",
        required_fields=["verdict", "reasoning", "stakeholders"],
        optional_fields=["risks", "reversibility", "timeline"],
        format_example={
            "verdict": "PROCEED_WITH_CAUTION",
            "reasoning": "Benefits outweigh risks with monitoring",
            "stakeholders": [{"name": "users", "impact": "positive"}],
            "risks": ["Implementation complexity"],
            "reversibility": "Medium (can rollback within 24h)",
        },
        description="Structured decision with full rationale",
    ),
    "eureka_result": SchemaTemplate(
        name="eureka_result",
        required_fields=["insight", "novelty_score", "coherence_score", "confidence"],
        optional_fields=["supporting_evidence", "alternative_explanations", "testable_predictions"],
        format_example={
            "insight": "The core discovery or synthesis",
            "novelty_score": 0.85,
            "coherence_score": 0.92,
            "confidence": 0.78,
            "supporting_evidence": ["Data point 1", "Pattern match"],
            "alternative_explanations": ["Other possible interpretation"],
            "testable_predictions": ["If true, then X should happen"],
        },
        description="Eureka insight with quality metrics",
    ),
}


# ═════════════════════════════════════════════════════════════════════════════
# FORMATTER CLASS
# ═════════════════════════════════════════════════════════════════════════════


class OutputFormatter:
    """
    Format pipeline outputs for different audiences.

    Usage:
        formatter = OutputFormatter(mode=OutputMode.USER)
        user_output = formatter.format(result, query_type="analysis")
    """

    def __init__(self, mode: OutputMode = OutputMode.USER):
        self.mode = mode

    def format(
        self,
        result: dict[str, Any],
        query_type: str = "general",
        template_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Format result based on mode and query type.

        Args:
            result: Raw pipeline result
            query_type: Type of query (determines template)
            template_name: Specific schema template to use

        Returns:
            Formatted output appropriate for the mode
        """
        if self.mode == OutputMode.USER:
            return self._format_user(result, query_type)
        elif self.mode == OutputMode.DEBUG:
            return self._format_debug(result)
        elif self.mode == OutputMode.SCHEMA:
            return self._format_schema(result, template_name or query_type)
        else:
            return result

    def _format_user(self, result: dict[str, Any], query_type: str) -> dict[str, Any]:
        """Format for human consumption—concise, readable."""
        formatted = {
            "answer": self._extract_answer(result),
            "verdict": result.get("verdict", "UNKNOWN"),
            "confidence": self._extract_confidence(result),
        }

        # Add principles applied (from 9 principles)
        principles = self._extract_principles(result)
        if principles:
            formatted["principles_applied"] = principles

        # Add brief rationale if verdict isn't SEAL
        if result.get("verdict") not in ["SEAL", None]:
            formatted["note"] = self._extract_rationale(result)

        # Add seal_id for audit trail
        if "seal" in result and result["seal"]:
            seal = result["seal"]
            if hasattr(seal, "seal_id"):
                formatted["audit_id"] = seal.seal_id[:16] + "..."
            elif isinstance(seal, dict):
                formatted["audit_id"] = seal.get("seal_id", "")[:16] + "..."

        return formatted

    def _format_debug(self, result: dict[str, Any]) -> dict[str, Any]:
        """Format for debugging—full technical details."""
        # Return everything, but add human-readable labels
        debug_output = {
            "raw_result": result,
            "summary": {
                "verdict": result.get("verdict"),
                "query_type": result.get("query_type"),
                "f2_threshold": result.get("f2_threshold"),
                "floors_failed": result.get("floors_failed", []),
                "processing_time_ms": result.get("processing_time_ms"),
            },
            "stage_outputs": {},
        }

        # Extract stage-specific outputs with mottos
        if "agi" in result:
            agi = result["agi"]
            debug_output["stage_outputs"]["agi"] = {
                "motto_111": agi.get("motto_111"),
                "motto_222": agi.get("motto_222"),
                "motto_333": agi.get("motto_333"),
            }

        if "asi" in result:
            asi = result["asi"]
            debug_output["stage_outputs"]["asi"] = {
                "motto_555": asi.get("motto_555"),
                "motto_666": asi.get("motto_666"),
            }

        if "apex" in result:
            apex = result["apex"]
            debug_output["stage_outputs"]["apex"] = {
                "motto_444": apex.get("motto_444"),
                "motto_777": apex.get("motto_777"),
                "motto_888": apex.get("motto_888"),
            }

        return debug_output

    def _format_schema(self, result: dict[str, Any], template_name: str) -> dict[str, Any]:
        """Format according to schema template."""
        template = SCHEMA_TEMPLATES.get(template_name)
        if not template:
            # Fall back to user mode if unknown template
            return self._format_user(result, template_name)

        # Extract and validate required fields
        structured = {"_schema": template.name}

        for field in template.required_fields:
            value = self._extract_field(result, field)
            structured[field] = value if value is not None else ""

        for field in template.optional_fields:
            value = self._extract_field(result, field)
            if value is not None:
                structured[field] = value

        # Add metadata
        structured["_metadata"] = {
            "verdict": result.get("verdict"),
            "confidence": self._extract_confidence(result),
            "template": template.name,
        }

        return structured

    # ═════════════════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═════════════════════════════════════════════════════════════════════════

    def _extract_answer(self, result: dict[str, Any]) -> str:
        """Extract the main answer text."""
        # Try various possible locations
        if "answer" in result:
            return result["answer"]
        if "response" in result:
            return result["response"]

        # Try to extract from AGI tensor
        if "agi" in result and isinstance(result["agi"], dict):
            agi = result["agi"]
            if "tensor" in agi and hasattr(agi["tensor"], "thought_chain"):
                thoughts = agi["tensor"].thought_chain
                if thoughts:
                    return (
                        thoughts[-1].thought
                        if hasattr(thoughts[-1], "thought")
                        else str(thoughts[-1])
                    )

        # Try apex output
        if "apex" in result and isinstance(result["apex"], dict):
            apex = result["apex"]
            if "judge" in apex and isinstance(apex["judge"], dict):
                return apex["judge"].get("justification", "No answer generated")

        return "No answer available"

    def _extract_confidence(self, result: dict[str, Any]) -> float:
        """Extract confidence score."""
        # Try W_3 first
        if "W_3" in result:
            return result["W_3"]
        if "apex" in result and isinstance(result["apex"], dict):
            return result["apex"].get("W_3", 0.5)
        # Try truth score
        if "f2_threshold" in result:
            return result["f2_threshold"]
        return 0.5

    def _extract_principles(self, result: dict[str, Any]) -> list[str]:
        """Extract the 9 principles that were applied."""
        principles = []

        # Map stage outputs to principles
        principle_map = {
            "motto_111": "Examined, not spoon-fed",
            "motto_222": "Explored, not restricted",
            "motto_333": "Clarified, not obscured",
            "motto_444": "Faced, not postponed",
            "motto_555": "Calmed, not inflamed",
            "motto_666": "Protected, not neglected",
            "motto_777": "Worked for, not merely hoped",
            "motto_888": "Aware, not overconfident",
        }

        # Check AGI outputs
        if "agi" in result and isinstance(result["agi"], dict):
            for key, principle in principle_map.items():
                if key in result["agi"]:
                    principles.append(principle)

        # Check ASI outputs
        if "asi" in result and isinstance(result["asi"], dict):
            for key in ["motto_555", "motto_666"]:
                if key in result["asi"]:
                    principles.append(principle_map[key])

        # Check APEX outputs
        if "apex" in result and isinstance(result["apex"], dict):
            for key in ["motto_444", "motto_777", "motto_888"]:
                if key in result["apex"]:
                    principles.append(principle_map[key])

        return principles if principles else ["Earned, not given"]

    def _extract_rationale(self, result: dict[str, Any]) -> str:
        """Extract brief rationale for non-SEAL verdicts."""
        if "remediation" in result and result["remediation"]:
            return result["remediation"]

        if "apex" in result and isinstance(result["apex"], dict):
            apex = result["apex"]
            if "judge" in apex and isinstance(apex["judge"], dict):
                return apex["judge"].get("justification", "Check details above")

        floors = result.get("floors_failed", [])
        if floors:
            return f"Needs attention: {', '.join(floors)}"

        return "Review output for details"

    def _extract_field(self, result: dict[str, Any], field: str) -> Any:
        """Extract a specific field from nested result."""
        # Direct access
        if field in result:
            return result[field]

        # Nested access
        for key in ["agi", "asi", "apex", "judge", "seal"]:
            if key in result and isinstance(result[key], dict):
                if field in result[key]:
                    return result[key][field]

        return None


# ═════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════


def format_for_user(result: dict[str, Any], query_type: str = "general") -> dict[str, Any]:
    """Quick format for user mode."""
    formatter = OutputFormatter(mode=OutputMode.USER)
    return formatter.format(result, query_type)


def format_for_debug(result: dict[str, Any]) -> dict[str, Any]:
    """Quick format for debug mode."""
    formatter = OutputFormatter(mode=OutputMode.DEBUG)
    return formatter.format(result)


def format_with_schema(result: dict[str, Any], template_name: str) -> dict[str, Any]:
    """Quick format with schema template."""
    formatter = OutputFormatter(mode=OutputMode.SCHEMA)
    return formatter.format(result, template_name=template_name)


def get_template(name: str) -> SchemaTemplate | None:
    """Get a schema template by name."""
    return SCHEMA_TEMPLATES.get(name)


def list_templates() -> list[str]:
    """List available schema templates."""
    return list(SCHEMA_TEMPLATES.keys())


__all__ = [
    "OutputMode",
    "OutputFormatter",
    "SchemaTemplate",
    "SCHEMA_TEMPLATES",
    "format_for_user",
    "format_for_debug",
    "format_with_schema",
    "get_template",
    "list_templates",
]

"""
arifOS × Marvin AI Bridge

Integrates Marvin's AI capabilities with arifOS constitutional governance.
Marvin provides structured AI output; arifOS provides safety validation.
"""

from __future__ import annotations

import logging
from typing import Any

try:
    import marvin
    from marvin import Agent, Task
    MARVIN_AVAILABLE = True
except ImportError:
    MARVIN_AVAILABLE = False
    marvin = None
    Agent = None
    Task = None

from arifosmcp.runtime.megaTools import asi_heart, apex_soul
from arifosmcp.runtime.models import Verdict

logger = logging.getLogger(__name__)


class ArifOSAgent(Agent):
    """
    Marvin Agent with arifOS constitutional governance.
    
    Extends Marvin's Agent to include:
    - ASI Heart safety critique before execution
    - APEX Soul validation of outputs
    - Automatic vault logging
    """
    
    def __init__(self, *args, enable_governance: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.enable_governance = enable_governance
        
    async def run(self, task: Task) -> Any:
        """Run task with arifOS governance."""
        
        if not self.enable_governance or not MARVIN_AVAILABLE:
            return await super().run(task)
        
        # Pre-execution safety check
        safety_result = await asi_heart(
            mode="critique",
            payload={
                "task": task.instructions,
                "agent": self.name,
                "context": task.context
            }
        )
        
        if safety_result.verdict == Verdict.VOID:
            raise RuntimeError(
                f"Task blocked by constitutional safety: "
                f"{safety_result.payload.get('reason', 'Unknown')}"
            )
        
        # Execute Marvin task
        result = await super().run(task)
        
        # Post-execution validation
        validation = await apex_soul(
            mode="validate",
            payload={
                "input": task.instructions,
                "output": result,
                "agent": self.name
            }
        )
        
        if validation.verdict == Verdict.VOID:
            logger.warning(f"Output validation failed: {validation.payload}")
        
        return result


def arifos_agent(
    name: str,
    instructions: str,
    model: str = "openai:gpt-4",
    enable_governance: bool = True,
    **kwargs
) -> Agent:
    """
    Create a Marvin Agent with arifOS governance.
    
    Args:
        name: Agent name
        instructions: System instructions
        model: Model identifier (pydantic-ai format)
        enable_governance: Whether to enable arifOS checks
        **kwargs: Additional Agent kwargs
        
    Returns:
        Configured Agent
        
    Example:
        writer = arifos_agent(
            name="Technical Writer",
            instructions="Write clear technical documentation",
            enable_governance=True
        )
        
        result = writer.run("Write about Python async")
    """
    if not MARVIN_AVAILABLE:
        raise RuntimeError("Marvin not installed. Run: pip install marvin")
    
    return ArifOSAgent(
        name=name,
        instructions=instructions,
        enable_governance=enable_governance,
        **kwargs
    )


async def governed_ai_task(
    instructions: str,
    result_type: type | None = None,
    context: dict | None = None,
    agent: Agent | None = None,
    enable_critique: bool = True
) -> Any:
    """
    Execute an AI task with full arifOS governance.
    
    Combines Marvin's marvin.run() with arifOS safety checks.
    
    Args:
        instructions: Task description
        result_type: Expected result type
        context: Task context
        agent: Optional specific agent
        enable_critique: Whether to run ASI critique
        
    Returns:
        Task result
        
    Example:
        result = await governed_ai_task(
            "Summarize constitutional AI principles",
            result_type=dict
        )
    """
    if not MARVIN_AVAILABLE:
        raise RuntimeError("Marvin not installed")
    
    # Pre-critique
    if enable_critique:
        critique = await asi_heart(
            mode="critique",
            payload={
                "instructions": instructions,
                "context": context or {}
            }
        )
        
        if critique.verdict == Verdict.VOID:
            return {
                "error": "Task blocked by constitutional safety",
                "reason": critique.payload.get("reason"),
                "alternatives": critique.payload.get("alternatives", [])
            }
    
    # Execute with Marvin
    result = marvin.run(
        instructions,
        result_type=result_type,
        context=context or {},
        agent=agent
    )
    
    # Post-validation
    if enable_critique:
        validation = await apex_soul(
            mode="validate",
            payload={
                "input": instructions,
                "output": result
            }
        )
        
        if validation.verdict == Verdict.VOID:
            logger.warning(f"Output validation concerns: {validation.payload}")
    
    return result


# Structured data extraction with governance
async def governed_extract(
    text: str,
    target_type: type,
    instructions: str = "",
    enable_critique: bool = True
) -> Any:
    """
    Extract structured data with arifOS validation.
    
    Wraps marvin.extract() with safety checks for PII/sensitive data.
    
    Args:
        text: Source text
        target_type: Type to extract
        instructions: Additional instructions
        enable_critique: Enable safety checks
        
    Returns:
        Extracted data
    """
    if not MARVIN_AVAILABLE:
        raise RuntimeError("Marvin not installed")
    
    # Check for sensitive data patterns
    if enable_critique:
        critique = await asi_heart(
            mode="critique",
            payload={
                "operation": "extract",
                "text_sample": text[:500],  # First 500 chars
                "target_type": str(target_type)
            }
        )
        
        if critique.payload.get('contains_pii'):
            logger.warning("Potential PII detected in extraction")
            
        if critique.verdict == Verdict.VOID:
            raise PermissionError("Extraction blocked: sensitive data detected")
    
    # Perform extraction
    return marvin.extract(text, target_type, instructions=instructions)


# Classification with governance
async def governed_classify(
    text: str,
    labels: list[str],
    enable_critique: bool = True
) -> str:
    """
    Classify text with arifOS validation.
    
    Args:
        text: Text to classify
        labels: Allowed labels
        enable_critique: Enable safety checks
        
    Returns:
        Classification label
    """
    if not MARVIN_AVAILABLE:
        raise RuntimeError("Marvin not installed")
    
    # Validate classification scope
    if enable_critique:
        critique = await asi_heart(
            mode="critique",
            payload={
                "operation": "classify",
                "text_sample": text[:200],
                "labels": labels
            }
        )
        
        if critique.verdict == Verdict.VOID:
            raise PermissionError("Classification blocked")
    
    return marvin.classify(text, labels)
